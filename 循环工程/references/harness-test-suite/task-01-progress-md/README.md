# 任务 1：验证 PROGRESS.md 解析

## 描述
确认循环工程 skill 的 `PROGRESS.md` 存在、包含必要章节，功能点列表中只包含本次任务的 `FP-01` 与 `FP-02`，且不含越界的 `FP-03`。

## 输入
- `PROGRESS.md`（位于 skill 根目录）

## 预期输出
- `PASS: PROGRESS.md 结构正确，包含 FP-01/FP-02 且无 FP-03`

## 验证命令

```bash
python task-01-progress-md/verify.py
```
