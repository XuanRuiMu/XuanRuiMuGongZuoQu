---
name: Obsidian笔记库
description: >
  搜索、创建和管理Obsidian笔记库中的笔记，支持wikilinks语法和index笔记。
  触发场景：需要在Obsidian笔记库中查找、创建或组织笔记。
  当用户说"Obsidian笔记"、"搜索笔记"、"创建笔记"、"笔记库"、"obsidian vault"时触发此技能。
---

# Obsidian笔记库

## 笔记库位置

`/mnt/d/Obsidian Vault/AI Research/`

根层级基本扁平。

## 命名规范

- **Index笔记**：聚合相关主题（如 `Ralph Wiggum Index.md`、`Skills Index.md`、`RAG Index.md`）
- 所有笔记名使用**标题大小写**
- 不用文件夹组织 — 使用链接和index笔记代替

## 链接

- 使用Obsidian `[[wikilinks]]` 语法：`[[笔记标题]]`
- 笔记在底部链接到依赖/相关笔记
- Index笔记就是 `[[wikilinks]]` 的列表

## 工作流

### 搜索笔记

```bash
# 按文件名搜索
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "关键词"

# 按内容搜索
grep -rl "关键词" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```

或直接在笔记库路径上使用Grep/Glob工具。

### 创建新笔记

1. 文件名使用**标题大小写**
2. 内容作为一个学习单元编写（按笔记库规则）
3. 在底部添加 `[[wikilinks]]` 链接到相关笔记
4. 如果属于编号序列，使用层级编号方案

### 查找相关笔记

在笔记库中搜索 `[[笔记标题]]` 以查找反向链接：

```bash
grep -rl "\\[\\[笔记标题\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```

### 查找index笔记

```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```
