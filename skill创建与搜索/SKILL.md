---
name: skill创建与搜索
description: >
  发现、搜索、安装、创建和改进agent技能。Use when
  用户想找技能、安装技能、创建新技能、编辑优化现有技能、测试技能性能或优化技能触发描述。
  触发场景：搜索技能、安装技能、创建技能、编辑技能、优化技能、测试技能、skill市场、写SKILL.md。
  当用户说"找技能"、"找一个...skill"、"有没有技能"、"推荐一个...skill"、"安装技能"、"创建技能"、"新建技能"、"编辑技能"、"优化技能"、"测试技能"、"写SKILL.md"时触发此技能。
---

# skill创建与搜索

## 适用场景

- 用户想找某个领域的现成技能
- 用户想安装、更新或管理技能
- 用户想从零创建新技能
- 用户想编辑、优化或测试现有技能

## 核心原则：先搜索，再创建

创建任何新技能前，必须先在GitHub生态中搜索是否已有相关技能。优先安装高质量现有技能，避免重复造轮子。

## 工作流

### 阶段1：搜索与发现

1. 理解用户需求：领域、具体任务、常见程度
2. 查 [skills.sh](https://skills.sh/) 排行榜
3. 运行CLI搜索：`npx skills find [关键词] [--owner <所有者>]`
4. 验证质量：
   - 安装量：优先≥1K，<100需谨慎
   - 来源信誉：官方源（anthropics/vercel-labs/microsoft）优先
   - GitHub星数：通过 `gh api repos/<owner>/<repo> --jq '.stargazers_count'` 或 WebSearch 查询；<100需谨慎
5. 向用户展示选项：名称、功能、安装量、来源、安装命令
6. 确认用户意图：
   - 若用户仅想了解，提供选项后停止
   - 若用户同意安装，执行：`npx skills add <owner/repo@skill> -g -y`

### 阶段2：创建与改进

未找到合适技能或用户想自定义时：

1. 捕获意图：技能做什么、何时触发、输出格式、是否测试
2. 访谈研究：边缘情况、输入输出、示例文件、成功标准、依赖项
3. 编写SKILL.md：name、description、compatibility、正文
4. 生成2-3个真实测试提示词，保存到 `evals/evals.json`
5. 并行运行：有技能 vs 基线
6. 起草量化断言，捕获 `timing.json`
7. 评分、聚合、启动查看器
8. 根据反馈重写，迭代直到满意
9. 扩大测试集再验证

### 阶段3：优化与交付

1. 安全扫描：`python3 scripts/security_scan.py <skill-path>/`（环境无脚本时跳过）
2. 规范验证：`python3 scripts/validate.py <skill-path>/`（环境无脚本时跳过）
3. 优化description：生成20个触发评估查询，运行优化循环
4. 跨平台导出（如需）：生成AGENTS.md和Tier2平台格式

## 铁律

| 规则         | 内容                                   |
| ------------ | -------------------------------------- |
| 先搜索后创建 | 任何新技能创建前必须搜索已有技能       |
| 质量验证     | 推荐前验证安装量、来源信誉、GitHub星数 |
| 渐进披露     | SKILL.md<500行，大文件拆references/    |
| 解释原因     | 用"为什么重要"替代大写MUST             |
| 测试驱动     | 可客观验证的技能必须写测试用例         |
| 无惊奇原则   | 技能内容不得包含恶意代码或误导性意图   |

## 参考文件

| 文件                                                                       | 加载时机         |
| -------------------------------------------------------------------------- | ---------------- |
| [references/skill-writing-guide.md](references/skill-writing-guide.md)     | 编写SKILL.md时   |
| [references/eval-workflow.md](references/eval-workflow.md)                 | 运行测试评估时   |
| [references/cross-platform-export.md](references/cross-platform-export.md) | 需要跨平台导出时 |
