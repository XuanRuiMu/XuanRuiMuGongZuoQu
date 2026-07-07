# Editing Presentations

## 编辑模式

| 模式                 | 何时使用                              | 方法                     |
| -------------------- | ------------------------------------- | ------------------------ |
| **Spire创建/编辑**   | 从零创建PPT或编辑带动画的PPT          | Spire.Presentation引擎   |
| **模板编辑（补充）** | 修改已生成PPT的文字内容，不受页数限制 | Unpack → Edit XML → Pack |

> **注意**: 模板编辑是补充功能，主要用于修改已生成PPT的文字内容。从零创建PPT请使用Spire引擎。模板编辑无法修改动画和渐变效果。

### 修改已生成PPT

当需要修改已生成的PPT时：

| 修改类型      | 推荐方法              | 限制              |
| ------------- | --------------------- | ----------------- |
| 修改文字内容  | 模板编辑（XML工作流） | 不能修改动画/渐变 |
| 修改动画/渐变 | Spire引擎重新加载编辑 | 受10页限制        |
| 大幅修改      | 重新生成              | 无                |

**Spire编辑已生成PPT**:

```python
from scripts.spire.engine import PPTEngine
engine = PPTEngine()
engine.ppt.LoadFromFile("existing.pptx")
slide = engine.ppt.Slides[0]
# 修改操作...
engine.save("modified.pptx")
```

⚠️ Spire免费版加载PPT时也受10页限制。超过10页的PPT请使用模板编辑修改文字。

---

## Template-Based Workflow

When using an existing presentation as a template:

1. **Analyze existing slides**:

   ```bash
   python -m markitdown template.pptx
   ```

   Review markitdown output to understand placeholder text and content structure.

2. **Plan slide mapping**: For each content section, choose a template slide.

   ⚠️ **USE VARIED LAYOUTS** — monotonous presentations are a common failure mode. Don't default to basic title + bullet
   slides. Actively seek out:
   - Multi-column layouts (2-column, 3-column)
   - Image + text combinations
   - Full-bleed images with text overlay
   - Quote or callout slides
   - Section dividers
   - Stat/number callouts
   - Icon grids or icon + text rows

   **Avoid:** Repeating the same text-heavy layout for every slide.

   Match content type to layout style (e.g., key points → bullet slide, team info → multi-column, testimonials → quote
   slide).

3. **Unpack**: `python scripts/unpack.py template.pptx unpacked/`

4. **Style-layer check (required before editing)**: Inspect XML style layer before making content edits. This
   establishes the template's actual style rules and prevents accidental style drift. If you later see
   misalignment/overflow/style inconsistency, inspect these files again before fixing.
   - Check `unpacked/ppt/slides/slide{N}.xml` for text runs, spacing, alignment, and local overrides
   - Check `unpacked/ppt/slideLayouts/slideLayout{N}.xml` for layout-level defaults
   - Check `unpacked/ppt/theme/theme1.xml` for theme fonts and colors

5. **Theme & Style alignment plan (required)**: Before real edits, write a short style plan to keep new content
   consistent with the template. Include at least:
   - Primary/secondary/accent colors to reuse
   - Header/body font faces and size ranges
   - Spacing and alignment conventions (margins, card gaps, list density)
   - Preferred visual motif from the template (cards, icon circles, dividers, etc.)

6. **Build presentation** (do this yourself, not with subagents):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides you want to reuse (`add_slide.py`)
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before step 7**

7. **Edit content**: Update text in each `slide{N}.xml`. **Use subagents here if available** — slides are separate XML
   files, so subagents can edit in parallel. For any edited slide with chart/diagram visuals, decide insight coverage
   and add/update on-slide insight text when needed.

8. **Clean**: `python scripts/clean.py unpacked/`

9. **Pack**: `python scripts/pack.py unpacked/ output.pptx --original template.pptx`

10. **⚠️ Layout QA (mandatory gate — RUN FIRST, DO NOT SKIP)**:

    ```bash
    python3 scripts/validate_layout.py output.pptx --slides <edited_slide_numbers>
    ```

    Only validate the slides you edited. Fix only the affected slide XML files until 0 issues. After each fix: `pack.py`
    → re-run `validate_layout.py`. Maximum 3 retry rounds — if issues persist, report to user and proceed.

