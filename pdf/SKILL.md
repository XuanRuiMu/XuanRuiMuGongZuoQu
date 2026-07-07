---
name: pdf
description:
  综合 PDF 处理工具包，用于提取文字和表格、创建新 PDF、合并/拆分文档、处理表单。当需要填写 PDF
  表单或以编程方式大规模处理、生成、分析 PDF
  文档时使用。触发场景：处理PDF文件、合并PDF、拆分PDF、添加水印、PDF加密解密、OCR识别、填写PDF表单、PDF转文字、扫描件识别。当用户说"pdf"、"PDF处理"、"合并pdf"、"拆分pdf"、"pdf加水印"、"pdf加密"、"pdf转文字"、"扫描件识别"时触发此技能。
license: Proprietary. LICENSE.txt has complete terms
---

# PDF 处理指南

## 概述

本指南涵盖使用 Python 库和命令行工具进行 PDF 处理的核心操作。如需高级功能、JavaScript 库和详细示例，请参阅 REFERENCE.md。如需填写 PDF 表单，请阅读 FORMS.md 并按其说明操作。

## 快速开始

```python
from pypdf import PdfReader, PdfWriter

# 读取 PDF
reader = PdfReader("document.pdf")
print(f"页数: {len(reader.pages)}")

# 提取文字
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## 长 PDF 处理工作流

当 PDF 文件较长时，不要依赖单次全文输出。应先按页提取文件，再用关键词或正则表达式检索。 `extract_pages.py`
在提取时会移除 `(cid:123)`
样式的垃圾 token，以减少上下文浪费。当检测到长合并 token 时，还会回退到单词级提取，为英文文本修复缺失的空格。

### 多查询检索工作流

> **Windows 注意：** Windows 上没有 `bash`。请将下文所有 `bash scripts/search_extracted.sh` 替换为
> `python scripts/search_extracted.py`。参数完全相同。

如果有多个查询需要检索，**切勿多次单独调用 `search_extracted.sh`**。正确做法：

1. 将所有查询写入一个文本文件（每行一个查询）
2. 使用 `--query-file` 一次性检索所有查询
3. 脚本会自动对所有查询的命中页进行去重

```bash
# 创建 queries.txt，每行一个查询
echo "find methodology" > queries.txt
echo "find results" >> queries.txt
echo "find conclusion" >> queries.txt

# 一次性检索所有查询并去重
bash scripts/search_extracted.sh extracted --query-file queries.txt
```

### 强制检索规则

对于任务导向型处理（例如准备 PPT 素材），必须始终使用基于查询的检索方式从已提取文件中获取内容。

- 必须：提取到 `pages/page_XXXX.txt`
- 必须：根据用户意图和关键约束构建任务级长查询
- 必须：运行 `search_extracted.sh` 并将匹配文件作为证据
- 必须：将完整匹配页作为命中结果的上下文
- 必须：当命中位于前 5 行内时，包含上一页
- 必须：当命中位于后 5 行内时，包含下一页
- 必须：对已包含的上下文页去重
- 禁止：默认读取固定页范围（如前 20 页）
- 禁止：将大范围页拼接成一个长上下文

```bash
# 1) 每页提取一个文本文件
python3 scripts/extract_pages.py input.pdf extracted

# 输出：
# extracted/pages/page_0001.txt
# extracted/pages/page_0002.txt
# ...

# 2) 任务级长查询检索（短语提取 + 召回/重排）
bash scripts/search_extracted.sh extracted "find methodology and experimental setup for ReAct with action-observation loop and reasoning traces"

# 3) 正则检索
bash scripts/search_extracted.sh extracted "ReAct|reasoning|agent" --regex

# 4) 多查询检索（跨查询页去重）
# queries.txt 每行一个查询
bash scripts/search_extracted.sh extracted --query-file queries.txt
```

### 端到端示例

```bash
# 目标：从长 PDF 中查找"方法 + 指标"的证据

python3 scripts/extract_pages.py report.pdf extracted

