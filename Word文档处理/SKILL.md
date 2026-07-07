---
name: Word文档处理
description: >
  创建、读取、编辑和操作 Word 文档（.docx）。支持快速路径（python-docx 常规中文办公文档）与高级路径（docx-js / XML
  解包编辑，处理修订、批注、复杂格式）。 触发场景：创建 Word 文档、读取
  docx、编辑文档、生成报告/备忘录/信函、处理修订批注、文档排版。
  当用户说"写文档"、"创建文档"、"word"、"docx"、"写报告"、"编辑文档"、"文档排版"、"tracked
  changes"、"comments"、"批注"、"修订"时触发此技能。
license: Proprietary. LICENSE.txt has complete terms
---

# Word 文档处理

## 适用场景

- 创建、读取、编辑 Word 文档（.docx）
- 生成带格式的专业文档（目录、页眉页脚、页码）
- 插入/替换图片、表格
- 查找替换、处理修订和批注
- 将内容转换为精美的 Word 文档

## 两条路径

| 需求                                  | 推荐路径 | 核心工具                  |
| ------------------------------------- | -------- | ------------------------- |
| 常规中文办公文档创建/编辑             | 快速路径 | python-docx               |
| 修订、批注、复杂 XML 编辑、保留原格式 | 高级路径 | docx-js + XML unpack/pack |

---

## 快速路径：python-docx

适合中文办公文档的常规创建与编辑。

### 技术栈

| 库          | 用途             |
| ----------- | ---------------- |
| python-docx | 创建和修改 .docx |
| docx2python | 提取文本和表格   |
| lxml        | 高级 XML 操作    |

### 创建与读取

```python
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
doc.add_heading('标题', level=1)
p = doc.add_paragraph('正文内容')
doc.save('output.docx')

# 读取
doc = Document('input.docx')
for para in doc.paragraphs:
    print(para.text)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

### 常用格式化

| 功能 | 方法                                         |
| ---- | -------------------------------------------- |
| 标题 | `doc.add_heading(text, level=1-9)`           |
| 加粗 | `run.bold = True`                            |
| 斜体 | `run.italic = True`                          |
| 字号 | `run.font.size = Pt(12)`                     |
| 字体 | `run.font.name = 'SimSun'`                   |
| 对齐 | `para.alignment = WD_ALIGN_PARAGRAPH.CENTER` |
| 分页 | `doc.add_page_break()`                       |
| 表格 | `doc.add_table(rows, cols)`                  |
| 图片 | `doc.add_image(path, width=Inches(6))`       |

### 中文字体支持

```python
from docx.oxml.ns import qn

run = para.add_run('中文文本')
run.font.name = 'Times New Roman'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
```

### 常见文档类型

| 类型   | 关键特征                 |
| ------ | ------------------------ |
| 报告   | 封面、目录、标题、页码   |
| 信函   | 信头、日期、称呼、签名   |
| 备忘录 | 头部信息块、正文、行动项 |
| 模板   | 占位符、统一样式         |

### 工作流

1. 理解需求：文档类型、内容、格式要求
2. 设计结构：章节、标题、表格
3. 编写代码：使用 python-docx
4. 格式化：样式、字体、对齐、间距
5. 验证：在 Word/LibreOffice 中打开检查
6. 交付：保存到指定路径

### 约束

- python-docx 读取模板现有样式能力有限，需充分测试
- 复杂布局（分栏、文本框）可能需要直接 XML 操作
- 中文字体需显式设置 `eastAsia` 字体
- 页码需要节/页脚 XML 操作
- 修订和批注 API 支持有限（转高级路径）

---

## 高级路径：docx-js + XML 解包编辑

适合 tracked changes、comments、复杂 XML 编辑以及保留原格式。

### .docx 结构

.docx 是 ZIP 压缩包，内部为 XML 文件。

### 快速参考

| 任务          | 方法                                                                                           |
| ------------- | ---------------------------------------------------------------------------------------------- |
| 读取/分析内容 | `pandoc --track-changes=all document.docx -o output.md`                                        |
| 创建新文档    | docx-js（见下文）                                                                              |
| 编辑现有文档  | unpack → 编辑 XML → repack（见下文）                                                           |
| .doc 转 .docx | `soffice --headless --convert-to docx document.doc`                                            |
| 接受所有修订  | `python scripts/accept_changes.py input.docx output.docx`                                      |
| 转为图片      | `soffice --headless --convert-to pdf document.docx && pdftoppm -jpeg -r 150 document.pdf page` |

### 新建文档（docx-js）

安装：`npm install docx`

**⚠️ 关键：docx-js 中使用 JavaScript 转义（`\"`），绝不要使用 XML 实体（`&#x201C;`），否则会显示为乱码。**

#### 基础模板

```javascript
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  Header,
  Footer,
  AlignmentType,
  LevelFormat,
  PageNumber,
  PageBreak,
  HeadingLevel,
  BorderStyle,
  WidthType,
  ShadingType,
} = require("docx");

// 只使用一个 section，避免空白页
const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // US Letter，DXA
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [/* 所有内容放这里 */],
    },
  ],
});
Packer.toBuffer(doc).then((buffer) => fs.writeFileSync("doc.docx", buffer));
```

#### CJK 字体配置

```javascript
const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" },
          size: 24,
        },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0, keepNext: false, keepLines: false },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1, keepNext: false, keepLines: false },
      },
    ],
  },
  sections: [{ children: [new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("标题 Title")] })] }],
});
```

#### 特殊字符

