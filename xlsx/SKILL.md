---
name: xlsx
description: >
  创建、读取、编辑和分析电子表格文件（.xlsx、.xlsm、.csv、.tsv）。Use this skill any time a spreadsheet file is the
  primary input or output. 触发场景：操作 Excel、创建表格、编辑电子表格、数据清洗、格式转换、图表生成、公式模型。
  当用户说"excel"、"表格"、"xlsx"、"电子表格"、"数据表"、"csv"、"做表格"、"整理数据"、"数据清洗"、"spreadsheet"时触发此技能。交付物必须是电子表格文件。
license: Proprietary. LICENSE.txt has complete terms
---

# 电子表格处理（xlsx）

## 概述

处理 .xlsx、.xlsm、.csv、.tsv 文件的创建、读取、编辑与分析。交付物必须是电子表格文件。

## 输出要求

### 所有 Excel 文件

#### 专业字体

- 所有交付物使用一致的专业字体（如 Arial、Times New Roman），除非用户另有指示。

#### 零公式错误

- 每个 Excel 模型必须以 **零公式错误** 交付：禁止出现 `#REF!`、`#DIV/0!`、`#VALUE!`、`#N/A`、`#NAME?`。

#### 保留现有模板

- 修改文件时研究并精确匹配现有格式、样式和约定。
- 不要对已有模式的文件强加标准化格式。
- 现有模板约定始终覆盖本指南。

#### 视觉表格设计（新建表格默认要求）

- 数据区域使用斑马条纹（不含表头和合计行），低对比度交替填充（如 `#FFFFFF` 和 `#F7F9FC`）。
- 使用细浅色边框（如 `#D9DEE7`），优先外边框 + 行分隔，避免厚重满网格。
- 小计/合计行使用加粗 + 上边框强调，而不是每个单元格厚边框。

#### KPI 视觉层级（存在 KPI 类指标时）

- 根据内容复杂度突出适量关键指标，优先 summary 行、当期关键值和异常值。
- 保持一致的高亮处理（推荐加粗 + 浅填充），避免滥用饱和色。
- 颜色语义保持一致（如绿色=正向，红色=风险）。
- 必要时在关键指标旁加短标签（如 "Core KPI"、"Exception"）。

### 财务模型

#### 颜色编码标准（除非用户或模板另有要求）

| 元素                          | 颜色                    |
| ----------------------------- | ----------------------- |
| 硬编码输入 / 用户会调整的数字 | 蓝色文本 RGB(0,0,255)   |
| 所有公式和计算                | 黑色文本 RGB(0,0,0)     |
| 同一工作簿其他工作表链接      | 绿色文本 RGB(0,128,0)   |
| 外部文件链接                  | 红色文本 RGB(255,0,0)   |
| 需要注意的关键假设            | 黄色背景 RGB(255,255,0) |

#### 数字格式标准

- **年份**：格式化为文本字符串（"2024" 而非 "2,024"）。
- **货币**：使用 `$#,##0`；标题中必须标明单位（如 "Revenue ($mm)"）。
- **零值**：使用数字格式将零显示为 "-"，包括百分比（`$#,##0;($#,##0);-`）。
- **百分比**：默认 `0.0%`（一位小数）。
- **倍数**：估值倍数格式为 `0.0x`（EV/EBITDA、P/E）。
- **负数**：使用括号 `(123)`，而非 `-123`。

#### 公式构建规则

- 所有假设（增长率、利润率、倍数等）放在独立假设单元格。
- 公式中使用单元格引用，而非硬编码值。
- 示例：使用 `=B5*(1+$B$6)`，而不是 `=B5*1.05`。

#### 公式错误预防

- 验证所有单元格引用正确。
- 检查范围中的 off-by-one 错误。
- 确保所有预测期间公式一致。
- 用边界值测试（零、负数）。
- 检查是否存在意外循环引用。

#### 硬编码文档要求

- 在单元格旁标注来源，格式：`Source: [系统/文档], [日期], [具体引用], [URL]`。

## 关键：使用公式，而非硬编码值

始终使用 Excel 公式，而不是在 Python 中计算后写入硬编码结果。

### ❌ 错误

```python
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码 5000
```

### ✅ 正确

```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

此规则适用于所有计算：总计、百分比、比率、差值等。源数据变更时电子表格应能自动重算。

## 强制：构建前规划

写任何数据/公式/代码前，必须完成以下两步：

### 步骤 1：Problem Review

- 读取所有相关文件（源 Excel/CSV/TSV、模板、引用文档）。
- 结合用户查询，用具体语言重述任务意图。

### 步骤 2：输出 Detailed Workbook Plan

结构化计划必须包含：

1. **Sheet Plan**：总工作表数、每个表名、用途。
2. **Schema Plan（每表）**：行字段、列字段、每个字段的值来源/计算方式（原始 / 查找 / 公式 / 聚合）。
3. **Style Plan（每表）**：表头样式、斑马条纹设计、KPI 层级设计。

**必需输出格式：**

```markdown
## Problem Review

- Files read: ...
- Task understanding: ...

## Detailed Plan

### Sheet Plan

1. Sheet: <name> — Purpose: <purpose>

### Schema Plan

1. Sheet: <name>

- Row fields: ...
- Column fields: ...
- Value source/calculation: ...

### Style Plan

1. Sheet: <name>