# 查找方法论相关证据
bash scripts/search_extracted.sh extracted "find method section describing interleaved reasoning and acting with concrete procedure details"

# 从页面文本中查找数字证据
bash scripts/search_extracted.sh extracted "[0-9]{4}|[0-9]+%" --regex
```

对于页面文件，每次命中返回整页作为上下文。如果命中靠近页面边界（前 5 行或后 5 行），还会包含相邻页（仅包含一次）。对于长查询，检索脚本会自动提取短语和关键词，计算 IDF 加权的召回/重排，并保留前 3 个匹配页（上下文扩展前）。使用
`--query-file` 时，匹配页会在最终输出前跨查询去重。使用匹配文件路径（例如
`pages/page_0031.txt`）作为下游任务的直接证据输入。

### 回退策略

如果 `search_extracted.sh` 返回"No matches found"，应回退到直接读取所有已提取的页面文件。按顺序遍历
`pages/page_XXXX.txt`，将每页内容作为上下文读取。

### 反模式（切勿使用）

```python
# 错误：固定范围读取会导致无关上下文并遗漏关键证据
with pdfplumber.open("document.pdf") as pdf:
    full_text = ""
    for page in pdf.pages[:20]:
        full_text += page.extract_text() or ""
```

始终优先使用"提取到文件 + grep 检索"，而非固定范围全文读取。

## Python 库

### pypdf - 基本操作

#### 合并 PDF

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### 拆分 PDF

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### 提取元数据

```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"标题: {meta.title}")
print(f"作者: {meta.author}")
print(f"主题: {meta.subject}")
print(f"创建者: {meta.creator}")
```

#### 旋转页面

```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # 顺时针旋转 90 度
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - 文字和表格提取

#### 带布局的文本提取

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### 提取表格

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"第 {i+1} 页第 {j+1} 个表格：")
            for row in table:
                print(row)
```

#### 高级表格提取

```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # 检查表格是否为空
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# 合并所有表格
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - 创建 PDF

#### CJK 字体支持（中文/日文/韩文）

创建包含非 ASCII 文本（如中文、日文、韩文）的 PDF 时，必须先注册支持 CJK 的字体：

```python
import os
import platform
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_cjk_font():
    """根据操作系统注册支持 CJK 的字体"""
    system = platform.system()

    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("CJKFont", font_path, subfontIndex=0))
            return "CJKFont"
    return None

# 创建 PDF 前先注册 CJK 字体
cjk_font = register_cjk_font()
```

#### 专业样式（必须使用）

始终使用以下精心设计的样式来生成专业外观的 PDF：

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

PRIMARY_COLOR = HexColor('#1a365d')
ACCENT_COLOR = HexColor('#2b6cb0')

def get_professional_styles(cjk_font='CJKFont'):
    """返回用于 PDF 生成的专业样式字典"""
    return {
        'title': ParagraphStyle(
            'Title', fontName=cjk_font, fontSize=28, leading=34,
            textColor=PRIMARY_COLOR, spaceAfter=20, alignment=1, wordWrap='CJK'
        ),
        'subtitle': ParagraphStyle(
            'Subtitle', fontName=cjk_font, fontSize=14, leading=18,
            textColor=HexColor('#4a5568'), spaceAfter=30, alignment=1, wordWrap='CJK'
        ),
        'h1': ParagraphStyle(
            'H1', fontName=cjk_font, fontSize=20, leading=26,
            textColor=PRIMARY_COLOR, spaceBefore=24, spaceAfter=12, wordWrap='CJK'
        ),
        'h2': ParagraphStyle(
            'H2', fontName=cjk_font, fontSize=16, leading=22,
            textColor=ACCENT_COLOR, spaceBefore=18, spaceAfter=8, wordWrap='CJK'
        ),
        'body': ParagraphStyle(
            'Body', fontName=cjk_font, fontSize=11, leading=18,
            textColor=HexColor('#2d3748'), spaceBefore=0, spaceAfter=10,
            firstLineIndent=0, wordWrap='CJK'
        ),
        'caption': ParagraphStyle(
            'Caption', fontName=cjk_font, fontSize=9, leading=12,
            textColor=HexColor('#718096'), alignment=1, spaceBefore=6, spaceAfter=12, wordWrap='CJK'
        ),
    }