| 需要输出 | ✅ 正确（JavaScript） | ❌ 错误（XML 实体）  |
| -------- | --------------------- | -------------------- |
| 双引号   | `\"`                  | `&#x201C;` / `&#34;` |
| 单引号   | `\'`                  | `&#x2019;` / `&#39;` |
| &        | `&`                   | `&amp;`              |
| <        | `<`                   | `&lt;`               |

#### 列表（不要使用 Unicode 项目符号）

```javascript
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbers",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      children: [
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("项目符号")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("编号项")] }),
      ],
    },
  ],
});
```

#### 表格

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  columnWidths: [4680, 4680],
  rows: [
    new TableRow({
      cantSplit: true, // 防止行跨页断开
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, // CLEAR，不要 SOLID
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun("单元格")] })],
        }),
      ],
    }),
  ],
});
```

#### 图片

```javascript
new Paragraph({
  children: [
    new ImageRun({
      type: "png", // 必须：png/jpg/jpeg/gif/bmp/svg
      data: fs.readFileSync("image.png"),
      transformation: { width: 200, height: 150 },
      altText: { title: "Title", description: "Desc", name: "Name" },
    }),
  ],
});
```

#### 分页与页眉页脚

```javascript
// 分页符必须放在 Paragraph 内
new Paragraph({ children: [new PageBreak()] });

// 页眉页脚
sections: [
  {
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: {
      default: new Header({ children: [new Paragraph({ children: [new TextRun("页眉")] })] }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })],
          }),
        ],
      }),
    },
    children: [/* content */],
  },
];
```

#### docx-js 关键规则

- 只使用 **一个 section**，所有内容放在 `children` 数组中；多个 section 会产生空白页
- 显式设置页面大小（docx-js 默认 A4）
- CJK 文档必须配置 `eastAsia` 字体
- 引号使用 JavaScript 转义，不要使用 XML 实体
- 不要使用 `\n`，使用独立 Paragraph
- 不要使用 Unicode 项目符号，使用 `LevelFormat.BULLET`
- `PageBreak` 必须放在 Paragraph 内
- `ImageRun` 必须指定 `type`
- 表格必须设置 `width` 和 `columnWidths`，且两者匹配
- 表格行设置 `cantSplit: true`
- 表头底纹使用 `ShadingType.CLEAR`，不要 `SOLID`
- 标题样式设置 `keepNext: false`、`keepLines: false`，避免底部大片空白
- 不要生成目录页

### 编辑现有文档（XML unpack/pack）

**此流程操作的是原始 XML，XML 实体（`&#x201C;`）仅在此处有效。**

#### 步骤 1：解包

```bash
python scripts/unpack.py document.docx unpacked/
```

解包会美化 XML、合并相邻 run、将智能引号转为 XML 实体。

#### 步骤 2：编辑 XML

直接编辑 `unpacked/word/` 下 XML，使用 Edit 工具做字符串替换。

- 作者默认使用 `"AI Assistant"`，除非用户另有要求
- 新增内容的引号和撇号使用 XML 实体：
  - `&#x2018;` / `&#x2019;`（单引号）
  - `&#x201C;` / `&#x201D;`（双引号）

#### 批注辅助脚本

```bash
python scripts/comment.py unpacked/ 0 "批注文本（含 &amp; 和 &#x2019;）"
python scripts/comment.py unpacked/ 1 "回复文本" --parent 0
python scripts/comment.py unpacked/ 0 "文本" --author "Custom Author"
```

然后在 `document.xml` 中添加标记（见下方 XML 参考）。

#### 步骤 3：打包

```bash
python scripts/pack.py unpacked/ output.docx --original document.docx
```

打包会自动修复部分问题（如 `durableId` 越界、缺失 `xml:space="preserve"`）。

### XML 参考

#### 修订（Tracked Changes）

```xml
<w:ins w:id="1" w:author="AI Assistant" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>插入文本</w:t></w:r>
</w:ins>

<w:del w:id="2" w:author="AI Assistant" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>删除文本</w:delText></w:r>
</w:del>
```

`<w:del>` 内使用 `<w:delText>` 替代 `<w:t>`。

只标记变更部分：

```xml
<w:r><w:t>期限是 </w:t></w:r>
<w:del w:id="1" w:author="AI Assistant" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="AI Assistant" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> 天。</w:t></w:r>
```

删除整段时，同时删除段落标记：

```xml
<w:p>
  <w:pPr>
    <w:rPr>
      <w:del w:id="1" w:author="AI Assistant" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="AI Assistant" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>要删除的整段内容...</w:delText></w:r>
  </w:del>
</w:p>
```

#### 批注（Comments）

**`<w:commentRangeStart>` 和 `<w:commentRangeEnd>` 是 `<w:r>` 的兄弟节点，不能放在 `<w:r>` 内部。**

```xml
<w:commentRangeStart w:id="0"/>
<w:del w:id="1" w:author="AI Assistant" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>删除内容</w:delText></w:r>
</w:del>
<w:r><w:t> 更多文本</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```

#### 图片

1. 图片放入 `word/media/`
2. 在 `word/_rels/document.xml.rels` 添加：

   ```xml
   <Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
   ```

3. 在 `[Content_Types].xml` 添加：

   ```xml
   <Default Extension="png" ContentType="image/png"/>
   ```

4. 在 `document.xml` 引用（EMUs：914400 = 1 英寸）

#### XML 通用规则

- `<w:pPr>` 元素顺序：`pStyle`、`numPr`、`spacing`、`ind`、`jc`、`rPr` 最后
- `<w:t>` 含前后空格时加 `xml:space="preserve"`
- RSIDs 为 8 位十六进制

### 依赖

- python-docx
- docx-js：`npm install docx`
- pandoc：文本提取
- LibreOffice：PDF 转换、接受修订
- Poppler：`pdftoppm` 转图片
