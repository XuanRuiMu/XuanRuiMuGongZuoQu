# 循环工程 Environment Engineering 四维规范

本文件规定循环工程 skill 在执行过程中必须遵守的环境工程四维约束：Permissions Engineering（权限工程）、Artifacts Engineering（产物工程）、Budget Engineering（预算工程）和 Human-in-the-Loop Engineering（人在回路工程）。所有 Headless Worker 在实现功能点前必须先读取本文件，确认当前操作不违反任何维度。

---

## 1. Permissions Engineering（权限工程）

### 1.1 核心原则

- **最小权限**：子代理只能访问完成当前功能点所必需的文件和目录。
- **白名单优先**：默认禁止访问所有路径，只有列入白名单的路径才允许操作。
- **显式授权**：超出白名单的操作必须先用 `AskUserQuestion` 取得用户明确授权。
- **下层限制优先**：TRAE Shell 的 `readOnlyDirectories` / `writableDirectories` 是硬性物理边界；本 skill 的白名单必须是其子集，不得试图绕过。

### 1.2 白名单

| 路径/模式 | 用途 | 备注 |
| --- | --- | --- |
| `.agents/skills/循环工程/` | 循环工程 skill 自身目录 | 所有 skill 产物必须在此目录内 |
| `.agents/skills/循环工程/references/` | references 文件 | 可新增/修改说明性 references 文件 |
| `.agents/skills/循环工程/references/harness-test-suite/` | 回归任务集 | 可运行/新增回归测试 |
| `.agents/evidence/` | 证据目录 | 按 EVIDENCE.md 结构化要求写入 |
| 用户通过 `AskUserQuestion` 明确授权的特定文件 | 临时扩展 | 必须记录授权依据到 PROGRESS.md |

### 1.3 黑名单

| 路径/模式 | 禁止原因 | 违反后果 |
| --- | --- | --- |
| `.git/` | Git 元数据，直接操作会破坏版本历史 | 属于危险操作，任何情况下不得触碰 |
| `AGENTS.md`（项目根目录） | 项目级通用规则，只能由用户明确授权后修改 | 违反 skill 隔离与禁止自动规则 |
| `SKILL.md`（本 skill 核心流程） | 核心契约，禁止自动改写 | 违反 PROGRESS.md 当前决策 |
| 其他 skill 的 `SKILL.md` | 不属于本 skill 范围 | 违反 skill 隔离 |
| 项目源码（如插件代码、服务端代码等） | 本任务只改 skill 自身 | 违反 PROGRESS.md "不做什么" |
| 工作区根目录下非白名单文件 | 避免污染项目根目录 | 必须在 skill 目录内产出 |
| TRAE Shell `readOnlyDirectories` 中的路径 | 物理只读边界 | 工具会拒绝写入 |

### 1.4 与 TRAE Shell 权限的配合

TRAE Shell 通过 `readOnlyDirectories` 和 `writableDirectories` 声明了本次会话的物理访问边界：

- 任何写入操作的目标路径必须同时满足：
  1. 在 TRAE Shell 的 `writableDirectories` 中；
  2. 在本 skill 的白名单中。
- 读取操作的目标路径必须同时满足：
  1. 在 TRAE Shell 的 `readOnlyDirectories` 或 `writableDirectories` 中；
  2. 不在本 skill 的黑名单中（除非用户显式授权）。
- 当 TRAE Shell 限制与本 skill 白名单冲突时，以**更严格者**为准。

### 1.5 路径校验检查清单

Headless Worker 在写入任何文件前必须执行：

1. 目标路径是否在本 skill 白名单内？
2. 目标路径是否在黑名单内？
3. 目标路径是否在 TRAE Shell `writableDirectories` 内？
4. 若答案为否/是/否，立即停止并用 `AskUserQuestion` 向用户说明。

#### 路径前缀检查示例

在写入前，子代理应显式声明目标路径，并验证其前缀：

```python
from pathlib import Path
skill_root = Path('.agents/skills/循环工程/').resolve()
target = (skill_root / '.agents' / 'evidence' / 'traces' / 'fp-xx.md').resolve()
# 验证 target 是否以 skill_root 为前缀
assert target.is_relative_to(skill_root), f'目标路径越界: {target}'
```

