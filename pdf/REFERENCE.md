# PDF 处理高级参考

本文档包含主技能说明中未涵盖的高级 PDF 处理功能、详细示例和附加库。

## pypdfium2 库（Apache/BSD 许可证）

### 概述

pypdfium2 是 PDFium（Chromium 的 PDF 库）的 Python 绑定。适用于快速 PDF 渲染、图片生成，可作为 PyMuPDF 的替代。

### 将 PDF 渲染为图片

```python
import pypdfium2 as pdfium
from PIL import Image

# 加载 PDF
pdf = pdfium.PdfDocument("document.pdf")

# 将页面渲染为图片
page = pdf[0]  # 第一页
bitmap = page.render(
    scale=2.0,  # 更高分辨率
    rotation=0  # 不旋转
)

# 转为 PIL 图片
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# 处理多页
for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

### 使用 pypdfium2 提取文本

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"第 {i+1} 页文本长度：{len(text)} 字符")
```

## JavaScript 库

### pdf-lib（MIT 许可证）

pdf-lib 是一个功能强大的 JavaScript 库，可在任何 JavaScript 环境中创建和修改 PDF 文档。

#### 加载并操作现有 PDF

```javascript
import { PDFDocument } from "pdf-lib";
import fs from "fs";

async function manipulatePDF() {
  // 加载现有 PDF
  const existingPdfBytes = fs.readFileSync("input.pdf");
  const pdfDoc = await PDFDocument.load(existingPdfBytes);

  // 获取页数
  const pageCount = pdfDoc.getPageCount();
  console.log(`文档共 ${pageCount} 页`);

  // 添加新页面
  const newPage = pdfDoc.addPage([600, 400]);
  newPage.drawText("Added by pdf-lib", {
    x: 100,
    y: 300,
    size: 16,
  });

  // 保存修改后的 PDF
  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync("modified.pdf", pdfBytes);
}
```

#### 从零创建复杂 PDF

```javascript
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";
import fs from "fs";

async function createPDF() {
  const pdfDoc = await PDFDocument.create();

  // 添加字体
  const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  // 添加页面
  const page = pdfDoc.addPage([595, 842]); // A4 尺寸
  const { width, height } = page.getSize();

  // 添加带样式的文本
  page.drawText("Invoice #12345", {
    x: 50,
    y: height - 50,
    size: 18,
    font: helveticaBold,
    color: rgb(0.2, 0.2, 0.8),
  });

  // 添加矩形（标题背景）
  page.drawRectangle({
    x: 40,
    y: height - 100,
    width: width - 80,
    height: 30,
    color: rgb(0.9, 0.9, 0.9),
  });

  // 添加表格状内容
  const items = [
    ["Item", "Qty", "Price", "Total"],
    ["Widget", "2", "$50", "$100"],
    ["Gadget", "1", "$75", "$75"],
  ];

  let yPos = height - 150;
  items.forEach((row) => {
    let xPos = 50;
    row.forEach((cell) => {
      page.drawText(cell, {
        x: xPos,
        y: yPos,
        size: 12,
        font: helveticaFont,
      });
      xPos += 120;
    });
    yPos -= 25;
  });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync("created.pdf", pdfBytes);
}
```

#### 高级合并和拆分操作

```javascript
import { PDFDocument } from "pdf-lib";
import fs from "fs";

async function mergePDFs() {
  // 创建新文档
  const mergedPdf = await PDFDocument.create();

  // 加载源 PDF
  const pdf1Bytes = fs.readFileSync("doc1.pdf");
  const pdf2Bytes = fs.readFileSync("doc2.pdf");

  const pdf1 = await PDFDocument.load(pdf1Bytes);
  const pdf2 = await PDFDocument.load(pdf2Bytes);

  // 从第一个 PDF 复制页面
  const pdf1Pages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices());
  pdf1Pages.forEach((page) => mergedPdf.addPage(page));

  // 从第二个 PDF 复制特定页面（第 0、2、4 页）
  const pdf2Pages = await mergedPdf.copyPages(pdf2, [0, 2, 4]);
  pdf2Pages.forEach((page) => mergedPdf.addPage(page));

  const mergedPdfBytes = await mergedPdf.save();
  fs.writeFileSync("merged.pdf", mergedPdfBytes);
}
```

### pdfjs-dist（Apache 许可证）

PDF.js 是 Mozilla 的 JavaScript 库，用于在浏览器中渲染 PDF。

#### 基本 PDF 加载和渲染

