---
name: 练习脚手架
description: >
  创建练习目录结构，包含章节、问题、解答和讲解，通过lint验证。
  触发场景：需要搭建练习目录、创建练习骨架、设置新的课程章节。
  当用户说"练习脚手架"、"创建练习"、"搭建练习目录"、"scaffold exercises"时触发此技能。
---

# 练习脚手架

创建通过 `pnpm ai-hero-cli internal lint` 的练习目录结构，然后用 `git commit` 提交。

## 目录命名

- **章节**：`exercises/` 内的 `XX-section-name/`（如 `01-retrieval-skill-building`）
- **练习**：章节内的 `XX.YY-exercise-name/`（如 `01.03-retrieval-with-bm25`）
- 章节号 = `XX`，练习号 = `XX.YY`
- 名称使用短横线命名法（小写，连字符）

## 练习变体

每个练习至少需要以下子文件夹之一：

- `problem/` - 学生工作区，含TODO
- `solution/` - 参考实现
- `explainer/` - 概念材料，无TODO

创建骨架时，默认使用 `explainer/`，除非计划另有指定。

## 必需文件

每个子文件夹（`problem/`、`solution/`、`explainer/`）需要一个 `readme.md`，要求：

- **不为空**（必须有真实内容，即使只有一行标题也行）
- 无损坏链接

创建骨架时，生成包含标题和描述的最小readme：

```md
# 练习标题

描述内容
```

如果子文件夹有代码，还需要一个 `main.ts`（>1行）。但对于骨架，仅readme的练习即可。

## 工作流

1. **解析计划** — 提取章节名称、练习名称和变体类型
2. **创建目录** — 每个路径使用 `mkdir -p`
3. **创建骨架readme** — 每个变体文件夹一个 `readme.md`，含标题
4. **运行lint** — `pnpm ai-hero-cli internal lint` 验证
5. **修复错误** — 迭代直到lint通过

## Lint规则摘要

linter（`pnpm ai-hero-cli internal lint`）检查：

- 每个练习有子文件夹（`problem/`、`solution/`、`explainer/`）
- `problem/`、`explainer/`、或 `explainer.1/` 中至少存在一个
- `readme.md` 在主子文件夹中存在且非空
- 无 `.gitkeep` 文件
- 无 `speaker-notes.md` 文件
- readme中无损坏链接
- readme中无 `pnpm run exercise` 命令
- 每个子文件夹需要 `main.ts`，除非仅含readme

## 移动/重命名练习

重新编号或移动练习时：

1. 使用 `git mv`（而非 `mv`）重命名目录 — 保留git历史
2. 更新数字前缀以维持顺序
3. 移动后重新运行lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：从计划创建骨架

给定如下计划：

```text
章节05：记忆技能构建
- 05.01 记忆简介
- 05.02 短期记忆（讲解 + 问题 + 解答）
- 05.03 长期记忆
```

创建：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

然后创建readme骨架：

```text
exercises/05-memory-skill-building/05.01-introduction-to-memory/\
explainer/readme.md -> "# 记忆简介"
exercises/05-memory-skill-building/05.02-short-term-memory/\
explainer/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/\
problem/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.02-short-term-memory/\
solution/readme.md -> "# 短期记忆"
exercises/05-memory-skill-building/05.03-long-term-memory/\
explainer/readme.md -> "# 长期记忆"
```
