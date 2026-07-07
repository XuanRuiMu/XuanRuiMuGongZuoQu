# 循环工程预算与熔断

本文件定义循环工程运行时的资源预算字段、默认上限和熔断规则。

## 预算字段定义

| 字段 | 类型 | 说明 | 当前状态 |
| --- | --- | --- | --- |
| `total_token_limit` | 整数或 `null` | 整个循环任务的总 token 上限 | **不可获取**（FP-01 结论），保持 `null` |
| `per_subagent_token_limit` | 整数或 `null` | 单个子代理调用的 token 上限 | **不可获取**（FP-01 结论），保持 `null` |
| `subagent_call_limit` | 整数 | 整个循环任务中调用 Task 子代理的总次数上限 | 默认 30，与 `total_turn_limit` 一致 |
| `total_turn_limit` | 整数 | 主代理与子代理交互的总轮次上限 | 默认 30 |
| `per_fp_attempt_limit` | 整数 | 单个功能点内部修复次数上限 | 默认 5 |
| `wall_clock_limit_minutes` | 整数 | 任务总 wall-clock 时间上限（分钟） | 默认 120 |
| `self_estimated_token_limit` | 整数或 `null` | 主代理根据子代理返回摘要自行估算的 token 上限 | 默认 `null`（可选） |
| `budget_source` | 字符串 | token 数据来源说明：`TRAE_CN_TASK`、`USER_ESTIMATE`、`UNAVAILABLE` | `UNAVAILABLE`（FP-01 结论） |

## 默认预算上限

| 类型 | 默认值 | 说明 |
| --- | --- | --- |
| 总循环次数 | 30 | 与 PROGRESS.md 中"熔断上限：总循环 30 轮"一致 |
| 子代理调用次数 | 30 | 与 `total_turn_limit` 一致，作为 token 不可获取时的主要熔断维度 |
| 单问题修复次数 | 5 | 与 PROGRESS.md 中"单问题修复上限 5 次"一致 |
| Token 总预算 | `null` | FP-01 结论：TRAE CN 无法提供子代理级 token 用量，标记为不可获取 |
| 单个子代理 Token 预算 | `null` | FP-01 结论：TRAE CN 无法提供子代理级 token 用量，标记为不可获取 |
| 自估算 Token 预算 | `null` | 可选辅助维度，由用户或主代理按需设置 |
| Wall-clock 时间 | 120 分钟 | 防止任务无限运行；用户可覆盖 |

## 熔断规则

| 条件 | 动作 | 记录位置 |
| --- | --- | --- |
| 同一问题修复次数达到 `per_fp_attempt_limit` | 停止该功能点修复，标记为"已阻塞"，返回主代理 | PROGRESS.md 待处理功能点状态列 |
| 总循环次数达到 `total_turn_limit` | 停止整个循环，用 AskUserQuestion 汇报当前状态 | PROGRESS.md 元信息"状态"改为"已熔断" |
| 子代理调用次数达到 `subagent_call_limit` | 停止整个循环，用 AskUserQuestion 汇报 | PROGRESS.md 元信息"状态"改为"已熔断" |
| Wall-clock 时间达到 `wall_clock_limit_minutes` | 停止整个循环，提示用户时间耗尽 | PROGRESS.md 元信息"状态"改为"已熔断" |
| 自估算 token 达到 `self_estimated_token_limit`（若设置） | 停止整个循环，提示用户预算耗尽 | BUDGET.md 当前状态 + AskUserQuestion |
| 遇到无法自行解决的阻塞 | 立即停下，用 AskUserQuestion 汇报 | PROGRESS.md"阻塞与遗留问题"小节 |

> **说明**：`total_token_limit` 与 `per_subagent_token_limit` 因 FP-01 结论不可获取，不作为熔断条件。Token 相关熔断仅当用户显式设置 `self_estimated_token_limit` 时生效。

## FP-01 结论回填

FP-01 已完成验证，结论如下：

```yaml
budget_source: UNAVAILABLE  # TRAE CN Task 工具无法提供子代理级 token 用量
actual_token_field_name: null  # TaskOutput 和任务跟踪器均无 token 字段
total_token_limit: null  # 不可获取，不作为熔断条件
per_subagent_token_limit: null  # 不可获取，不作为熔断条件
fallback_strategy: "子代理调用次数 + wall-clock 时间 + 可选的自估算 token 作为预算维度"
```

降级方案细节：

1. **子代理调用次数**：每发起一次 Task 工具调用即计数 +1，上限 30，与 `total_turn_limit` 一致。
2. **Wall-clock 时间**：从主代理首次读取 PROGRESS.md 开始计时，上限 120 分钟。
3. **自估算 token**：主代理根据子代理返回摘要的字数估算，仅作为可选辅助维度；不设置时不触发熔断。

原 `total_token_limit` 与 `per_subagent_token_limit` 字段保留但值为 `null`，用于记录 FP-01 结论，避免后续功能点重复验证。

## 兼容性声明

- 本文件默认上限与 PROGRESS.md 中现有熔断规则一致，不引入新的数值约束。
- FP-01 已结论：TRAE CN 无法提供子代理级 token 用量，token 相关字段保持 `null` 并采用子代理调用次数 + wall-clock 时间 + 可选自估算 token 的降级方案。
- 本文件与 `references/EnvironmentEngineering.md` 中 Budget Engineering 维度一致。