- Header: ...
- Zebra striping: ...
- KPI hierarchy: ...
```

如果输入不完整，仍先输出该计划并明确标注假设。

**只有满足以下条件后才能开始实现：**

- [ ] Problem Review 完成
- [ ] Detailed Workbook Plan 已输出

## 常见工作流

1. **先输出计划（强制）**：按上述格式输出 Problem Review + Detailed Plan。
2. **选择工具**：pandas 处理数据，openpyxl 处理公式/格式。
3. **创建/加载**：新建工作簿或加载现有文件。
4. **修改**：添加/编辑数据、公式、格式。
5. **保存**：写入文件。
6. **重算公式（使用公式时强制）**：

   ```bash
   python scripts/recalc.py output.xlsx
   ```

7. **验证并修复错误**：
   - 脚本返回 JSON 格式的错误详情。
   - 若 `status` 为 `errors_found`，查看 `error_summary`。
   - 修复错误后再次重算。
   - 常见错误：
     - `#REF!`：无效单元格引用
     - `#DIV/0!`：除零
     - `#VALUE!`：公式中数据类型错误
     - `#NAME?`：无法识别的公式名称

## 读取与分析数据

### 使用 pandas 分析数据

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('file.xlsx')  # 默认第一个 sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # 所有 sheet

# 分析
df.head()
df.info()
df.describe()

# 写入 Excel
df.to_excel('output.xlsx', index=False)
```

## 创建新 Excel 文件

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# 公式
sheet['B2'] = '=SUM(A1:A10)'

# 格式
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 列宽
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

## 编辑现有 Excel 文件

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # 或 wb['SheetName']

for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)

new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## 重算公式

openpyxl 写入的公式是字符串，不会自动计算值。使用 `scripts/recalc.py`：

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

示例：

```bash
python scripts/recalc.py output.xlsx 30
```

脚本功能：

- 首次运行时自动配置 LibreOffice 宏。
- 重算所有工作表中的所有公式。
- 扫描所有单元格的 Excel 错误。
- 返回 JSON 格式的错误位置和计数。
- 支持 Linux、macOS、Windows。

## 公式验证清单

### 必要验证

- [ ] 测试 2-3 个示例引用，确认取值正确
- [ ] 确认 Excel 列映射正确（如第 64 列 = BL，而非 BK）
- [ ] 记住 Excel 行是 1 索引（DataFrame 行 5 = Excel 行 6）

### 常见陷阱

- [ ] NaN 处理：使用 `pd.notna()` 检查空值
- [ ] 最右侧列：FY 数据常在第 50+ 列
- [ ] 多重匹配：搜索所有出现，不只第一个
- [ ] 除零：分母为零前检查（`#DIV/0!`）
- [ ] 错误引用：验证所有单元格引用指向正确位置（`#REF!`）
- [ ] 跨工作表引用：使用正确格式 `Sheet1!A1`

### 公式测试策略

- [ ] 先小范围测试公式再广泛应用
- [ ] 验证公式依赖的所有单元格存在
- [ ] 测试边界值：零、负数、极大值

### 解读 recalc.py 输出

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## 最佳实践

### 库选择

- **pandas**：数据分析、批量操作、简单导出。
- **openpyxl**：复杂格式、公式、Excel 特有功能。

### openpyxl 要点

- 单元格索引是 1 起始（`row=1, column=1` 表示 A1）。
- 使用 `data_only=True` 读取计算值：`load_workbook('file.xlsx', data_only=True)`。
- **警告**：以 `data_only=True` 打开并保存会永久丢失公式。
- 大文件使用 `read_only=True` 读取或 `write_only=True` 写入。
- 公式被保留但不计算，需用 `scripts/recalc.py` 更新值。

### pandas 要点

- 显式指定数据类型：`pd.read_excel('file.xlsx', dtype={'id': str})`。
- 大文件只读必要列：`pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`。
- 正确处理日期：`pd.read_excel('file.xlsx', parse_dates=['date_column'])`。

### 可复用样式辅助函数

```python
from openpyxl.styles import PatternFill, Border, Side, Font

ZEBRA_FILL_1 = PatternFill(fill_type="solid", fgColor="FFFFFF")
ZEBRA_FILL_2 = PatternFill(fill_type="solid", fgColor="F7F9FC")
KPI_FILL = PatternFill(fill_type="solid", fgColor="EAF2FF")
THIN_BORDER = Border(
    left=Side(style="thin", color="D9DEE7"),
    right=Side(style="thin", color="D9DEE7"),
    top=Side(style="thin", color="D9DEE7"),
    bottom=Side(style="thin", color="D9DEE7"),
)
TOP_EMPHASIS_BORDER = Border(
    left=Side(style="thin", color="D9DEE7"),
    right=Side(style="thin", color="D9DEE7"),
    top=Side(style="medium", color="AAB4C5"),
    bottom=Side(style="thin", color="D9DEE7"),
)

def apply_zebra_style(ws, min_row, max_row, min_col, max_col):
    for r in range(min_row, max_row + 1):
        fill = ZEBRA_FILL_1 if (r - min_row) % 2 == 0 else ZEBRA_FILL_2
        for c in range(min_col, max_col + 1):
            ws.cell(r, c).fill = fill

def apply_light_borders(ws, min_row, max_row, min_col, max_col):
    for r in range(min_row, max_row + 1):
        for c in range(min_col, max_col + 1):
            ws.cell(r, c).border = THIN_BORDER

def highlight_kpis(ws, cells, label_col=None, label_text=None):
    for ref in cells:
        cell = ws[ref]
        cell.fill = KPI_FILL
        cell.font = Font(bold=True, color="1F2937")
    if label_col and label_text and cells:
        ws[f"{label_col}{ws[cells[0]].row}"] = label_text
```

## 代码风格

生成 Excel 操作 Python 代码时：

- 代码最小、简洁，避免不必要注释。
- 避免冗长变量名和冗余操作。
- 避免不必要的 `print`。

对于 Excel 文件本身：

- 复杂公式或重要假设单元格加注释。
- 硬编码值标注数据来源。
- 关键计算和模型段添加说明。