# 用法
styles = get_professional_styles('CJKFont')
story.append(Paragraph("标题 Title", styles['title']))
story.append(Paragraph("第一章 Chapter 1", styles['h1']))
story.append(Paragraph("正文内容...", styles['body']))
```

#### 专业表格样式

```python
from reportlab.lib.colors import HexColor
from reportlab.platypus import Table, LongTable
from reportlab.lib import colors

def create_styled_table(data, col_widths=None, is_large=False):
    """创建专业样式的表格"""
    TableClass = LongTable if is_large else Table
    table = TableClass(data, colWidths=col_widths, repeatRows=1 if is_large else 0)

    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'CJKFont'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f7fafc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f7fafc'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
    ])
    return table
```

#### 行内文本格式

在 Paragraph 内使用类 HTML 标签实现富文本：

```python
from reportlab.platypus import Paragraph

text = """
<b>粗体 Bold</b>, <i>斜体 Italic</i>, <u>下划线 Underline</u>
<font color="#2b6cb0">蓝色文字 Blue text</font>
<font size="14">大字号 Larger</font>, <font size="9">小字号 Smaller</font>
化学式: H<sub>2</sub>O, 数学: E=mc<sup>2</sup>
<br/>换行 Line break
"""
story.append(Paragraph(text, styles['body']))
```

| 标签                 | 效果     |
| -------------------- | -------- |
| `<b>`                | **粗体** |
| `<i>`                | _斜体_   |
| `<u>`                | 下划线   |
| `<font color="...">` | 颜色     |
| `<font size="...">`  | 字号     |
| `<sub>`              | 下标     |
| `<sup>`              | 上标     |
| `<br/>`              | 换行     |

#### 文本对齐

```python
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle

left_style = ParagraphStyle('Left', alignment=TA_LEFT)
center_style = ParagraphStyle('Center', alignment=TA_CENTER)
right_style = ParagraphStyle('Right', alignment=TA_RIGHT)
justify_style = ParagraphStyle('Justify', alignment=TA_JUSTIFY)
```

#### 彩色分隔线

在标题和章节标题下添加装饰性分隔线，以增强视觉层次：

```python
from reportlab.platypus import Flowable
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch

class ColoredDivider(Flowable):
    """彩色水平分隔线"""
    def __init__(self, width, height=2, color=HexColor('#2b6cb0'), space_before=6, space_after=12):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.spaceAfter = space_after
        self.spaceBefore = space_before

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

# 预定义分隔线
CONTENT_WIDTH = 6.5 * inch

def title_divider():
    """文档标题下的宽强调分隔线"""
    return ColoredDivider(CONTENT_WIDTH, height=3, color=HexColor('#2b6cb0'), space_after=20)

def h1_divider():
    """H1 标题下的中等分隔线"""
    return ColoredDivider(CONTENT_WIDTH * 0.3, height=2, color=HexColor('#2b6cb0'), space_after=12)

def subtle_divider():
    """章节间的细灰色分隔线"""
    return ColoredDivider(CONTENT_WIDTH, height=1, color=HexColor('#e2e8f0'), space_after=10)

# 在 story 中的用法
story.append(Paragraph("报告标题 Report Title", styles['title']))
story.append(title_divider())  # 标题下的强调线

story.append(Paragraph("第一章 Chapter 1", styles['h1']))
story.append(h1_divider())  # H1 下的短强调线

story.append(Paragraph("正文内容...", styles['body']))
story.append(subtle_divider())  # 章节间的细微分隔
```

#### 带正确边距的文档设置

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate

doc = SimpleDocTemplate(
    "report.pdf",
    pagesize=letter,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch,
)
```

#### 分页最佳实践（重要）

