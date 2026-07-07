# M17 React 性能模式

> 定位：React / Next.js 应用专属性能规则，按影响优先级（CRITICAL→LOW）分类。聚焦数据流、渲染、包体积与服务端/客户端协作的 React 专项优化。边界：React/Next.js 基础架构见 M07，通用 Web 性能（Core Web Vitals、动画性能、资源优化）见 M14。

---

## 1. 何时进入本模块

在以下场景进入 M17：

- 用户明确使用 React / Next.js，且问题集中在「性能」而非「怎么用框架」。
- 需要优化组件重渲染、数据瀑布、Suspense 边界、Server/Client 数据获取。
- 需要削减 React 应用包体积、优化动态导入、避免 barrel imports。
- 需要判断 React.cache / `use` / `startTransition` / `useDeferredValue` 的适用场景。

若任务涉及框架选型、组件目录、RSC/Server Actions 基础用法 → 返回 M07。若任务聚焦 LCP/INP/CLS、图片/字体/动画性能 → 返回 M14。M17 只回答「React 专项性能模式」。

---

## 2. 优先级总览

| 优先级 | 关注领域 | 典型收益 |
| --- | --- | --- |
| CRITICAL | async waterfall、bundle size | 显著缩短 TTI/FCP、减少主包体积 |
| HIGH | server-side 数据与缓存 | 降低 TTFB、减少重复 I/O |
| MEDIUM-HIGH | client-side 获取与去重 | 减少冗余请求、避免内存泄漏 |
| MEDIUM | re-render、rendering 效率 | 提升交互响应、降低帧开销 |
| LOW-MEDIUM | JS 微优化 | 小幅度减少运行耗时 |
| LOW | advanced patterns | 特定场景使用，不优先投入 |

---

## 3. CRITICAL

### 3.1 消除 async waterfall

串行 `await` 是 React/Next.js 应用最常见的性能陷阱。独立数据必须并行获取；依赖数据才串行。

#### 错误：串行 await
```tsx
export default async function Page() {
  const user = await getUser();      // 阻塞
  const posts = await getPosts(user.id); // 阻塞
  const stats = await getStats();    // 阻塞
  return <Dashboard user={user} posts={posts} stats={stats} />;
}
```

#### 正确：独立 Promise.all
```tsx
export default async function Page() {
  const [user, stats] = await Promise.all([getUser(), getStats()]);
  const posts = await getPosts(user.id); // 依赖 user
  return <Dashboard user={user} posts={posts} stats={stats} />;
}
```

#### early promise / late await
在组件顶层尽早创建 promise，到真正需要结果的地方再 `await`，让 I/O 与渲染重叠。

```tsx
export default async function Page() {
  const userPromise = getUser();
  const statsPromise = getStats();

  return (
    <>
      <Suspense fallback={<UserSkeleton />}>
        <UserCard promise={userPromise} />
      </Suspense>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsCard promise={statsPromise} />
      </Suspense>
    </>
  );
}

async function UserCard({ promise }: { promise: Promise<User> }) {
  const user = await promise;
  return <div>{user.name}</div>;
}
```

#### better-all：请求合并
如果多个独立请求总是同时出现，优先合并为单个 API/数据库查询，减少往返。

#### Suspense boundaries
每个可能阻塞的异步区域都必须包裹独立的 `Suspense`，避免一个慢请求拖慢整个页面。

```tsx
<Suspense fallback={<ProductListSkeleton />}>
  <ProductList />
</Suspense>
<Suspense fallback={<ReviewSkeleton />}>
  <Reviews />
</Suspense>
```

### 3.2 Bundle size

#### 避免 barrel imports
barrel 文件会阻止 tree-shaking，把整个包的副作用全部引入。

```tsx
// 错误
import { Button } from "@/components/ui"; // 拉入全部 UI

// 正确
import { Button } from "@/components/ui/button";
```

#### next/dynamic 懒加载
对首屏外的重组件、模态框、图表、富文本编辑器使用动态导入。

```tsx
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("./HeavyChart"), {
  ssr: false,
  loading: () => <ChartSkeleton />,
});
```

