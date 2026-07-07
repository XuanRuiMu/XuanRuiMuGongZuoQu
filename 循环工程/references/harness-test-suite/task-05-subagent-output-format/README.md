# 任务 5：验证子代理输出摘要字段格式

## 描述
验证子代理返回摘要中的 `token_estimate`、`failure_tags`、`evidence_link` 字段符合 `references/子代理提示词模板.md` 的格式要求。

## 输入
- `samples/valid.txt`：格式正确的子代理摘要示例
- `samples/invalid_missing.txt`：缺少必要字段的错误摘要示例
- `samples/invalid_typo.txt`：`evidence_link` 存在拼写错误的摘要示例

## 预期输出
- `PASS: 子代理输出摘要字段格式验证通过`

## 验证命令

```bash
python task-05-subagent-output-format/verify.py
```
