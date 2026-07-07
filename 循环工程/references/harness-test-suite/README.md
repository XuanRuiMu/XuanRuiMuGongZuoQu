# 固定回归任务集

本目录包含循环工程 skill 的最小固定回归任务集，用于在每次迭代后快速验证 skill 元文件与约定结构未被意外破坏。

## 任务清单

| 任务 | 目录 | 验证目标 |
|---|---|---|
| 任务 1 | `task-01-progress-md/` | 验证 `PROGRESS.md` 可被正确解析且包含必要章节与 FP-03 行 |
| 任务 2 | `task-02-subagent-summary/` | 验证子代理摘要 JSON 符合约定的字段与类型 |
| 任务 3 | `task-03-skill-structure/` | 验证 skill 目录结构符合规范（含本任务集） |
| 任务 4 | `task-04-evidence-structure/` | 验证 `.agents/evidence/` 目录及子目录存在，且 `EVIDENCE.md` 包含必要章节 |

## 运行方式

一次性运行全部任务：

```bash
python run_all.py
```

单独运行某个任务：

```bash
python task-01-progress-md/verify.py
python task-02-subagent-summary/verify.py
python task-03-skill-structure/verify.py
python task-04-evidence-structure/verify.py
```

每个验证脚本成功时打印 `PASS` 并返回退出码 `0`，失败时打印 `FAIL` 并返回非零退出码。