**核心原则**：让内容自然流动。尽量减少 `PageBreak` 和 `KeepTogether` 的使用。

| 内容        | 添加方式                              | KeepTogether？ | PageBreak？  |
| ----------- | ------------------------------------- | -------------- | ------------ |
| 封面        | `story.append()` + 之后 `PageBreak()` | 否             | **仅封面后** |
| **标题**    | 直接 `story.append()`                 | **否**         | **否**       |
| **段落**    | 直接 `story.append()`                 | **否**         | **否**       |
| 图片 + 说明 | `KeepTogether([Image, Paragraph])`    | 是             | 否           |
| 小表格      | `KeepTogether([Table])`               | 是             | 否           |
| 大表格      | `LongTable(..., repeatRows=1)`        | 否             | 否           |

**⚠️ 常见错误 #1 - 过多 PageBreak：**

```python
# 错误：切勿在章节/小节前添加 PageBreak！
story.append(PageBreak())  # 会造成大片空白！
story.append(Paragraph("Chapter 2", heading_style))

# 正确：直接添加标题，让内容自然流动
story.append(Paragraph("Chapter 2", heading_style))
```

**规则：仅封面后使用一次 PageBreak。其他任何地方都不要使用 PageBreak！**

**⚠️ 常见错误 #2 - 对标题/段落使用 KeepTogether：**

```python
# 错误：会造成半页空白！
story.append(KeepTogether([
    Paragraph("Chapter 2", heading_style),
    Paragraph("Long content...", body_style),
]))

# 正确：直接添加，让内容自然流动和分割
story.append(Paragraph("Chapter 2", heading_style))
story.append(Paragraph("Long content...", body_style))
```

**完整示例：**

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether

# 1. 先注册 CJK 字体（使用上文的 register_cjk_font()）
register_cjk_font()

# 2. 设置带正确边距的文档
doc = SimpleDocTemplate("report.pdf", pagesize=letter,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch)

# 3. 使用专业样式（使用上文的 get_professional_styles()）
styles = get_professional_styles('CJKFont')

story = []

# 封面 - 仅在此处使用 PageBreak
story.append(Spacer(1, 2*inch))
story.append(Paragraph("报告标题 Report Title", styles['title']))
story.append(Paragraph("副标题 Subtitle", styles['subtitle']))
story.append(PageBreak())

# 标题和段落 - 直接添加（不要 KeepTogether，不要 PageBreak）
story.append(Paragraph("第一章 Introduction", styles['h1']))
story.append(Paragraph("正文内容自然流动，可跨页分割...", styles['body']))
story.append(Paragraph("1.1 背景 Background", styles['h2']))
story.append(Paragraph("更多内容...", styles['body']))

# 图片 - 使用 KeepTogether
story.append(KeepTogether([
    Image("fig.png", width=400, height=300),
    Paragraph("图 1: 说明文字", styles['caption'])
]))

# 表格 - 使用上文的 create_styled_table()
story.append(KeepTogether([create_styled_table(small_data)]))

doc.build(story)
```

### matplotlib - 带 CJK 支持的图表

创建包含中文文本的 matplotlib 图表时，必须配置字体：

```python
import os
import platform
import matplotlib.pyplot as plt
import matplotlib

def setup_matplotlib_cjk():
    """配置 matplotlib 以支持 CJK 字符"""
    system = platform.system()

    if system == "Darwin":  # macOS
        font_names = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'STHeiti']
    elif system == "Windows":
        font_names = ['Microsoft YaHei', 'SimHei', 'SimSun']
    else:  # Linux
        font_names = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'Droid Sans Fallback']

    # 查找可用字体
    available_fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    for font_name in font_names:
        if font_name in available_fonts:
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False  # 修复减号显示
            return font_name
    return None

# 创建图表前先设置 CJK 字体
cjk_font = setup_matplotlib_cjk()

# 创建带中文标签的柱状图
categories = ['第一季度', '第二季度', '第三季度', '第四季度']
values = [120, 135, 142, 158]

plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='steelblue')
plt.title('季度销售数据 Quarterly Sales', fontsize=16)
plt.xlabel('季度 Quarter', fontsize=12)
plt.ylabel('销售额 Sales', fontsize=12)
plt.tight_layout()
plt.savefig('chart.png', dpi=150)
plt.close()
```

#### 在 PDF 中嵌入 matplotlib 图表

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

# 先创建并保存图表（见上文）
# 然后嵌入 PDF

doc = SimpleDocTemplate("report_with_chart.pdf", pagesize=letter)
story = []

# 添加标题
cjk_style = ParagraphStyle('CJKStyle', fontName='CJKFont', fontSize=14, wordWrap='CJK')
story.append(Paragraph("销售报告 Sales Report", cjk_style))
story.append(Spacer(1, 20))

# 添加图表图片
chart_img = Image('chart.png', width=400, height=240)
story.append(chart_img)
story.append(Spacer(1, 20))

# 添加描述
story.append(Paragraph("图表显示了四个季度的销售数据变化趋势。", cjk_style))

doc.build(story)
```

## 命令行工具

### pdftotext (poppler-utils)

```bash
# 提取文字
pdftotext input.pdf output.txt

# 提取文字并保留布局
pdftotext -layout input.pdf output.txt

# 提取指定页
pdftotext -f 1 -l 5 input.pdf output.txt  # 第 1-5 页
```

### qpdf

```bash
# 合并 PDF
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# 拆分页面
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# 旋转页面
qpdf input.pdf output.pdf --rotate=+90:1  # 将第 1 页旋转 90 度

# 移除密码
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk（如果可用）

```bash
# 合并
pdftk file1.pdf file2.pdf cat output merged.pdf

# 拆分
pdftk input.pdf burst

# 旋转
pdftk input.pdf rotate 1east output rotated.pdf
```

## 常见任务

### 从扫描版 PDF 提取文字

```python
# 需要：pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# 将 PDF 转为图片
images = convert_from_path('scanned.pdf')

# 对每页进行 OCR
text = ""
for i, image in enumerate(images):
    text += f"第 {i+1} 页：\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### 添加水印

```python
from pypdf import PdfReader, PdfWriter

# 创建水印（或加载现有水印）
watermark = PdfReader("watermark.pdf").pages[0]

# 应用到所有页面
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 提取图片

```bash
# 使用 pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# 这会提取所有图片为 output_prefix-000.jpg, output_prefix-001.jpg 等
```

### 密码保护

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# 添加密码
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## 快速参考

| 任务            | 最佳工具                                                                | 命令/代码                                                           |
| --------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 合并 PDF        | pypdf                                                                   | `writer.add_page(page)`                                             |
| 拆分 PDF        | pypdf                                                                   | 每页一个文件                                                        |
| 提取文字        | pdfplumber                                                              | `page.extract_text()`                                               |
| 提取表格        | pdfplumber                                                              | `page.extract_tables()`                                             |
| 提取长 PDF 页面 | `scripts/extract_pages.py`                                              | `python3 scripts/extract_pages.py input.pdf extracted`              |
| 检索已提取文件  | `scripts/search_extracted.sh`（Windows：`scripts/search_extracted.py`） | `bash scripts/search_extracted.sh extracted "long query" [--regex]` |
| 创建 PDF        | reportlab                                                               | Canvas 或 Platypus                                                  |
| 命令行合并      | qpdf                                                                    | `qpdf --empty --pages ...`                                          |
| 扫描版 PDF OCR  | pytesseract                                                             | 先转为图片                                                          |
| 填写 PDF 表单   | pdf-lib 或 pypdf（见 FORMS.md）                                         | 见 FORMS.md                                                         |

## 后续步骤

- 如需高级 pypdfium2 用法，见 REFERENCE.md
- 如需 JavaScript 库（pdf-lib），见 REFERENCE.md
- 如需填写 PDF 表单，按 FORMS.md 的说明操作
- 如需故障排除指南，见 REFERENCE.md