任何写入操作的目标路径前缀必须是 `.agents/skills/循环工程/`，否则视为越界。

---

## 2. Artifacts Engineering（产物工程）

### 2.1 核心原则

- **版本化**：所有 harness 组件的修改必须可追溯、可回滚。
- **结构化**：证据必须按固定目录结构存放，禁止散落到各处。
- **备份优先**：任何自动级提案在应用前，必须先创建可恢复的备份。
- **最小留存**：过程性文件在任务结束后按用户决策清理。

### 2.2 Git 版本化要求

循环工程 skill 所在目录应纳入 Git 版本控制。所有 harness 组件修改必须遵循：

1. **自动级修改**：应用前执行 `git stash` 或 `git commit -m "backup before harness auto-apply"` 创建备份；应用后运行回归任务集验证；验证通过后方可提交。
2. **待确认/禁止自动级修改**：不得在未经 `AskUserQuestion` 同意前应用；用户同意后同样必须先备份再修改。
3. **提交信息规范**：
   - 自动级：`harness(auto): <简短描述>`
   - 待确认级：`harness(confirm): <简短描述>`
   - 禁止自动级：`harness(manual): <简短描述>`
4. **无 Git 仓库时的降级**：若工作区未初始化 Git，Headless Worker 应：
   - 提示用户初始化仓库；
   - 或手动复制待修改文件为 `<原文件名>.backup.<YYYYMMDD-HHMMSS>` 作为临时备份；
   - 在摘要中明确记录未使用 Git 备份。

### 2.3 受保护产物清单

以下产物属于 harness 结构的一部分，禁止子代理在未经授权的情况下修改：

| 路径/模式 | 禁止原因 | 违反后果 |
| --- | --- | --- |
| `references/harness-test-suite/` 下的回归测试文件 | 测试文件是验证 harness 行为的基准 | 修改测试会掩盖真实失败，使回归失去意义 |
| `EVIDENCE.md` 中的历史证据摘要 | 历史证据用于 Weakness Mining | 篡改证据会导致元循环基于虚假信息做决策 |

如需修改上述文件，必须通过 `AskUserQuestion` 取得用户明确授权，并在 PROGRESS.md 中记录授权依据。

### 2.4 回归测试设计原则

为避免 harness 回归测试随任务目标变化而频繁失效，所有新增回归测试必须遵循以下原则：

- **结构不变量优先**：只验证不会随任务变化的结构，例如目录存在、文件命名模式、必要章节标题模式、表格中包含 `FP-` 前缀记录等。
- **不硬编码任务特定内容**：禁止在断言中写入固定任务标题、固定功能点 ID 列表、固定章节顺序或固定决策内容。
- **边界与模式检查**：优先使用正则、前缀检查、存在性检查，而非精确字符串匹配。
- **测试输入与测试对象分离**：若需要样本数据，应将样本放在 `samples/` 子目录中，避免修改测试对象来迎合测试。

违反以上原则的回归测试应在 Self-Harness 元循环中被识别为 harness 弱点，并按修改分级处理。

#### 2.4.1 全局状态测试隔离

当功能点实现依赖全局可变状态（如 Redis 中的 IP 封禁、速率限制计数、验证码发送间隔等）时，回归测试设计必须考虑并发执行时的状态污染：

- 优先在测试框架配置中禁用文件/进程级并行（如 Vitest 的 `fileParallelism: false`），或在测试 setup 中清理相关全局状态。
- 禁止默认并行运行依赖共享 Redis/数据库状态的测试，除非已证明状态完全隔离。
- 敏感/限流功能的测试用例应在内部小循环中验证，确保不会因为其他测试的并发调用导致 flaky 失败。

### 2.5 证据目录 `.agents/evidence/` 结构化要求

证据目录是 Environment Engineering 与 Self-Harness 元循环的共同产物，必须严格按以下结构组织：

```text
.agents/evidence/
├── traces/          # 原始任务轨迹片段或压缩摘要
├── proposals/       # harness 改进提案（按 FP/日期命名）
├── validations/     # 提案验证结果
└── archive/         # 归档（超过 20 条后用户确认可创建）
```