#### defer 第三方库
非首屏必需的第三方库（如地图、视频播放器、分析）延迟到交互后再加载。

```tsx
const loadMap = () => import("@some-map-lib");

function MapButton() {
  return <button onClick={() => loadMap().then(initMap)}>显示地图</button>;
}
```

#### conditional import
根据环境或用户能力按需导入 polyfill 或重型库。

```tsx
if (typeof Intl === "undefined") {
  await import("intl-polyfill");
}
```

#### preload on intent
在 hover / focus / 滚动接近时预加载即将进入视口的组件或数据。

```tsx
function ProductCard({ id }: { id: string }) {
  const router = useRouter();
  return (
    <div
      onMouseEnter={() => router.prefetch(`/product/${id}`)}
    >
      ...
    </div>
  );
}
```

---

## 4. HIGH

### 4.1 React.cache
在 Next.js App Router 同一次请求中，多个组件需要相同数据时，使用 `React.cache` 避免重复查询。

```tsx
import { cache } from "react";

const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } });
});

// Page 和 Sidebar 同时调用，只执行一次数据库查询
export default async function Page({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);
  return (
    <>
      <Header user={user} />
      <Sidebar userId={params.id} />
    </>
  );
}

async function Sidebar({ userId }: { userId: string }) {
  const user = await getUser(userId);
  return <nav>{user.name}</nav>;
}
```

### 4.2 LRU 与请求级缓存
对昂贵的计算或外部 API 使用 LRU 缓存，但注意：React.cache 是请求级，不能跨请求。跨请求缓存使用 `unstable_cache` 或外部缓存（Redis）。

### 4.3 hoist static I/O
不随请求变化的数据（配置、分类、菜单）在模块顶层或构建时获取，不要在每次 render 中重复请求。

```tsx
// 正确：构建时读取一次
const categories = await getCategories();

export default async function Page() {
  return <CategoryNav categories={categories} />;
}
```

### 4.4 minimize serialization
Server Component 传给 Client Component 的 props 必须是 JSON 可序列化的。避免传递大型对象、函数、类实例，减少序列化开销和泄漏风险。

```tsx
// 错误：传递 class 实例或函数
<ClientChart data={new ChartData(raw)} formatter={formatCurrency} />

// 正确：传递纯数据
<ClientChart data={raw} />
```

### 4.5 parallel fetching
Server Component 中所有独立 fetch 使用 `Promise.all`，见 3.1。

### 4.6 after()
Next.js 15+ 的 `unstable_after`（将稳定为 `after`）用于在响应返回后执行非阻塞任务（如日志、分析、缓存预热），不阻塞用户响应。

```tsx
import { after } from "next/server";

export default async function Page() {
  after(() => analytics.track("page_view", { path: "/" }));
  return <Home />;
}
```

---

## 5. MEDIUM-HIGH

### 5.1 SWR dedup
使用 SWR / TanStack Query 等库时，依赖其内置的请求去重、缓存、重新验证策略，避免多个组件重复发起相同请求。

```tsx
function useUser(id: string) {
  return useSWR(`/api/user/${id}`, fetcher);
}

// 多个组件调用 useUser('1') 只产生一个请求
```

### 5.2 dedupe event listeners
高频事件（scroll、resize、pointermove）在顶层统一监听，通过 Context 或 ref 分发给子组件，避免每个组件重复绑定。

```tsx
function useWindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });
  useEffect(() => {
    const handler = () => setSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);
  return size;
}
```

### 5.3 passive listeners
对 scroll、touch、wheel 等高频事件使用 `{ passive: true }`，避免阻塞主线程。

```tsx
document.addEventListener("scroll", handler, { passive: true });
```

### 5.4 localStorage schema versioning
缓存到 localStorage 的数据必须带 schema 版本号，避免旧数据格式导致异常或渲染错误。

```tsx
const STORAGE_KEY = "app-settings";
const SCHEMA_VERSION = 2;

function loadSettings() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return defaultSettings;
  const parsed = JSON.parse(raw);
  if (parsed.version !== SCHEMA_VERSION) return defaultSettings;
  return parsed.data;
}
```