11. **⚠️ Content QA (mandatory — run AFTER Layout QA passes, DO NOT SKIP)**: `python -m markitdown output.pptx`
    - For each edited slide with chart/diagram content, verify insight text is present when the visual carries
      analytical meaning.

12. **Record edited slide numbers (required)**: keep a list of slide numbers you changed (e.g., `3 5 8`).

---

## Spire编辑

When editing a Professional mode PPT (with animations, gradients, shadows, 3D effects):

**Read [spire-engine.md](spire-engine.md) for full engine API details.**

### Workflow

1. **Load existing PPT**:

   ```python
   from scripts.spire.engine import PPTEngine
   engine = PPTEngine()
   engine.load("input.pptx")
   ```

2. **Modify slides**: Use PPTEngine methods to edit content:

   ```python
   slide = engine.get_slide(0)
   engine.add_text_to_shape(slide, "Updated Title", 1, 1, 8, 1,
       font_size=32, font_color=(255, 255, 255), bold=True)
   engine.add_rounded_card(slide, 1, 2, 8, 3, fill_color=(30, 30, 60))
   ```

3. **Add animations** (if needed):

   ```python
   engine.add_animation(slide, shape, "fade", trigger="onClick")
   engine.add_transition(slide, "push", advance_time=3.0)
   ```

4. **Save**:

   ```python
   engine.save("output.pptx")
   ```

5. **Visual QA**: Use the visual inspector for Professional mode:

   ```python
   from scripts.spire.visual_inspector import PPTVisualInspector
   inspector = PPTVisualInspector()
   inspector.inspect("output.pptx", output_dir="qa_output/")
   ```

### Theme Changes

To change the theme of existing slides using the four-dimension system:

```python
from scripts.spire.themes import combine, suggest_combination

theme = combine(background="赛博暗夜", color="霓虹科技", font="等宽极客", layout="左文右图")

slide = engine.add_slide()
engine.set_gradient_background(slide, theme.bg_start, theme.bg_end)
```

### ⚠️ Spire Free Version Limitation

- Max 10 slides (9 effective content pages)
- When editing a PPT that exceeds this limit, use python-pptx for basic content edits instead
- Only use Spire engine when you need to modify animations, gradients, or advanced effects

---

## Scripts

| Script         | Purpose                               |
| -------------- | ------------------------------------- |
| `unpack.py`    | Extract and pretty-print PPTX         |
| `add_slide.py` | Duplicate slide or create from layout |
| `clean.py`     | Remove orphaned files                 |
| `pack.py`      | Repack with validation                |

### unpack.py

```bash
python scripts/unpack.py input.pptx unpacked/
```

Extracts PPTX, pretty-prints XML, escapes smart quotes.

### add_slide.py

```bash
python scripts/add_slide.py unpacked/ slide2.xml      # Duplicate slide
python scripts/add_slide.py unpacked/ slideLayout2.xml # From layout
```

Prints `<p:sldId>` to add to `<p:sldIdLst>` at desired position.

### clean.py

```bash
python scripts/clean.py unpacked/
```

Removes slides not in `<p:sldIdLst>`, unreferenced media, orphaned rels.

### pack.py

```bash
python scripts/pack.py unpacked/ output.pptx --original input.pptx
```

Validates, repairs, condenses XML, re-encodes smart quotes.

---

## 缩略图生成

使用 `thumbnail.py` 为PPT的每页幻灯片生成PNG缩略图网格，用于快速视觉预览。

### 功能

- 将PPT每页转为缩略图，排列成网格布局输出为JPG图片
- 每张缩略图标注对应的XML文件名（如 `slide1.xml`）
- 隐藏幻灯片以灰色占位符+X标记显示
- 页数较多时自动分页输出多个网格文件

### 用法

```bash
python scripts/thumbnail.py <input.pptx> [output_prefix] [--cols N]
```

### 参数

