# 视觉质检

## 质检体系

### 0. ⚠️ AI识图能力检查（必须首先执行）

**在执行视觉质检前，必须先确认当前AI Agent是否具备识图能力。**

判断标准：当前Agent能否读取和分析图片文件（PNG/JPG）。

- **有识图能力**：正常执行视觉质检全流程（截图 → 重叠检测 → AI视觉分析）
- **无识图能力**：必须使用 `AskUserQuestion` 询问用户：
  - 选项A：换一个有识图能力的模型继续
  - 选项B：跳过AI视觉分析，仅执行程序化重叠检测
  - 选项C：跳过视觉质检，仅执行内容质检

**不可在无识图能力时静默跳过视觉质检！必须停下来和用户确认。**

### 1. 视觉质检（Spire截图 + 重叠检测 + 深度布局检测）

#### 1a. 截图 + 程序化重叠检测

```python
from scripts.spire.visual_inspector import PPTVisualInspector

inspector = PPTVisualInspector("output.pptx", resolution="hd")

# 程序化重叠检测（不需要识图能力）
overlaps = inspector.detect_overlaps(min_overlap_ratio=0.05)
for issue in overlaps:
    print(f"第{issue.slide_index+1}页: {issue.shape_a} 与 {issue.shape_b} 重叠 [{issue.severity}]")

# 生成完整报告（含重叠检测）
report = inspector.generate_report()
```

**重叠检测**（程序化，不需要识图能力）：

- 自动检测每页所有元素之间的边界重叠
- 两个有文字的元素重叠标记为 `critical`
- 仅装饰性元素重叠标记为 `warning`
- `min_overlap_ratio=0.05`：重叠面积占较小元素5%以上才报告

#### 1b. 深度布局检测（必做，补充重叠检测无法发现的问题）

```python
from scripts.validate_layout import PPTXLayoutValidator

validator = PPTXLayoutValidator("output.pptx")
validator.validate()
print(validator.get_report())
```

**深度检测覆盖范围**（重叠检测无法发现的问题）：

- 文字溢出容器边界
- 低对比度元素（文字与背景色差不足）
- 空白页（无可见元素）
- 箭头悬空（连接线无有效端点）
- 字号过小（标题<18pt / 正文<12pt / 备注<8pt / 文本框<10pt）✅ 已实现
- 元素超出幻灯片边界

**⚠️ 两步检测必须都执行**：重叠检测（1a）发现元素间冲突，深度布局检测（1b）发现单元素问题。两者互补，不可替代。

**分辨率选项**：default(1000×562) / hd(1920×1080) / 2k(2560×1440) / 4k(3840×2160)

**输出**：

- `_{filename}_质检/slide_XX.png` — 每页截图
- `_{filename}_质检/inspection_report.json` — 质检报告（含重叠检测结果）

**AI视觉分析**（需要识图能力）：将截图发送给AI模型，使用报告中的分析提示词进行5维度评估：

- 文字可读性 (25%)
- 布局平衡性 (25%)
- 配色协调性 (20%)
- 层次清晰度 (15%)
- 整体美观度 (15%)

### 2. 内容质检

```bash
python -m markitdown output.pptx
```

检查缺失内容、错别字、顺序错误。

**规则**：

1. 视觉质检和内容质检都必须执行
2. `blank_slide` 是生成缺陷，不可跳过
3. 发现问题后修复并重新质检，最多3轮
4. 质检输出目录：`{工作区根目录}/玄锐暮PPT/{项目名}/质检/`
5. **重叠检测中 `critical` 级别的问题必须修复**
6. **无识图能力时必须先询问用户，不可静默跳过**