```javascript
import * as pdfjsLib from "pdfjs-dist";

// 配置 worker（对性能很重要）
pdfjsLib.GlobalWorkerOptions.workerSrc = "./pdf.worker.js";

async function renderPDF() {
  // 加载 PDF
  const loadingTask = pdfjsLib.getDocument("document.pdf");
  const pdf = await loadingTask.promise;

  console.log(`已加载 ${pdf.numPages} 页的 PDF`);

  // 获取第一页
  const page = await pdf.getPage(1);
  const viewport = page.getViewport({ scale: 1.5 });

  // 渲染到 canvas
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  canvas.height = viewport.height;
  canvas.width = viewport.width;

  const renderContext = {
    canvasContext: context,
    viewport: viewport,
  };

  await page.render(renderContext).promise;
  document.body.appendChild(canvas);
}
```

#### 提取带坐标的文本

```javascript
import * as pdfjsLib from "pdfjs-dist";

async function extractText() {
  const loadingTask = pdfjsLib.getDocument("document.pdf");
  const pdf = await loadingTask.promise;

  let fullText = "";

  // 从所有页面提取文本
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const textContent = await page.getTextContent();

    const pageText = textContent.items.map((item) => item.str).join(" ");

    fullText += `\n--- 第 ${i} 页 ---\n${pageText}`;

    // 获取带坐标的文本用于高级处理
    const textWithCoords = textContent.items.map((item) => ({
      text: item.str,
      x: item.transform[4],
      y: item.transform[5],
      width: item.width,
      height: item.height,
    }));
  }

  console.log(fullText);
  return fullText;
}
```

#### 提取注释和表单

```javascript
import * as pdfjsLib from "pdfjs-dist";

async function extractAnnotations() {
  const loadingTask = pdfjsLib.getDocument("annotated.pdf");
  const pdf = await loadingTask.promise;

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const annotations = await page.getAnnotations();

    annotations.forEach((annotation) => {
      console.log(`注释类型: ${annotation.subtype}`);
      console.log(`内容: ${annotation.contents}`);
      console.log(`坐标: ${JSON.stringify(annotation.rect)}`);
    });
  }
}
```

## 高级命令行操作

### poppler-utils 高级功能

#### 提取带边界框坐标的文本

```bash
# 提取带边界框坐标的文本（对结构化数据至关重要）
pdftotext -bbox-layout document.pdf output.xml

# XML 输出包含每个文本元素的精确坐标
```

#### 高级图片转换

```bash
# 以指定分辨率转为 PNG 图片
pdftoppm -png -r 300 document.pdf output_prefix

# 以高分辨率转换指定页范围
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res_pages

# 转为 JPEG 并设置质量
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

#### 提取嵌入的图片

```bash
# 提取所有嵌入图片（含元数据）
pdfimages -j -p document.pdf page_images

# 仅列出图片信息（不提取）
pdfimages -list document.pdf

# 以原始格式提取图片
pdfimages -all document.pdf images/img
```

### qpdf 高级功能

#### 复杂页面操作

```bash
# 将 PDF 按每组页数拆分
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# 用复杂范围提取特定页面
qpdf input.pdf --pages input.pdf 1,3-5,8,10-end -- extracted.pdf

# 从多个 PDF 合并特定页面
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 doc3.pdf 2,4 -- combined.pdf
```

#### PDF 优化和修复

```bash
# 为 Web 优化 PDF（线性化以支持流式传输）
qpdf --linearize input.pdf optimized.pdf

# 移除未使用对象并压缩
qpdf --optimize-level=all input.pdf compressed.pdf

# 尝试修复损坏的 PDF 结构
qpdf --check input.pdf
qpdf --fix-qdf damaged.pdf repaired.pdf

# 显示详细 PDF 结构用于调试
qpdf --show-all-pages input.pdf > structure.txt
```

#### 高级加密

```bash
# 添加带特定权限的密码保护
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf

# 检查加密状态
qpdf --show-encryption encrypted.pdf

