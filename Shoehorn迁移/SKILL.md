---
name: Shoehorn迁移
description: >
  将测试文件中的`as`类型断言迁移为@total-typescript/shoehorn的类型安全替代方案。支持fromPartial/fromAny/fromExact三种模式。
  触发场景：需要将测试中的`as`断言替换为shoehorn、在测试中使用部分数据、迁移类型断言。
  当用户说"Shoehorn迁移"、"替换as断言"、"shoehorn"、"测试类型安全"时触发此技能。
---

# Shoehorn迁移

## 为什么用shoehorn？

`shoehorn`让你在测试中传递部分数据，同时保持TypeScript类型安全。它用类型安全的替代方案替换 `as` 断言。

**仅用于测试代码。** 永远不要在生产代码中使用shoehorn。

测试中 `as` 的问题：

- 被训练不要使用它
- 必须手动指定目标类型
- 故意传错误数据时需要双重断言（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 属性很多但只需少量的大对象

迁移前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...还有20个属性
};

it("gets user by id", () => {
  // 只关心body.id但必须伪造整个Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...伪造全部20个属性
  });
});
```

迁移后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

迁移前：

```ts
getUser({ body: { id: "123" } } as Request);
```

迁移后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

迁移前：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // 故意用错误类型
```

迁移后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 何时使用各函数

| 函数            | 使用场景                              |
| --------------- | ------------------------------------- |
| `fromPartial()` | 传递仍能通过类型检查的部分数据        |
| `fromAny()`     | 传递故意错误的数据（保留自动补全）    |
| `fromExact()`   | 强制完整对象（稍后与fromPartial互换） |

## 工作流

1. **收集需求** — 询问用户：
   - 哪些测试文件有 `as` 断言导致问题？
   - 是否涉及只需少量属性的大对象？
   - 是否需要传递故意错误的数据用于错误测试？

2. **安装并迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找含 `as` 断言的测试文件：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 将 `as Type` 替换为 `fromPartial()`
   - [ ] 将 `as unknown as Type` 替换为 `fromAny()`
   - [ ] 添加 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查验证
