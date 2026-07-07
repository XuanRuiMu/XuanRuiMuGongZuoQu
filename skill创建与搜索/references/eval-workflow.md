# 技能评估工作流

## 目录结构

结果放在 `<skill-name>-workspace/` 中：

```
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-0/
│   │   ├── with_skill/outputs/
│   │   ├── without_skill/outputs/（或 old_skill/outputs/）
│   │   ├── eval_metadata.json
│   │   └── timing.json
│   └── benchmark.json
└── iteration-2/
```

## 第1步：同轮启动所有运行

每个测试用例同时启动两个子代理：

- 有技能运行：传入 `<path-to-skill>`
- 基线运行：创建新技能时不传技能；改进现有技能时用旧版本快照

## 第2步：起草断言

运行进行中时，起草量化断言并更新 `eval_metadata.json`。

良好断言标准：

- 客观可验证
- 名称描述清晰
- 不强制主观判断

## 第3步：捕获计时数据

每个子代理完成时保存 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

## 第4步：评分、聚合、查看

1. 评分每个运行，保存 `grading.json`
2. 聚合基准：`python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`（脚本不存在时手动汇总）
3. 分析师审查：识别非判别性断言、高方差用例、时间/token权衡
4. 启动查看器：`python <skill-creator-path>/eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "my-skill" --benchmark <workspace>/iteration-N/benchmark.json`（脚本不存在时直接用文件对比）
5. 无桌面环境时用 `--static <output_path>` 生成独立HTML

## 迭代

根据用户反馈重写技能，重复上述流程，然后扩大测试集。