| 参数            | 必填 | 说明                              |
| --------------- | ---- | --------------------------------- |
| `input`         | 是   | 输入的PowerPoint文件路径（.pptx） |
| `output_prefix` | 否   | 输出文件名前缀，默认 `thumbnails` |
| `--cols`        | 否   | 网格列数，默认3，最大6            |

### 示例

```bash
# 默认输出 thumbnails.jpg，3列
python scripts/thumbnail.py presentation.pptx

# 自定义输出前缀，4列
python scripts/thumbnail.py template.pptx grid --cols 4
# 输出: grid.jpg（页数多时: grid-1.jpg, grid-2.jpg）
```

### 依赖

- `soffice`（LibreOffice）— PPT转PDF
- `pdftoppm`（Poppler）— PDF转图片
- `Pillow` — 图片处理
- `defusedxml` — XML安全解析

### 使用场景

在正式视觉质检（visual QA）之前，用缩略图网格快速浏览整体效果，确认页面顺序、布局多样性和内容分布是否合理。

---

## Slide Operations

Slide order is in `ppt/presentation.xml` → `<p:sldIdLst>`.

**Reorder**: Rearrange `<p:sldId>` elements.

**Delete**: Remove `<p:sldId>`, then run `clean.py`.

**Add**: Use `add_slide.py`. Never manually copy slide files—the script handles notes references, Content_Types.xml, and
relationship IDs that manual copying misses.

---

## Editing Content

**Subagents:** If available, use them here (after completing step 4). Each slide is a separate XML file, so subagents
can edit in parallel. In your prompt to subagents, include:

- The slide file path(s) to edit
- **"Use the Edit tool for all changes"**
- The formatting rules and common pitfalls below

For each slide:

1. Read the slide's XML
2. Identify ALL placeholder content—text, images, charts, icons, captions
3. Replace each placeholder with final content

**Use the Edit tool, not sed or Python scripts.** The Edit tool forces specificity about what to replace and where,
yielding better reliability.

### Formatting Rules

- **Bold all headers, subheadings, and inline labels**: Use `b="1"` on `<a:rPr>`. This includes:
  - Slide titles
  - Section headers within a slide
  - Inline labels like (e.g.: "Status:", "Description:") at the start of a line
- **Never use unicode bullets (•)**: Use proper list formatting with `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from the layout. Only specify `<a:buChar>` or `<a:buNone>`.

---

## Common Pitfalls

### Template Adaptation

When source content has fewer items than the template:

- **Remove excess elements entirely** (images, shapes, text boxes), don't just clear text
- Check for orphaned visuals after clearing text content
- Run visual QA to catch mismatched counts

When replacing text with different length content:

- **Shorter replacements**: Usually safe
- **Longer replacements**: May overflow or wrap unexpectedly
- Test with visual QA after text changes
- Consider truncating or splitting content to fit the template's design constraints

**Template slots ≠ Source items**: If template has 4 team members but source has 3 users, delete the 4th member's entire
group (image + text boxes), not just the text.

### Multi-Item Content

If source has multiple items (numbered lists, multiple sections), create separate `<a:p>` elements for each — **never
concatenate into one string**.

**❌ WRONG** — all items in one paragraph:

```xml
<a:p>
  <a:r><a:rPr .../><a:t>Step 1: Do the first thing. Step 2: Do the second thing.</a:t></a:r>
</a:p>
```

**✅ CORRECT** — separate paragraphs with bold headers:

```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" .../><a:t>Do the first thing.</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1" .../><a:t>Step 2</a:t></a:r>
</a:p>
<!-- continue pattern -->
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing. Use `b="1"` on headers.

### Smart Quotes

Handled automatically by unpack/pack. But the Edit tool converts smart quotes to ASCII.

**When adding new text with quotes, use XML entities:**

```xml
<a:t>the &#x201C;Agreement&#x201D;</a:t>
```

| Character | Name               | Unicode | XML Entity |
| --------- | ------------------ | ------- | ---------- |
| `"`       | Left double quote  | U+201C  | `&#x201C;` |
| `"`       | Right double quote | U+201D  | `&#x201D;` |
| `'`       | Left single quote  | U+2018  | `&#x2018;` |
| `'`       | Right single quote | U+2019  | `&#x2019;` |

### Other

- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)