# 移除密码保护（需要密码）
qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf
```

## 高级 Python 技术

### pdfplumber 高级功能

#### 提取带精确坐标的文本

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # 提取所有带坐标的文本
    chars = page.chars
    for char in chars[:10]:  # 前 10 个字符
        print(f"字符: '{char['text']}' 位于 x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # 按边界框提取文本（left, top, right, bottom）
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

#### 使用自定义设置进行高级表格提取

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]

    # 使用自定义设置提取复杂布局的表格
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    # 表格提取的可视化调试
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### reportlab 高级功能

#### 高级分页控制

创建多页文档时，正确的分页可防止过多空白：

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, LongTable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * inch

doc = SimpleDocTemplate(
    "document.pdf",
    pagesize=letter,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=MARGIN
)

styles = getSampleStyleSheet()
story = []

# --- 封面（独立页）---
cover_title_style = ParagraphStyle(
    'CoverTitle',
    parent=styles['Title'],
    fontSize=36,
    spaceAfter=30,
)
story.append(Spacer(1, 2 * inch))
story.append(Paragraph("Document Title", cover_title_style))
story.append(Paragraph("Subtitle or Author", styles['Normal']))
story.append(PageBreak())

# --- 正文内容（自然流动，可跨页分割）---
heading_style = ParagraphStyle(
    'Heading',
    parent=styles['Heading1'],
    spaceBefore=12,
    spaceAfter=6,
)
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=11,
    leading=14,
    spaceBefore=6,
    spaceAfter=6,
    wordWrap='CJK',
)

story.append(Paragraph("Chapter 1: Introduction", heading_style))
story.append(Paragraph("This is body text that can flow naturally across pages. "
                       "Long paragraphs will automatically split at page boundaries. "
                       "This maximizes page utilization and avoids blank space.", body_style))

# --- 图片带说明（保持在一起，不分割）---
def add_figure(story, image_path, caption, width=4*inch):
    caption_style = ParagraphStyle('Caption', parent=styles['Normal'], fontSize=9, alignment=1)
    img = Image(image_path, width=width, height=width*0.75)
    story.append(KeepTogether([
        img,
        Spacer(1, 6),
        Paragraph(caption, caption_style)
    ]))

# add_figure(story, "chart.png", "Figure 1: Sales Chart")

# --- 小表格（保持在一起）---
def add_small_table(story, data, col_widths):
    table = Table(data, colWidths=col_widths)
    table.setStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, 'black'),
        ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
    ])
    story.append(KeepTogether([table]))

# --- 大表格（按行分割，重复表头）---
def add_large_table(story, data, col_widths):
    table = LongTable(data, colWidths=col_widths, repeatRows=1)
    table.splitByRow = True
    table.setStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, 'black'),
        ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
    ])
    story.append(table)

doc.build(story)
```

#### 创建带表格的专业报告（含 CJK 支持）

```python
import os
import platform
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 为非 ASCII 文本支持注册 CJK 字体
def register_cjk_font():
    system = platform.system()
    if system == "Darwin":
        paths = ["/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/STHeiti Medium.ttc"]
    elif system == "Windows":
        paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"]
    else:
        paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for p in paths:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont("CJKFont", p, subfontIndex=0))
            return "CJKFont"
    return "Helvetica"

cjk_font = register_cjk_font()

# 含中文的示例数据
data = [
    ['产品 Product', '第一季度 Q1', '第二季度 Q2', '第三季度 Q3', '第四季度 Q4'],
    ['部件 Widgets', '120', '135', '142', '158'],
    ['设备 Gadgets', '85', '92', '98', '105']
]

# 创建带表格的 PDF
doc = SimpleDocTemplate("report.pdf")
elements = []

# 添加带 CJK 支持的标题
styles = getSampleStyleSheet()
cjk_title_style = ParagraphStyle('CJKTitle', parent=styles['Title'], fontName=cjk_font)
title = Paragraph("季度销售报告 Quarterly Sales Report", cjk_title_style)
elements.append(title)

# 添加带高级样式的表格（使用 CJK 字体）
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), cjk_font),  # 所有单元格使用 CJK 字体
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)

doc.build(elements)
```

#### 带 CJK 支持的 matplotlib 图表

创建用于嵌入 PDF 的 matplotlib 图表时：

```python
import os
import platform
import matplotlib.pyplot as plt
import matplotlib

def setup_matplotlib_cjk():
    """配置 matplotlib 以在图表中支持 CJK 字符"""
    system = platform.system()
    if system == "Darwin":
        font_names = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'STHeiti']
    elif system == "Windows":
        font_names = ['Microsoft YaHei', 'SimHei', 'SimSun']
    else:
        font_names = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'Droid Sans Fallback']

    available_fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    for font_name in font_names:
        if font_name in available_fonts:
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            return font_name
    return None

# 创建任何图表前先设置
cjk_font = setup_matplotlib_cjk()

# 创建带中文标签的饼图
labels = ['研发 R&D', '市场 Marketing', '运营 Operations', '销售 Sales']
sizes = [30, 25, 20, 25]
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('部门预算分配 Budget Allocation', fontsize=16)
plt.axis('equal')
plt.tight_layout()
plt.savefig('pie_chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

#### 带 CJK 换行的长文本

对于需要正确换行的长中文文本：

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

# 重要：设置 wordWrap='CJK' 以实现正确的中文换行
cjk_paragraph_style = ParagraphStyle(
    'CJKParagraph',
    fontName='CJKFont',
    fontSize=12,
    leading=18,
    wordWrap='CJK',  # 对中文文本换行至关重要
)

doc = SimpleDocTemplate("long_text.pdf")
story = []

long_chinese_text = """
这是一段很长的中文文本，用于演示中文换行功能。在没有设置 wordWrap='CJK' 的情况下，
reportlab 默认使用英文换行规则，只在空格处换行。但中文句子通常没有空格，
因此需要特别设置 CJK 换行模式，才能让文本在适当的位置自动换行。
"""
story.append(Paragraph(long_chinese_text, cjk_paragraph_style))

doc.build(story)
```