| 子目录 | 命名规范 | 内容要求 |
| --- | --- | --- |
| `traces/` | `<FP-ID>-<关键词>-<YYYYMMDD>.md` | 只保留与失败模式相关的片段，禁止贴完整对话 |
| `proposals/` | `<FP-ID>-proposal-<序号>-<YYYYMMDD>.md` | 必须包含针对弱点、目标组件、修改分级、预期效果、验证方式 |
| `validations/` | `<proposal-name>-validation-<YYYYMMDD>.md` | 必须包含验证方法、结果、回归任务集输出 |
| `archive/` | 用户确认后创建 | 归档历史轨迹，保留至少一个完整周期供审计 |

### 2.6 产物清理规则

- 过程性文件（如临时备份、中间摘要）在任务结束后必须清理，但**仅限于本工作区/本项目内由循环工程 skill 创建或修改的文件**。
- `PROGRESS.md` 是否保留由用户在阶段4决定；若删除，必须确认该 `PROGRESS.md` 位于当前工作区/本项目内且由本技能创建，禁止删除其他项目或工作区根目录下非本技能创建的文件。
- `.agents/evidence/` 下的原始轨迹长期保留，EVIDENCE.md 中只保留最近 20 条摘要。

---

## 3. Budget Engineering（预算工程）

### 3.1 FP-01 结论

TRAE CN Task 工具**无法直接获取子代理级 token 用量**。TaskOutput 和任务跟踪器均无 token 字段，因此 `total_token_limit` 与 `per_subagent_token_limit` 不可作为可机器验证的熔断条件。

### 3.2 预算维度

基于 FP-01 结论，采用以下三维降级方案：

| 维度 | 字段名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- | --- |
| 子代理调用次数 | `subagent_call_limit` | 整数 | 整个循环任务中调用 Task 子代理的总次数上限 | 30 |
| Wall-clock 时间 | `wall_clock_limit_minutes` | 整数 | 任务总运行时间上限（分钟） | 120 |
| 自估算 token | `self_estimated_token_limit` | 整数或 `null` | 由主代理根据子代理返回摘要自行估算的 token 上限 | `null`（可选） |

### 3.3 熔断规则

| 条件 | 动作 | 记录位置 |
| --- | --- | --- |
| 子代理调用次数 >= `subagent_call_limit` | 停止循环，用 `AskUserQuestion` 汇报 | PROGRESS.md 元信息"状态"改为"已熔断" |
| Wall-clock 时间 >= `wall_clock_limit_minutes` | 停止循环，用 `AskUserQuestion` 汇报 | PROGRESS.md 元信息"状态"改为"已熔断" |
| 自估算 token >= `self_estimated_token_limit`（若设置） | 停止循环，用 `AskUserQuestion` 汇报 | BUDGET.md 当前状态 + AskUserQuestion |
| 同一问题修复次数达到 `per_fp_attempt_limit` | 停止该功能点修复，标记为"已阻塞" | PROGRESS.md 待处理功能点状态列 |
| 遇到无法自行解决的阻塞 | 立即停止，用 `AskUserQuestion` 汇报 | PROGRESS.md "阻塞与遗留问题"小节 |

### 3.4 计数规则

- **子代理调用次数**：每成功发起一次 Task 工具调用即计数 +1，无论子代理返回成功/失败/阻塞。
- **Wall-clock 时间**：从主代理第一次读取 PROGRESS.md 开始计时，到循环完全停止结束。
- **自估算 token**：主代理根据每个子代理返回摘要的字数按约定换算因子估算；仅作辅助参考，不作为唯一熔断依据。

### 3.5 预算覆盖关系

- `subagent_call_limit` 与 PROGRESS.md 中"总循环 30 轮"保持一致。
- `per_fp_attempt_limit` 与 PROGRESS.md 中"单问题修复上限 5 次"保持一致。
- 当多个熔断条件同时触发时，按"先发生先记录"原则写入，并在 `AskUserQuestion` 中一并汇报。

---

## 4. Human-in-the-Loop Engineering（人在回路工程）

