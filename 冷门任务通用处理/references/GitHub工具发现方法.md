# GitHub工具发现方法

本文档详细说明阶段3"GitHub工具发现"的执行方法，借鉴 skill-discovery 的工作流。

## 搜索维度

在GitHub生态中搜索三类工具：

| 工具类型    | 用途                         | 示例                           |
| ----------- | ---------------------------- | ------------------------------ |
| Skill       | 封装了特定任务工作流的指令包 | 清理系统、文件处理、音视频处理 |
| MCP服务器   | 提供工具能力的运行时服务     | 文件系统、数据库、API集成      |
| 脚本/库/CLI | 可直接执行的工具             | Python脚本、npm包、命令行工具  |

## 搜索方法

### 方法1：Skills CLI 搜索

```bash
npx skills find "<关键词>"
```

**使用要点**：

- 关键词用英文效果更好
- 尝试多个同义词：`clean`、`cleanup`、`disk`、`storage`
- PowerShell环境用 `Select-Object -First N` 替代 `head`

### 方法2：GitHub 代码搜索

直接在GitHub搜索SKILL.md文件：

```text
https://github.com/search?q=skill+<关键词>+SKILL.md&type=code
```

**搜索技巧**：

- `skill <关键词> SKILL.md` — 搜索包含关键词的skill
- `mcp server <关键词>` — 搜索MCP服务器
- `<关键词> tool cli` — 搜索CLI工具
- `filename:SKILL.md <关键词>` — 精确搜索SKILL.md文件

### 方法3：GitHub 仓库搜索

```text
https://github.com/search?q=<关键词>&type=repositories
```

**筛选条件**：

- Sort by: Stars（按星数排序）
- Language: 根据任务选择
- Updated: >2025-01-01（最近更新）

### 方法4：聚合仓库浏览

浏览知名的skill/tool聚合仓库：

| 仓库                                | 内容             | URL                                            |
| ----------------------------------- | ---------------- | ---------------------------------------------- |
| awesome-claude-skills               | Claude skill聚合 | github.com/ComposioHQ/awesome-claude-skills    |
| anthropics/skills                   | 官方skill        | github.com/anthropics/skills                   |
| obra/superpowers                    | 工程方法论skill  | github.com/obra/superpowers                    |
| K-Dense-AI/claude-scientific-skills | 科研skill        | github.com/K-Dense-AI/claude-scientific-skills |
| modelcontextprotocol                | MCP官方          | github.com/modelcontextprotocol                |
| awesome-mcp-servers                 | MCP聚合          | github.com/punkpeye/awesome-mcp-servers        |

### 方法5：包管理器搜索

| 包管理器 | 搜索命令                          | 适用场景         |
| -------- | --------------------------------- | ---------------- |
| npm      | `npm search <关键词>`             | Node.js工具、CLI |
| pip      | `pip search <关键词>` 或 PyPI网站 | Python工具、库   |
| brew     | `brew search <关键词>`            | macOS系统工具    |
| winget   | `winget search <关键词>`          | Windows系统工具  |
| scoop    | `scoop search <关键词>`           | Windows便携工具  |

## 工具质量评估

借鉴 skill-discovery 的评估方法，对发现的工具进行质量评估。

### 评估维度

| 维度        | 高分标准                 | 低分警告             |
| ----------- | ------------------------ | -------------------- |
| 安装量/星数 | 1K+ stars/installs       | <100 stars           |
| 来源信誉    | 官方、知名组织、知名作者 | 未知作者、无个人信息 |
| 维护状态    | 最近6个月有更新          | 1年以上未更新        |
| 文档质量    | README详细、有示例       | README简陋、无示例   |
| 兼容性      | 与当前环境兼容           | 依赖不兼容环境       |
| 许可证      | MIT/Apache等开源协议     | 无许可证或专有       |

### 评估流程

1. **读取README/SKILL.md**：了解工具功能和用法
2. **检查最近提交**：`gh api repos/{owner}/{repo}/commits?per_page=1`
3. **检查星数和fork数**：GitHub仓库页面
4. **检查issues**：open issues数量、是否有人回复
5. **验证兼容性**：依赖要求、运行环境

### 质量等级

| 等级 | 标准                                          | 建议               |
| ---- | --------------------------------------------- | ------------------ |
| A    | 1K+ stars，官方/知名来源，6月内更新，文档完善 | 直接使用           |
| B    | 100-1K stars，来源可信，1年内更新，文档可用   | 可使用，注意验证   |
| C    | <100 stars，或来源不明，或更新较旧            | 谨慎使用，充分测试 |
| D    | 无文档，无更新，或安全风险                    | 不建议使用         |

## 工具清单格式

```markdown
# [任务名] 可用工具清单

## Skills

### 1. [Skill名称]

- **来源**：[owner/repo](URL)
- **星数**：[N]
- **质量等级**：[A/B/C]
- **安装方式**：`npx skills add owner/repo@skill -g -y`
- **适用场景**：[描述]
- **评估**：[一句话评价]

## MCP服务器

### 1. [MCP名称]

- **来源**：[owner/repo](URL)
- **星数**：[N]
- **质量等级**：[A/B/C]
- **安装方式**：[安装命令]
- **提供工具**：[工具列表]
- **适用场景**：[描述]

## 脚本/库/CLI

### 1. [工具名称]

- **来源**：[owner/repo](URL) 或 [包管理器]
- **星数/下载量**：[N]
- **质量等级**：[A/B/C]
- **安装方式**：[安装命令]
- **使用示例**：[基本用法]
- **适用场景**：[描述]
```

## 搜索策略

### 关键词扩展

对每个任务，生成多个搜索关键词：

```text
任务：清理C盘垃圾
关键词：
- clean C drive
- disk cleanup
- free up space
- 系统清理
- junk file cleaner
- Windows storage sense
- CCleaner alternative
```

### 搜索顺序

1. 先搜skill（可能有现成工作流）
2. 再搜MCP（可能有工具能力）
3. 最后搜脚本/库/CLI（执行工具）

### 替代方案

如果某类工具搜索结果少：

- 尝试同义词和上位词
- 搜索"how to <任务>"找教程中提到的工具
- 搜索"<任务> best tool 2026"找推荐文章
- 搜索"<任务> github"找开源项目

## 安全注意事项

- **不安装未评估的工具**：所有工具必须经过质量评估
- **检查工具权限**：了解工具需要的权限范围
- **优先官方源**：从官方仓库/包管理器安装
- **验证哈希**：如有可能验证下载文件的完整性
- **沙盒优先**：优先在沙盒/测试环境试用