---

## 6. MEDIUM

### 6.1 Re-render

#### defer reads
把读取 Context 或全局状态的逻辑下沉到真正使用它的子组件，避免父组件因无关变化重渲染。

```tsx
// 错误：父组件读取整个 context
function Parent() {
  const { theme, user } = useAppContext();
  return (
    <div className={theme}>
      <Header user={user} />
    </div>
  );
}

// 正确：只在需要处读取
function Header() {
  const user = useUserContext();
  return <div>{user.name}</div>;
}
```

#### memo 昂贵工作
对真正昂贵的子树使用 `React.memo` 或拆分为独立组件；不要为预防而包裹。

```tsx
const ExpensiveList = React.memo(function ExpensiveList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{heavyTransform(item)}</li>
      ))}
    </ul>
  );
});
```

#### primitive deps
`useEffect` / `useMemo` / `useCallback` 的依赖数组使用原始值，避免对象引用变化导致频繁触发。

```tsx
// 错误
useEffect(() => {}, [{ id }]);

// 正确
useEffect(() => {}, [id]);
```

#### derived state
派生状态不要放到 state 中，直接在 render 中计算。

```tsx
// 错误
const [fullName, setFullName] = useState(`${firstName} ${lastName}`);

// 正确
const fullName = `${firstName} ${lastName}`;
```

#### functional setState
新状态依赖旧状态时，使用函数式更新，避免闭包中的旧值。

```tsx
setCount((prev) => prev + 1);
```

#### lazy init
`useState` 初始值由昂贵计算得到时，使用 lazy initializer。

```tsx
const [state, setState] = useState(() => computeInitialState(props));
```

#### startTransition
对非紧急更新（如搜索结果过滤、大型列表排序）使用 `startTransition`，保持交互响应。

```tsx
import { startTransition } from "react";

function Search({ query, onQueryChange }: SearchProps) {
  const [inputValue, setInputValue] = useState(query);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    startTransition(() => {
      onQueryChange(value);
    });
  };

  return <input value={inputValue} onChange={handleChange} />;
}
```

#### useRef for transient
不触发渲染的瞬时状态（如拖拽位置、interval id）使用 `useRef`。

```tsx
const dragPosition = useRef({ x: 0, y: 0 });
```

#### no inline components
不要在 render 函数内部定义新组件，否则每次渲染都会创建新类型，React 无法复用状态。

```tsx
// 错误
function Parent() {
  const InlineChild = () => <div />;
  return <InlineChild />;
}

// 正确
function Child() {
  return <div />;
}
function Parent() {
  return <Child />;
}
```

### 6.2 Rendering

#### animate SVG wrapper
对 SVG 内部元素做动画时，优先对包裹的容器使用 `transform`，避免对大量 SVG 节点重排。

#### content-visibility
对首屏外的大型静态列表或卡片区域使用 `content-visibility: auto`，跳过离屏渲染。

```css
.offscreen-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}
```

#### hoist static JSX
不依赖 props/state 的静态 JSX 提升到组件外部或模块层级，避免每次渲染重新创建。

```tsx
const staticIcon = <Icon name="star" />;

function Rating({ value }: { value: number }) {
  return (
    <span>
      {staticIcon} {value}
    </span>
  );
}
```

#### hydration no flicker
避免在 hydration 前后渲染差异巨大的内容。条件渲染依赖客户端信息时，使用 `useEffect` 或 `useSyncExternalStore` 避免 hydration mismatch。

```tsx
function ClientOnly({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted ? children : null;
}
```

#### conditional render with ternary
条件渲染使用三元表达式，避免 `&&` 在值为 `0` / `""` 时意外渲染。

```tsx
// 错误
{items.length && <List items={items} />}

// 正确
{items.length > 0 ? <List items={items} /> : null}
```

#### useTransition for loading
对需要反馈的异步状态切换使用 `useTransition` 的 `isPending`。