## 复杂工作流

### 从 PDF 提取图形/图片

#### 方法 1：使用 pdfimages（最快）

```bash
# 以原始质量提取所有图片
pdfimages -all document.pdf images/img
```

#### 方法 2：使用 pypdfium2 + 图像处理

```python
import pypdfium2 as pdfium
from PIL import Image
import numpy as np

def extract_figures(pdf_path, output_dir):
    pdf = pdfium.PdfDocument(pdf_path)

    for page_num, page in enumerate(pdf):
        # 渲染高分辨率页面
        bitmap = page.render(scale=3.0)
        img = bitmap.to_pil()

        # 转为 numpy 以便处理
        img_array = np.array(img)

        # 简单图形检测（非白色区域）
        mask = np.any(img_array != [255, 255, 255], axis=2)

        # 查找轮廓并提取边界框
        # （此处为简化版 - 实际实现需要更复杂的检测）

        # 保存检测到的图形
        # ... 实现取决于具体需求
```

### 带错误处理的批量 PDF 处理

```python
import os
import glob
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_pdfs(input_dir, operation='merge'):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    if operation == 'merge':
        writer = PdfWriter()
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"已处理: {pdf_file}")
            except Exception as e:
                logger.error(f"处理 {pdf_file} 失败: {e}")
                continue

        with open("batch_merged.pdf", "wb") as output:
            writer.write(output)

    elif operation == 'extract_text':
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                output_file = pdf_file.replace('.pdf', '.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"已从 {pdf_file} 提取文本")

            except Exception as e:
                logger.error(f"从 {pdf_file} 提取文本失败: {e}")
                continue
```

### 高级 PDF 裁剪

```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("input.pdf")
writer = PdfWriter()

# 裁剪页面（left, bottom, right, top，单位为点）
page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

writer.add_page(page)
with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

## 性能优化技巧

### 1. 大型 PDF

- 使用流式处理而非将整个 PDF 加载到内存
- 使用 `qpdf --split-pages` 拆分大文件
- 用 pypdfium2 逐页处理

### 2. 文本提取

- `pdftotext -bbox-layout` 是纯文本提取最快的
- 使用 pdfplumber 处理结构化数据和表格
- 对超大文档避免使用 `pypdf.extract_text()`

### 3. 图片提取

- `pdfimages` 比渲染页面快得多
- 预览用低分辨率，最终输出用高分辨率

### 4. 表单填写

- pdf-lib 比大多数替代方案更好地保持表单结构
- 处理前预验证表单字段

### 5. 内存管理

```python
# 分块处理 PDF
def process_large_pdf(pdf_path, chunk_size=10):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for start_idx in range(0, total_pages, chunk_size):
        end_idx = min(start_idx + chunk_size, total_pages)
        writer = PdfWriter()

        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])

        # 处理分块
        with open(f"chunk_{start_idx//chunk_size}.pdf", "wb") as output:
            writer.write(output)
```

## 常见问题故障排除

### 加密 PDF

```python
# 处理受密码保护的 PDF
from pypdf import PdfReader

try:
    reader = PdfReader("encrypted.pdf")
    if reader.is_encrypted:
        reader.decrypt("password")
except Exception as e:
    print(f"解密失败: {e}")
```

### 损坏的 PDF

```bash
# 使用 qpdf 修复
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### 文本提取问题

```python
# 对扫描版 PDF 回退到 OCR
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image)
    return text
```

## 许可证信息

- **pypdf**：BSD 许可证
- **pdfplumber**：MIT 许可证
- **pypdfium2**：Apache/BSD 许可证
- **reportlab**：BSD 许可证
- **poppler-utils**：GPL-2 许可证
- **qpdf**：Apache 许可证
- **pdf-lib**：MIT 许可证
- **pdfjs-dist**：Apache 许可证
