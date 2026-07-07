# M16 UX 规则审计

## 何时调用本模块

当用户要求「审计」「走查」「检查 UI 是否符合最佳实践」「UX 规则审查」「界面质量检查」时调用本模块。典型触发词：

- `/audit-ux <路径>`
- 「检查这段代码的 UX 问题」
- 「UX 规则审计」「前端最佳实践检查」

适用时机：

1. 代码审查阶段：PR/MR 中对现有 UI 文件做轻量审计。
2. 交付前：确认新页面/组件没有常见 UX 违规。
3. 回归检查：重构 UI 后快速扫描是否破坏焦点、语义、状态等。
4. 设计稿落地后：验证实现是否还满足可访问、可交互、可扩展的要求。

### 无代码路径时的处理

若用户未提供文件路径、代码片段或可访问 URL，按以下顺序处理：
1. 停止并索要具体代码（文件路径或粘贴关键片段）。
2. 若用户无法提供代码，输出本模块的「快速检查清单」供用户自检，并说明拿到代码后可做 file:line 级审计。

> 边界说明
>
> - 可访问性整改流程与修复模式 → 见 [M13 可访问性修复](M13-可访问性修复.md)。
> - 动画设计、微交互时序、scroll-driven animations → 见 [M04 动效与交互](M04-动效与交互.md)。
> - 性能测量、Core Web Vitals、包体积 → 见 [M14 性能优化](M14-性能优化.md)。
>
> 本模块输出 file:line 级别的审计发现，并给出最小可执行建议；复杂修复、整改流程与性能调优分别指向 [M13 可访问性修复](M13-可访问性修复.md)、[M04 动效与交互](M04-动效与交互.md)、[M14 性能优化](M14-性能优化.md)。

---

## 审计输出格式

每项发现必须精确到文件与行号，便于直接定位：

```markdown
| 文件 | 行号 | 类别 | 问题 | 建议 | 优先级 | 后续模块 |
| ---- | ---- | ---- | ---- | ---- | ------ | -------- |
| components/Button.tsx | 42 | Focus States | 使用 `outline: none` 且无替代样式 | 改用 `:focus-visible` 显式定义焦点环 | P1 | M13 |
| pages/Login.tsx | 18 | Forms | `<input>` 无关联 `<label>` | 添加 `label for` 或隐式包裹 | P1 | M13 |
| components/Feed.tsx | 73 | Images | `<img>` 未设置 width/height | 设置尺寸或使用 aspect-ratio 占位 | P2 | M14 |
```

> 「后续模块」列标注该问题应由哪个模块负责整改：M13（可访问性修复）、M04（动效与交互）、M14（性能优化）等。

输出原则：

- 简短：问题与建议各一句话。
- 可操作：开发者在 5 分钟内知道改什么。
- 可验证：修改后能通过本模块的对应条目复核。
- 按优先级 P1/P2/P3 排序，P1 为阻塞性/合规性问题。

---

## 规则分类

### 1. Accessibility

聚焦语义与辅助技术，与 M13 的整改流程互补；本列表只保留最常见、最易在审计阶段定位的问题。

1. 页面有且仅有一个 `<main>`。
2. 标题层级连续（h1→h2→h3），不跳级。
3. 列表/表格使用原生 `<ul>` / `<ol>` / `<table>` 结构。
4. 图标按钮必须有 `aria-label` 或相邻可见文本。
5. 非装饰图片必须有 `alt`；装饰图片用 `alt=""`。
6. 链接文本脱离上下文后仍可理解目标。
7. 表单错误通过 `aria-describedby` 与控件关联。
8. 状态变化使用 `aria-live` 区域播报。
9. 不滥用 `role` 覆盖原生语义。

```html
<!-- 反例 -->
<div class="title">文章标题</div>
<button><svg>...</svg></button>

<!-- 正例 -->
<h1>文章标题</h1>
<button aria-label="关闭"><svg>...</svg></button>
```

### 2. Focus States

1. 所有可聚焦元素必须有可见焦点样式。
2. 使用 `:focus-visible` 而非 `:focus` 显示键盘焦点环。
3. 禁止全局 `outline: none` 而不提供替代样式。
4. 焦点样式应覆盖所有状态（hover/focus/active 同时存在时仍可见）。
5. 复杂组件（tablist、menu）使用 `:focus-within` 给出容器级反馈。
6. 焦点环颜色与背景对比度 ≥ 3:1。

