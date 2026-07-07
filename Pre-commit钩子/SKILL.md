---
name: Pre-commit钩子
description: >
  在当前仓库中设置Husky pre-commit钩子，配合lint-staged（Prettier）、类型检查和测试。
  触发场景：需要添加pre-commit钩子、设置Husky、配置lint-staged、在提交时自动格式化/类型检查/测试。
  当用户说"Pre-commit钩子"、"设置pre-commit"、"Husky钩子"、"lint-staged"、"提交时格式化"时触发此技能。
---

# 设置Pre-commit钩子

## 本技能设置的内容

- **Husky** pre-commit钩子
- **lint-staged** 对所有暂存文件运行Prettier
- **Prettier** 配置（如缺失）
- **typecheck** 和 **test** 脚本在pre-commit钩子中

## 步骤

### 1. 检测包管理器

检查
`package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun）。使用存在的那个。不明确时默认npm。

### 2. 安装依赖

作为devDependencies安装：

````text
husky lint-staged prettier
```text
### 3. 初始化Husky

```bash
npx husky init
```text
这会创建 `.husky/` 目录并在package.json中添加 `prepare: "husky"`。

### 4. 创建 `.husky/pre-commit`

写入此文件（Husky v9+不需要shebang）：

```text
npx lint-staged
npm run typecheck
npm run test
```text
**适配**：将 `npm` 替换为检测到的包管理器。如果仓库的package.json中没有 `typecheck` 或 `test` 脚本，省略那些行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```text
### 6. 创建 `.prettierrc`（如缺失）

仅在无Prettier配置时创建。使用以下默认值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```text
### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json中的 `prepare` 脚本为 `"husky"`
- [ ] `prettier` 配置存在
- [ ] 运行 `npx lint-staged` 验证其工作

### 8. 提交

暂存所有变更/新建的文件并提交，消息为：`Add pre-commit hooks (husky + lint-staged + prettier)`

这将通过新的pre-commit钩子运行——是验证一切工作的良好冒烟测试。

## 备注

- Husky v9+的钩子文件不需要shebang
- `prettier --ignore-unknown` 跳过Prettier无法解析的文件（图片等）
- pre-commit先运行lint-staged（快速，仅暂存文件），然后运行完整typecheck和测试
````
