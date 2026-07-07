---
name: 文档写作
description: >
  文档写作与格式转换技能。支持结构化协作文档撰写（提案/技术规格/决策文档），
  文章编辑改进（章节重写/清晰度提升/依赖排序），
  以及将各种文件格式（PDF/DOCX/PPTX/XLSX/图片/音频/HTML/CSV/JSON/XML/ZIP/YouTube/EPub）转换为Markdown。
  触发场景：撰写文档、创建提案、起草技术规格、编写决策文档、编辑文章、改进文章、重写章节、
  文件转Markdown、提取文档内容、PDF转文字、DOCX转Markdown。
  当用户说"写文档"、"写提案"、"起草规格"、"技术文档"、"协作写文档"、"文档撰写"、
  "编辑文章"、"改进文章"、"重写章节"、"文章优化"、
  "转markdown"、"文件转文本"、"提取文档内容"、"pdf转文字"、"docx转markdown"时触发此技能。
---

# 文档写作 — 协作撰写 + 格式转换

## 模式选择

根据用户需求自动选择模式：

| 需求                            | 模式     |
| ------------------------------- | -------- |
| 撰写文档/提案/技术规格/决策文档 | 协作撰写 |
| 编辑/改进/重写现有文章          | 文章编辑 |
| 将文件转换为Markdown文本        | 格式转换 |

---

## 模式一：协作撰写

引导用户通过结构化工作流协作撰写文档。作为主动引导者，带领用户经历三个阶段。

### 何时提供此工作流

当用户需要撰写以下内容时：

- 文档
- 提案
- 技术规格
- 决策文档
- 其他结构化内容

### 三阶段工作流

#### 阶段1：上下文收集

- 理解文档目的和受众
- 收集关键信息和约束
- 确定文档类型和格式

#### 阶段2：迭代优化与结构化

- 起草文档结构
- 迭代优化内容
- 确保逻辑清晰和完整性

#### 阶段3：读者测试

- 验证文档对目标读者的可用性
- 检查可读性和理解度
- 最终修改和交付

---

## 模式二：文件转Markdown

将文件和办公文档转换为Markdown。使用MarkItDown工具。

### 支持的格式

| 格式    | 方法                     | 备注                 |
| ------- | ------------------------ | -------------------- |
| PDF     | 文本提取 + OCR回退       | 扫描版PDF使用OCR     |
| DOCX    | python-docx解析          | 保留标题、表格、列表 |
| PPTX    | python-pptx解析          | 逐幻灯片提取         |
| XLSX    | openpyxl解析             | 以Markdown表格输出   |
| 图片    | OCR（Tesseract/EasyOCR） | 支持中文文字         |
| 音频    | Whisper转录              | 支持多种语言         |
| HTML    | BeautifulSoup解析        | 去除标签，保留结构   |
| CSV     | pandas解析               | Markdown表格输出     |
| JSON    | 结构化解析               | 嵌套对象转为嵌套列表 |
| XML     | ElementTree解析          | 属性和文本提取       |
| ZIP     | 压缩包解压               | 逐个处理包含的文件   |
| YouTube | yt-dlp + Whisper         | 提取字幕或转录       |
| EPub    | EbookLib解析             | 逐章节提取           |

### 使用方法

#### 命令行

```bash
markitdown path/to/file.pdf
markitdown path/to/file.docx
markitdown path/to/file.xlsx
```

#### Python API

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("path/to/file.pdf")
print(result.text_content)
```

#### 批量转换

```python
import glob

for file_path in glob.glob("documents/**/*", recursive=True):
    result = md.convert(file_path)
    with open(f"output/{file_path.stem}.md", "w", encoding="utf-8") as f:
        f.write(result.text_content)
```

### 工作流程

1. **识别格式**：根据扩展名确定文件类型
2. **选择解析器**：选择合适的转换方法
3. **转换**：将内容提取为Markdown
4. **清理**：去除伪影，修复格式
5. **输出**：返回Markdown文本或保存到文件

### 参考文件

| 文件                                             | 加载时机                   |
| ------------------------------------------------ | -------------------------- |
| [references/API参考.md](references/API参考.md)   | 需要MarkItDown API详细参考 |
| [references/文件格式.md](references/文件格式.md) | 需要格式支持详情和限制     |
| [assets/使用示例.md](assets/使用示例.md)         | 需要使用示例               |

### 转换脚本

| 脚本                                                           | 用途                 |
| -------------------------------------------------------------- | -------------------- |
| [scripts/batch_convert.py](scripts/batch_convert.py)           | 批量转换目录中的文件 |
| [scripts/convert_literature.py](scripts/convert_literature.py) | 文献专用转换         |
| [scripts/convert_with_ai.py](scripts/convert_with_ai.py)       | AI辅助转换           |

### 约束

- OCR质量取决于图片分辨率和文字清晰度
- 音频转录需要Whisper模型（可能需要下载）
- 大型PDF处理可能耗时较长
- 复杂的Excel公式不会被保留——仅保留值
- YouTube转录需要网络连接

---

## 模式三：文章编辑（源自mattpocock/edit-article）

当用户需要编辑、改进或重写现有文章时使用此模式。

### 核心思想

信息是有向无环图（DAG），章节顺序必须尊重依赖关系。被依赖的章节必须先出现，依赖它的章节后出现。

### 工作流

#### 步骤1：章节拆分

将文章按标题分为章节，列出所有章节及其标题。

#### 步骤2：依赖分析

分析章节间的依赖关系：

1. 哪些章节定义了其他章节使用的概念？
2. 哪些章节引用了其他章节的结论？
3. 是否存在循环依赖？（如果有，必须打破）

#### 步骤3：与用户确认

向用户确认：

1. 章节列表是否完整
2. 章节顺序是否合理（依赖关系是否被尊重）
3. 哪些章节需要重点改进

#### 步骤4：逐章节重写

对每个章节执行重写，目标：

1. **清晰度**——每个概念只用一种方式解释，删除冗余解释
2. **连贯性**——章节内的段落之间有逻辑连接
3. **流畅度**——段落过渡自然，读者不需要回头重读
4. **每段最多240字符**——超过240字符的段落必须拆分

#### 步骤5：全局审查

所有章节重写完成后：

1. 检查章节间的引用是否一致
2. 检查术语是否全文统一
3. 检查是否有重复内容（同一概念在多处解释）
4. 验证依赖顺序是否正确