```tsx
const [isPending, startTransition] = useTransition();

function handleTabChange(tab: string) {
  startTransition(() => setTab(tab));
}

return (
  <>
    {isPending && <Spinner />}
    <TabContent tab={tab} />
  </>
);
```

---

## 7. LOW-MEDIUM

### 7.1 batch DOM changes via class
通过切换 class 一次性改变多个样式，而不是逐个修改 style。

```tsx
// 错误
el.style.width = "100px";
el.style.height = "100px";
el.style.opacity = "0.5";

// 正确
el.classList.add("expanded");
```

### 7.2 index maps
频繁按 id 查找的数据先构建 Map，避免 `array.find` 的 O(n)。

```tsx
const userMap = new Map(users.map((u) => [u.id, u]));
const user = userMap.get(id);
```

### 7.3 cache calls
对稳定输入的纯函数结果做 memoization。

```tsx
const expensive = useMemo(() => compute(items), [items]);
```

### 7.4 toSorted / toReversed
需要保留原数组引用时使用 `toSorted` / `toReversed`，避免意外 mutation 导致依赖比较失效。

```tsx
const sorted = items.toSorted((a, b) => a.price - b.price);
```

### 7.5 early length check
数组操作前先做长度检查，避免空数组上的不必要计算或渲染。

```tsx
{items.length > 0 ? <List items={items} /> : <EmptyState />}
```

---

## 8. LOW

### 8.1 Advanced patterns
- **useDeferredValue**：对需要保持响应的输入，延迟更新其派生 UI，常与 memo 配合使用。
- **useMemo for children stability**：仅在子树极其昂贵且 props 稳定时，使用 `useMemo` 缓存 children。
- **React Server Components 作为默认**：让更多组件保留在服务端，减少客户端 JS 体积。
- **Server Actions 替代手动 API**：减少客户端序列化与网络往返。
- **渐进式 hydration / `React.lazy`**：非关键组件延迟 hydrate。

这些模式在基准性能优化完成后，针对特定瓶颈使用。不要在没有测量的情况下优先投入。

---

## 9. 与相邻模块的边界

| 内容 | 归属模块 |
| --- | --- |
| React 19 / Next.js / shadcn/ui 基础架构、栈选择、RSC/Server Actions 用法 | M07 组件与框架 |
| Core Web Vitals、图片/字体/动画性能、通用 Web 性能测量 | M14 性能优化 |
| React 专项性能模式：async waterfall、Suspense、React.cache、重渲染、bundle size | **M17** |
| CSS 动画设计、微交互时序 | M04 动效与交互 |
| 前端测试策略 | M12 应用测试 |

---

## 10. 快速检查清单

- [ ] 独立数据是否使用 `Promise.all` 并行获取？
- [ ] 依赖数据是否只在其前置结果之后才 `await`？
- [ ] 每个异步区域是否有独立的 `Suspense` 边界？
- [ ] 是否避免 barrel imports，直接导入具体模块？
- [ ] 重组件 / 第三方库是否使用 `next/dynamic` 或动态导入延迟加载？
- [ ] 同请求重复数据是否使用 `React.cache` 去重？
- [ ] 静态 I/O 是否提升到模块顶层或构建时？
- [ ] 传给 Client Component 的 props 是否是精简的可序列化数据？
- [ ] 客户端获取是否使用 SWR / TanStack Query 等去重缓存库？
- [ ] 高频事件是否去重并尽量使用 passive listener？
- [ ] `localStorage` 缓存是否带 schema 版本号？
- [ ] Context 读取是否下沉到真正消费的组件？
- [ ] 是否信任 React Compiler，不为预防而包裹 memo？
- [ ] `useEffect` / `useMemo` 依赖数组是否由原始值构成？
- [ ] 派生状态是否直接在 render 中计算而非存入 state？
- [ ] 昂贵非紧急更新是否使用 `startTransition`？
- [ ] 瞬时状态是否使用 `useRef`？
- [ ] 是否在 render 函数内部定义 inline 组件？
- [ ] 首屏外大型区域是否使用 `content-visibility: auto`？
- [ ] 条件渲染是否使用三元表达式而非 `&&`？