```css
/* 反例 */
button:focus { outline: none; }

/* 正例 */
button:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

### 3. Forms

1. 每个输入框必须有关联 `<label>`。
2. 必填项同时用视觉标记和 `required` 属性声明。
3. 使用正确的 `type`（email/tel/url/search/date）和 `inputmode`。
4. 为字段组使用 `<fieldset>` + `<legend>`。
5. 为常见字段提供 `autocomplete` 值。
6. 不阻止用户粘贴密码/验证码等字段。

#### 3.1 Validation（表单验证）

1. 错误提示通过 `aria-invalid` + `aria-describedby` 与对应控件关联。
2. 表单提交后把焦点移到第一个错误字段或错误汇总。
3. 输入约束（格式、长度）在标签或提示中预先说明，不要等到报错才告知。
4. 错误文案使用主动语态并给出下一步动作（见 M15）。

```html
<!-- 反例 -->
<input type="text" placeholder="邮箱" />
<span class="error">格式错误</span>

<!-- 正例 -->
<label for="email">邮箱 <span aria-label="必填">*</span></label>
<input id="email" type="email" required autocomplete="email" aria-invalid="true" aria-describedby="email-error" />
<span id="email-error">请输入有效的邮箱地址</span>
```

### 4. Animation

聚焦「是否尊重运动偏好」与「动画属性是否安全」，不讨论动效设计本身（见 M04）。

1. 全局实现 `prefers-reduced-motion: reduce` 回退。
2. 关键信息不依赖动画呈现。
3. 交互反馈优先使用 `transition`，复杂 enter/exit 用 JS 动画库管理。
4. 优先使用 `transform` / `opacity` 实现动画；使用 `filter`、`clip-path`、`color` 等其他属性时，须评估性能影响并在 [M14 性能优化](M14-性能优化.md) 中验证。
5. `transition` 必须显式列出属性，避免 `all`。
6. 自动播放循环动画在离屏时暂停。

```css
/* 反例 */
.modal {
  transition: all 0.3s ease;
}

/* 正例 */
.modal {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
@media (prefers-reduced-motion: reduce) {
  .modal {
    transition: none;
  }
}
```

### 5. Content Handling

1. 用户生成内容（UGC）渲染前做消毒，不直接注入 `innerHTML`。
2. 文本溢出时使用 `overflow-wrap: break-word` 或 `word-break`。
3. 长内容使用 `line-clamp` 或截断提示，而不是固定高度裁剪。
4. 空状态提供明确文案和下一步操作。
5. 404/错误页提供返回首页或可恢复路径。
6. 长表单分步骤展示，并提供进度指示。

```html
<!-- 反例 -->
<div class="post" [innerHTML]="rawContent"></div>

<!-- 正例 -->
<div class="post">{{ sanitizedContent }}</div>
```

### 6. Images

1. 图片设置 `width` / `height` 或 `aspect-ratio` 防止 CLS。
2. 首屏关键图片使用 `fetchpriority="high"`。
3. 非首屏图片使用 `loading="lazy"`。
4. 大图使用 `decoding="async"`。
5. 响应式图片使用 `srcset` + `sizes`。
6. 图标使用 SVG 或字体图标，避免低分辨率位图。

```html
<!-- 反例 -->
<img src="hero.jpg" alt="" />

<!-- 正例 -->
<img src="hero.jpg" width="1200" height="600" alt="产品截图" fetchpriority="high" decoding="async" />
```

### 7. Performance

聚焦代码层面可静态发现的性能风险，具体测量与优化见 M14。

1. 长列表/大数据表格使用虚拟化。
2. 延迟加载非首屏重组件（dynamic import / React.lazy）。
3. 对关键资源使用 `preconnect` / `preload` / `prefetch`。
4. 避免在渲染过程中读取布局属性（`offsetHeight`、`getBoundingClientRect`）。
5. 避免在 `requestAnimationFrame` 中读写布局属性交替。
6. 事件处理做防抖/节流（scroll、resize、input）。
7. 第三方脚本延迟加载或使用 Partytown。

```js
// 反例
function handleScroll() {
  const h = document.body.offsetHeight;
  list.style.height = h + 'px';
}

// 正例
const debounced = debounce((entries) => {
  // 批量处理
}, 100);
```

### 8. Navigation & State

1. URL 应反映页面状态，便于分享和深链。
2. 使用 `<a href>` 做页面跳转，`<button>` 做同一页行为。
3. 破坏性行为（删除、重置）需要确认或支持撤销。
4. 当前导航项通过 `aria-current="page"` 标记。
5. 页面返回时保留合理的滚动位置或状态。
6. 面包屑使用语义结构并标记当前位置。

```html
<!-- 反例 -->
<div class="nav-item" onclick="goTo('/settings')">设置</div>

<!-- 正例 -->
<a href="/settings" class="nav-item" aria-current="page">设置</a>
```

### 9. Touch & Interaction

1. 可点击目标最小尺寸 ≥ 44×44 CSS px（推荐），至少 ≥ 24×24 CSS px（最低）。
2. 避免误触：相邻可点击元素间距 ≥ 8px。
3. 禁用双击缩放或 300ms 延迟的遗留 `touch-action: manipulation`。
4. 处理触控的主动态/涟漪反馈。
5. 禁止移动端的默认高亮：`tap-highlight-color: transparent` 并提供自定义反馈。
6. 避免滚动链穿透：`overscroll-behavior: contain`。
7. 手势操作不替代唯一操作路径。

```css
/* 反例 */
.icon-btn {
  width: 20px;
  height: 20px;
}

/* 正例 */
.icon-btn {
  min-width: 44px;
  min-height: 44px;
  touch-action: manipulation;
}
```

### 10. Dark Mode & Theming

1. 使用 CSS 自定义属性定义颜色，避免硬编码色值。
2. 支持 `color-scheme: light dark`。
3. 图片/阴影在暗色模式下重新评估对比度。
4. `<meta name="theme-color">` 与当前主题同步。
5. `<select>` 下拉背景色在暗色模式下不丢失（Windows/Chrome 默认问题）。
6. 主题切换按钮状态使用 `aria-pressed` 标记。

```css
/* 反例 */
body {
  background: #fff;
  color: #000;
}

/* 正例 */
:root {
  color-scheme: light dark;
  --bg: #fff;
  --fg: #000;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --fg: #fafafa;
  }
}
body {
  background: var(--bg);
  color: var(--fg);
}
```

### 11. Locale & i18n

1. 用户可见文本必须走翻译文件，禁止硬编码。
2. 日期、时间、数字、货币使用 `Intl` API。
3. 为需要保持原文的元素设置 `translate="no"`（代码、品牌名、人名）。
4. 文案避免基于特定语序的字符串拼接。
5. 提供 `lang` 属性与当前内容语言一致。
6. 图标或 emoji 不应单独承载语义；必须配合文本或 aria-label。

```tsx
// 反例
<p>Welcome, {name}!</p>