### 4.1 核心原则

- **默认不应用**：任何需要人工确认的提案，在用户未明确同意前不得应用。
- **沉默/超时即拒绝**：用户未在合理时间内回复，或回复不明确，视为拒绝，保持现状。
- **可追溯**：所有用户决策必须简要记录到 PROGRESS.md 的"当前决策"小节。

### 4.2 必须人工确认的修改清单

以下修改属于关键决策，必须在应用前用 `AskUserQuestion` 取得用户明确同意：

| 修改类型 | 级别 | 原因 |
| --- | --- | --- |
| 修改 `SKILL.md` 核心流程 | 禁止自动 | 涉及 skill 核心契约 |
| 修改 `AGENTS.md` | 禁止自动 | 项目级通用规则 |
| 删除、新增或调整铁律 | 禁止自动 | 改变 skill 行为边界 |
| 变更停止条件或熔断上限默认值 | 禁止自动 | 影响循环安全 |
| 修改提示词返回结构 | 待确认 | 影响子代理行为 |
| 新增/删除 budget 字段 | 待确认 | 影响预算维度 |
| 调整 Permissions 白名单/黑名单 | 待确认 | 影响可访问路径 |
| 删除过程性文件（PROGRESS.md 等） | 待确认 | 可能导致断点续跑信息丢失 |
| 应用"待确认"级 harness 提案 | 待确认 | 按 HARNESS.md 分级规则执行 |

### 4.3 AskUserQuestion 触发条件

循环工程在以下场景必须停下并使用 `AskUserQuestion`：

1. **阶段1目标定义完成**：向用户确认目标、停止条件、熔断上限。
2. **阶段2任务拆解完成**：向用户确认 PROGRESS.md 内容。
3. **熔断触发**：总循环次数/子代理调用次数/Wall-clock 时间/自估算 token 达到上限。
4. **功能点阻塞**：同一问题修复超过 5 次，或后续功能点全部依赖阻塞项。
5. **Self-Harness 待确认/禁止自动提案**：元循环产生需要用户决策的提案。
6. **阶段4交付确认**：目标达成，汇总结果并询问下一步。
7. **任何超出白名单的写入请求**：必须先取得用户明确授权。

### 4.4 用户沉默/超时/拒绝时的默认行为

| 用户状态 | 默认行为 |
| --- | --- |
| 沉默或超时 | 视为拒绝；不应用提案；保持当前状态；在 PROGRESS.md 中标记为"待用户确认" |
| 明确拒绝 | 不应用提案；记录拒绝原因；继续处理其他不依赖该提案的功能点 |
| 部分同意 | 仅应用用户明确同意的部分；其余保持待确认状态 |
| 同意但要求修改 | 按用户修改后的方案重新评估修改级别，必要时再次 AskUserQuestion |

### 4.5 决策记录格式

每次人工确认后，在 PROGRESS.md 中追加一行：

```text
- <YYYY-MM-DD HH:MM> 用户确认：[决策内容摘要]
```

禁止记录完整对话，只记录决策结果。

---

## 5. 四维协同检查清单

Headless Worker 在完成功能点前必须自检以下四项：

- [ ] Permissions：所有读取/写入路径均符合白名单且不在黑名单内。
- [ ] Artifacts：修改已备份（Git stash/commit 或手动备份），证据目录结构正确。
- [ ] Budget：当前子代理调用次数、Wall-clock 时间、自估算 token 均未超限。
- [ ] Human-in-the-Loop：本功能点/提案的修改级别允许自动执行；若属于待确认/禁止自动，已获取用户授权。

---

## 6. 与现有文件的兼容性声明

- 本文件不修改 `SKILL.md`、`AGENTS.md` 或其他 skill 的核心流程。
- 本文件的白名单/黑名单与 PROGRESS.md 中"禁止触碰"和"不做什么"小节一致。
- 本文件的预算维度与 BUDGET.md 中 FP-01 后的降级方案一致。
- 本文件的证据目录结构与 EVIDENCE.md 一致。
- 本文件的修改分级与 HARNESS.md 中"自动/待确认/禁止自动"三级规则一致。
