# 文档转PPT

## 支持的文档格式

| 格式  | 方式       | 说明     |
| ----- | ---------- | -------- |
| .docx | markitdown | Word文档 |
| .pdf  | markitdown | PDF文档  |
| .md   | markitdown | Markdown |
| .txt  | markitdown | 纯文本   |

## 工作流

1. **提取文档内容**

   ```bash
   python -m markitdown document.docx
   ```

1. **AI生成PPT大纲** — 按SKILL.md中的叙事脊柱格式生成大纲

1. **选择创建模式** — Spire（专业版，唯一推荐）

1. **生成PPT**

## PDF转换（辅助）

使用系统安装的 LibreOffice 进行格式转换：

```bash
# PPT → PDF
soffice --headless --convert-to pdf output.pptx

# PDF → 图片（需要poppler）
# pdftoppm -jpeg -r 150 output.pdf slide
```

## 注意事项

- 文档内容过长时截取前10000字符
- 自动估算文档页数用于规划PPT页数
- 保留关键数据和引用来源
- 将复杂段落拆解为要点列表

## ⚠️ docx 图片 + 图号标题 自动提取（必做）

**当用户提供的论文是 .docx 且需要"按图号自动定位图片到对应PPT页"时，必须先执行图片与图号标题的关联提取。**

Word 中图片与图号标题的对应关系：

- 图片位于段落 A（段落内含 `<a:blip>` 标签）
- 图号标题位于段落 A 的**下一个非空段落**，文字形如 `图X-X  XXX图`（X 为数字）

提取流程：

```python
import zipfile, re, xml.etree.ElementTree as ET
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
CAPTION_RE = re.compile(r"^图\s*(\d+)\s*[-—]\s*(\d+)\s+(.+)$")

with zipfile.ZipFile("paper.docx") as zf:
    # 1) rId -> media/xxx
    rels = {}
    for m in re.finditer(r'Id="([^"]+)"\s+Type="[^"]*image"\s+Target="([^"]+)"',
                          zf.read("word/_rels/document.xml.rels").decode("utf-8")):
        rels[m.group(1)] = m.group(2)
    # 2) 遍历 body 段落，匹配 a:blip
    root = ET.fromstring(zf.read("word/document.xml").decode("utf-8"))
    body = root.find("w:body", NS)
    paragraphs = body.findall("w:p", NS)

def ptext(p):
    return "".join((t.text or "") for t in p.findall(".//w:t", NS)).strip()

results = []
seen = set()
for i, p in enumerate(paragraphs):
    blip = p.find(".//a:blip", NS)
    if blip is None:
        continue
    rid = blip.attrib.get(f"{{{NS['r']}}}embed")
    if not rid or rid in seen:
        continue
    seen.add(rid)
    caption = ""
    for j in range(i + 1, min(i + 6, len(paragraphs))):
        t = ptext(paragraphs[j])
        if CAPTION_RE.match(t):
            caption = t
            break
    results.append((rid, rels.get(rid, ""), caption))

# 3) 同时复制 media 到 图片素材/_from_docx/ 并写出 manifest
import shutil, pathlib
out_dir = pathlib.Path("图片素材/_from_docx")
out_dir.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile("paper.docx") as zf:
    for i, (rid, target, cap) in enumerate(results):
        media_path = "word/" + target
        ext = pathlib.Path(target).suffix or ".jpg"
        out = out_dir / f"img_{i:02d}{ext}"
        with zf.open(media_path) as src, open(out, "wb") as f:
            shutil.copyfileobj(src, f)
# 4) 写出 manifest（图片文件名 + 图号标题 + 用途建议）
manifest = "\n".join(
    f"img_{i:02d}{pathlib.Path(t).suffix or '.jpg'}\t{cap}"
    for i, (rid, t, cap) in enumerate(results)
)
(out_dir / "_manifest.txt").write_text(manifest, encoding="utf-8")
```

**按图号自动定位到对应PPT页**：

- `图3-1` `图3-2` → 系统设计章节（架构图、流程图）
- `图5-1` `图5-2` `图5-3` `图5-4` → 系统测试章节（属性面板、技能截图）
- `图4-1` `图4-2` → 系统实现章节（实现流程图、类图）

**特殊处理**：

- 封面/校徽等无图号标题的图（一般出现在最前部 P1-P5）→ 用作封面背景/装饰
- docx 中的 emoji 表情、特殊符号在 markitdown 提取时可能丢失 → 必要时手动校正
- 图片位置编号（img_00、img_01...）按 docx 中出现顺序排列，与原论文图号可能不一致 → 以 manifest 中的 caption 为准