// 正例
<p>{t('welcome', { name })}</p>
<code translate="no">npm install</code>
```

### 12. Hydration Safety

1. 服务端渲染的初始值与客户端一致，避免 hydration mismatch。
2. 依赖客户端 API 的组件使用客户端挂载守卫或 `ssr: false` 动态导入。
3. 表单输入的默认值通过 `defaultValue` / `defaultChecked` 设置，hydration 不丢失。
4. 自动聚焦不应在 hydration 时与已有焦点冲突。
5. 时钟、随机数、UUID 等不稳定值延迟到客户端生成。

```tsx
// 反例
const [id] = useState(crypto.randomUUID());

// 正例：仅在客户端唯一 ID 场景使用；若需要 SSR 可用 ID，使用框架提供的 useId()
const [id, setId] = useState('');
useEffect(() => setId(crypto.randomUUID()), []);
```

---

## 与相邻模块边界

| 本模块 M16 不深入 | 应交给 | 原因 |
| ---------------- | ------ | ---- |
| a11y 整改流程、键盘走查、焦点陷阱实现、ARIA 反模式 | M13 可访问性修复 | M13 是修复执行手册，M16 只负责发现 |
| 动画设计、时序、缓动、CSS 新特性选型 | M04 动效与交互 | M04 是设计实现指南 |
| Core Web Vitals 测量、包体积分析、渲染调优 | M14 性能优化 | M14 是性能工程与测量手册 |

若审计发现涉及上述领域，输出格式示例：

```markdown
| components/Modal.tsx | 56 | Focus States | 打开模态框时焦点未进入 | 参考 M13「焦点陷阱与模态框处理」实现 | P1 |
```

---

## 快速检查清单

- [ ] 所有交互元素可键盘到达且有可见焦点样式？
- [ ] 表单每个输入都有关联 label，错误提示已关联？
- [ ] 图片设置了 width/height 或 aspect-ratio？
- [ ] 动画有 `prefers-reduced-motion` 回退且使用 transform/opacity？
- [ ] 长列表或大数据使用虚拟化或分页？
- [ ] URL 能反映当前关键状态并支持深链？
- [ ] 可点击目标最小 44×44 CSS px（最低 24×24）？
- [ ] 暗色模式下颜色、阴影、select 背景正常？
- [ ] 用户可见文本全部来自翻译文件？
- [ ] 服务端与客户端初始状态一致，无 hydration mismatch？
