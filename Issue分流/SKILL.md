---
name: Issue分流
description: >
  通过状态机驱动的分流角色对Issue进行分流处理。包含5个状态角色和2个分类角色，AI生成标记，needs-info模板，恢复会话规则。
  触发场景：创建Issue、分流Issue、审查Bug或功能请求、为AFK智能体准备Issue、管理Issue工作流。
  当用户说"分流"、"triage"、"审查Issue"、"处理Issue"、"Issue分流"、"管理Issue工作流"时触发此技能。
---

# Issue分流

通过一个小型状态机的分流角色，在项目Issue跟踪器上移动Issue。

分流期间发布到Issue跟踪器的每条评论或Issue**必须**以此免责声明开头：

````text
> *此内容由AI在分流过程中生成。*
```text
## 参考文档

- [AGENT-BRIEF.md](references/AGENT-BRIEF.md) — 如何编写持久的智能体简报
- [OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md) — `.out-of-scope/` 知识库的工作方式

## 角色

两个**分类**角色：

- `bug` — 某物损坏了
- `enhancement` — 新功能或改进

五个**状态**角色：

- `needs-triage` — 需要维护者评估
- `needs-info` — 等待报告者提供更多信息
- `ready-for-agent` — 已完整描述，可供AFK智能体执行
- `ready-for-human` — 需要人工实现
- `wontfix` — 不会处理

每个分流的Issue应恰好携带一个分类角色和一个状态角色。如果状态角色冲突，标记并询问维护者后再做任何操作。

这些是规范角色名称——Issue跟踪器中使用的实际标签字符串可能不同。映射关系应该已提供给你——如果没有，运行 `/setup-matt-pocock-skills`。

状态转换：未标记的Issue通常先进入 `needs-triage`；然后移动到 `needs-info`、`ready-for-agent`、`ready-for-human` 或 `wontfix`。`needs-info` 在报告者回复后回到 `needs-triage`。维护者可以随时覆盖——标记看起来异常的转换并在继续前询问。

## 调用

维护者调用 `/triage` 并用自然语言描述他们想要什么。解释请求并执行。示例：

- "给我看需要我关注的东西"
- "看看 #42"
- "把 #42 移到 ready-for-agent"
- "有什么是智能体可以接手的？"

## 显示需要关注的内容

查询Issue跟踪器并展示三个桶，按最旧排序：

1. **未标记** — 从未分流。
2. **`needs-triage`** — 评估进行中。
3. **`needs-info` 且报告者在上次分流备注后有新活动** — 需要重新评估。

显示计数和每个Issue的一行摘要。让维护者选择。

## 分流特定Issue

1. **收集上下文。**阅读完整Issue（正文、评论、标签、报告者、日期）。解析之前的分流备注，避免重复已解决的问题。使用项目的领域术语表探索代码库，尊重该区域的ADR。阅读 `.out-of-scope/*.md` 并揭示与此Issue相似的先前拒绝记录。

2. **推荐。**告诉维护者你的分类和状态推荐及理由，加上与Issue相关的简短代码库摘要。等待指示。

3. **复现（仅限Bug）。**在任何烤问之前，尝试复现：阅读报告者的步骤，追踪相关代码，运行测试或命令。报告结果——成功复现及代码路径、复现失败，或细节不足（强 `needs-info` 信号）。确认的复现会产生更强的智能体简报。

4. **烤问（如需要）。**如果Issue需要充实，运行一个 `/grill-with-docs` 会话。

5. **应用结果：**
   - `ready-for-agent` — 发布智能体简报评论（[AGENT-BRIEF.md](references/AGENT-BRIEF.md)）。
   - `ready-for-human` — 与智能体简报相同结构，但注明为什么不能委派（判断决策、外部访问、设计决策、手动测试）。
   - `needs-info` — 发布分流备注（下方模板）。
   - `wontfix`（Bug）— 礼貌解释，然后关闭。
   - `wontfix`（增强）— 写入 `.out-of-scope/`，从评论中链接，然后关闭（[OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md)）。
   - `needs-triage` — 应用角色。如有部分进展可选择性评论。

## 快速状态覆盖

如果维护者说"把 #42 移到 ready-for-agent"，信任他们并直接应用角色。确认你即将做什么（角色变更、评论、关闭），然后执行。跳过烤问。如果移到 `ready-for-agent` 而没有烤问会话，询问他们是否要编写智能体简报。

## Needs-info模板

```markdown
## 分流备注

**目前已确认的内容：**

- 要点1
- 要点2

**仍需你提供的信息（@报告者）：**

- 问题1
- 问题2
```text
在"目前已确认的内容"下捕获烤问期间解决的所有内容，这样工作不会丢失。问题必须具体且可操作，而非"请提供更多信息"。

## 恢复之前的会话

如果Issue上存在之前的分流备注，阅读它们，检查报告者是否回答了任何待解决的问题，并在继续之前呈现更新后的情况。不要重复问已解决的问题。
````
