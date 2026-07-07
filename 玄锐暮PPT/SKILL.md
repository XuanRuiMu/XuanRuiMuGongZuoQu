---
name: 玄锐暮PPT
description:
  "PPT全流程处理技能。支持读取解析pptx内容、编辑修改现有演示文稿、合并拆分幻灯片、从零创建专业PPT（高级动画、渐变背景、阴影效果、3D效果、图表、表格）。Spire.Presentation统一引擎，34种独特布局模板池，9种装饰元素，21种入场动画+21种页面切换，四维度自由组合主题系统：8背景×15配色×8字体×34布局。触发场景：操作pptx文件、读取幻灯片内容、编辑演示文稿、合并拆分PPT、从零创建PPT、制作幻灯片、美化演示文稿、添加动画效果、WPS演示。当用户说pptx、读取ppt、编辑ppt、合并幻灯片、拆分ppt、ppt模板、演讲者备注、做ppt、做幻灯片、创建演示、ppt动画、美化ppt、WPS、演示文稿、幻灯片、presentation、create
  ppt、edit ppt、slides时触发此技能。"
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX Skill

## 引擎

| 引擎               | 页数限制      | 动画 | 渐变/阴影/3D | WPS兼容 |
| ------------------ | ------------- | ---- | ------------ | ------- |
| Spire.Presentation | 10页(9内容页) | ✅   | ✅           | ✅      |

**超9页方案**：分批生成多个PPT，用户手动拼接

### ⚠️ Spire 免费版已知限制（不算BUG）

> **重要**：以下限制是 Spire.Presentation 免费版的固有行为，**不是代码bug，无需修复**：

| 限制             | 表现                                                                                                                                 | 处理方式                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| **1. 水印页**    | 第1页强制插入"Evaluation Warning"内容页                                                                                              | 用户手动删除（不算bug）                                                                                                    |
| **2. 文字水印**  | 每页左上角带红色"Evaluation Warning : The document was created with Spire.Presentation for Python"文字+矩形边框                      | 用户手动删除（不算bug）                                                                                                    |
| **3. 10页上限**  | 单文件最多10页（含水印页），9页有效内容                                                                                              | 分批生成+用户手动拼接                                                                                                      |
| **4. Shape边框** | Spire.Presentation的Line对象**没有Visible属性**，`Line.Visible=False`、`Line.Width=0`、`Line.Style=TextLineStyle.none`均无法移除边框 | 必须在`engine.save()`后用python-pptx后处理`shape.line.fill.background()`移除（已内置到`engine.save(remove_borders=True)`） |

#### 判断原则

- 如果一个"问题"在删除水印页/水印文字后消失 → **不是bug**
- 如果一个问题在删除水印后仍然存在 → 才是真bug，需要修复

---

## 检查点文档机制

**解决上下文溢出问题**：PPT生成过程可能因上下文溢出导致进度丢失。通过检查点文档，即使上下文完全丢失，新会话也能从断点恢复。

### 总入口：进度总览

**每次执行skill的第一步，必须先读取总入口文件**：

1. 检查 `{项目目录}/pptx-checkpoints/进度总览.md` 是否存在
2. 如存在，读取并按指示恢复（跳到对应步骤继续）
3. 如不存在，从头开始

**每次步骤变更时，必须更新总入口文件**：

```markdown
# PPT生成进度总览

## 当前状态

- 当前步骤：步骤N（[步骤名称]）
- 完成状态：[进行中/已完成]

## 已完成步骤

- 步骤1：✅ [完成日期]
- 步骤2：✅ [完成日期]

## 迭代信息

- 当前迭代轮次：[1/2/3]
- 迭代原因：[评分未达标/其他]
- 回退到的步骤：[步骤5/步骤6]

## 下一步操作

- [具体操作描述]

## 关键注意事项

- [从最近完成的检查点中提取的注意事项]
```

### 检查点文件路径

所有检查点文件存放在 `{项目目录}/pptx-checkpoints/` 目录：

```text
pptx-checkpoints/
├── 进度总览.md              ← 总入口，每次步骤变更时更新
├── 步骤1-检查点.md          ← 仁爱检测 + 版本选择
├── 步骤2-检查点.md          ← 4步风格询问
├── 步骤3-检查点.md          ← 内容规划（含叙事脊柱）
├── 步骤4-检查点.md          ← 外部资源生成
├── 步骤5-检查点.md          ← 代码生成
├── 步骤6-检查点.md          ← 视觉质检
├── 步骤7-检查点.md          ← 内容质检 + 评分
└── 步骤8-检查点.md          ← 交付 + 清理
```

### 检查点操作流程

#### 步骤执行前

1. 读取 `pptx-checkpoints/进度总览.md`，确认当前进度
2. 读取对应的 `pptx-checkpoints/步骤N-检查点.md`
3. 按检查点中的"恢复时需读取的文件"列表读取必要文件
4. 按检查点中的"恢复后跳过的子任务"跳过已完成部分
5. 从断点继续执行

#### 步骤执行结束前

1. 生成 `pptx-checkpoints/步骤N-检查点.md`
2. 更新 `pptx-checkpoints/进度总览.md`

#### 验证门失败时的检查点处理

- 验证门失败需要回退重做时，当前检查点的完成状态必须标记为"部分完成（验证门N失败，需回退到步骤X重做）"
- 禁止将验证门失败的步骤标记为"已完成"，否则恢复时会跳过该步骤
- 回退重做时，被回退步骤的检查点应在重做完成后重新生成

### 检查点内容模板

```markdown
# 步骤N：[步骤名称] - 检查点

## 完成状态

[已完成/部分完成（说明完成到哪一步）]

## 关键产出物路径

- [产出物1路径]
- [产出物2路径]

## 本步骤关键数据

- [步骤专属的关键数据]

## 恢复时需读取的文件

- [文件1路径]：[读取目的]
- [文件2路径]：[读取目的]

## 恢复后跳过的子任务

- [已完成的子任务1]
- [已完成的子任务2]

## 下一步注意事项

- [注意事项1]
- [注意事项2]

## 遗留问题

- [问题1]
```

---

## Quick Reference

| 任务          | 指南                                                                            |
| ------------- | ------------------------------------------------------------------------------- |
| 读取/分析内容 | `python -m markitdown presentation.pptx`                                        |
| 编辑现有PPT   | Read [editing.md](editing.md) — 补充功能                                        |
| 从零创建PPT   | 1. 风格询问 → 2. 规划内容 → 3. Read [spire-engine.md](spire-engine.md)          |
| 主题与布局    | Read [themes.md](themes.md) — 8背景×15配色×8字体×34布局                         |
| 图表生成      | Read [charts.md](charts.md) — 自动图表                                          |
| 文档转PPT     | Read [document-convert.md](document-convert.md)                                 |
| 视觉质检      | Read [visual-qa.md](visual-qa.md) — Spire截图 + AI分析                          |
| 缩略图预览    | `python scripts/thumbnail.py input.pptx [prefix] [--cols N]` — 快速网格预览每页 |

---

## ⚠️ REQUIRED: 仁爱学院论文答辩PPT分支

**当用户提供文档资料作为PPT内容来源时，必须先执行此检测。此检测在4步风格询问之前。**

### 检测步骤

1. 用 `markitdown` 提取文档文本
2. 检查文本中是否包含"天津仁爱学院"关键字
3. 如果检测到 → 进入仁爱论文答辩PPT流程（询问版本 + 通用内容规范）
   - **⚠️ 仁爱学院论文答辩PPT必须15~20页**（含水印页），这是硬性要求
   - Spire免费版单文件最多10页，15~~20页需分批生成2~~3个PPT后手动拼接
4. 如果未检测到 → 跳过此分支，进入4步风格询问流程

### 版本选择（仅影响视觉风格，不影响内容结构）

使用 `AskUserQuestion` 询问用户选择版本：

| 版本   | 视觉风格                         | 流程差异                  | 适用场景                   |
| ------ | -------------------------------- | ------------------------- | -------------------------- |
| 普通版 | 白底黑字、大字体、无装饰、无动画 | 跳过4步风格询问，直接生成 | 答辩实用为主，让老师看清楚 |
| 专业版 | 完整主题系统、动画、装饰         | 走完整4步风格询问流程     | 追求视觉效果               |

> **重要**：无论选择哪个版本，**内容结构和图片处理流程完全相同**。区别仅在于视觉呈现方式。

---

### 通用内容结构（普通版和专业版共用）

**⚠️ 仁爱学院论文答辩PPT必须15~20页**。以下为15~20页的详细内容分配：

| 页    | 内容                     | 说明                                                     |
| ----- | ------------------------ | -------------------------------------------------------- |
| 1     | 封面                     | 论文题目、姓名、学号、指导教师、天津仁爱学院             |
| 2     | 目录/研究概述            | 研究背景与主要研究内容                                   |
| 3-5   | 系统需求分析（**重点**） | 配有相关图（用例图、功能结构图等），3页展开论述          |
| 6-8   | 系统设计（**重点**）     | 配有相关图（架构图、E-R图、类图等），3页展开论述         |
| 9-11  | 系统实现                 | 特色功能界面截图 + 核心代码，3页展示                     |
| 12-13 | 系统测试                 | 测试用例与测试结果                                       |
| 14    | 论文特色/创新之处        | 简要论述                                                 |
| 15    | 简要回顾主要工作和成果   | 总结                                                     |
| 16-20 | 扩展页（可选）           | 根据论文内容补充：详细技术方案、更多实现截图、性能分析等 |

> **分批生成策略**：Spire免费版单文件最多10页，15~~20页需分2~~3批生成：
>
> - **第1批**（10页）：封面~~系统需求分析~~系统设计前半
> - **第2批**（10页）：系统设计后半~~系统实现~~系统测试~~创新~~总结
> - **第3批**（可选）：扩展页
> - 生成后用户手动拼接为一个完整PPT

---

### 通用图片处理流程（普通版和专业版共用，铁律）

> **⚠️ 铁律：必须先识别图片内容，确认与章节匹配后才能插入！禁止无脑按图号插入！**

#### 步骤1：提取论文中的图片

使用 `document-convert.md` 中的 docx 图片提取脚本：

1. 解析 docx 中所有 `<a:blip>` 标签，提取图片文件
2. 匹配图片与图号标题（格式：`图X-X  XXX图`）
3. 将图片保存到 `图片素材/_from_docx/` 目录
4. 生成 `_manifest.txt` 记录图片文件名 + 图号标题

#### 步骤2：AI识图验证（必须执行，不可跳过）

**对每一张提取的图片，必须执行AI识图验证**：

1. 读取图片文件，使用AI视觉能力识别图片实际内容
2. 将图片实际内容与图号标题描述进行对比
3. 判断图片属于哪个章节/内容类型：
   - 用例图 / 功能结构图 → 需求分析章节
   - 架构图 / E-R图 / 类图 / 流程图 → 系统设计章节
   - 界面截图 → 系统实现章节
   - 其他类型 → 根据内容判断
4. **如果图片内容与图号标题不匹配**（如标题写"用例图"但实际是架构图），以**图片实际内容**为准进行分类

**验证输出格式**（每张图片）：

```text
图片文件: img_03.png
图号标题: 图3-2  系统用例图
AI识别内容: 包含多个小人图标和椭圆，确认为用例图
分类: 需求分析章节
匹配结果: ✅ 标题与内容一致
```

或：

```text
图片文件: img_05.png
图号标题: 图4-1  系统架构图
AI识别内容: 包含实体属性和关系连线，实际为E-R图
分类: 系统设计章节
匹配结果: ⚠️ 标题与内容不一致，以实际内容（E-R图）为准
```

#### 步骤3：图片插入策略

根据步骤2的验证结果，将图片插入对应PPT页面：

| PPT页面           | 应插入的图片类型                          | 选择标准                        |
| ----------------- | ----------------------------------------- | ------------------------------- |
| 需求分析（3-4页） | 用例图、功能结构图、需求分析相关图        | AI识别为"需求分析"类的图片      |
| 系统设计（5-6页） | 架构图、E-R图、类图、流程图、数据库设计图 | AI识别为"系统设计"类的图片      |
| 系统实现（7页）   | 界面截图、功能演示截图                    | AI识别为"系统实现/界面"类的图片 |

##### 插入规则

- 每页最多放1-2张图，确保图片足够大、清晰可读
- 图片宽度 ≥ 幻灯片宽度的60%（普通版和专业版均如此）
- 图片下方保留图号标题文字
- 如果某章节对应的图片超过2张，选择最有代表性的

#### 步骤4：程序生成补充图片（可选）

当论文中缺少某些关键图时（如需求分析无图、系统设计无图），可使用程序生成补充：

- 使用 `auto_charts.py` 或 matplotlib 生成架构图、流程图等
- 使用 mermaid 生成图后截图插入
- **生成的图片也必须经过AI识图验证**，确认内容与目标章节匹配

---

### 普通版视觉规范

**仅在选择"普通版"时适用。**

- 背景：纯白 `engine.set_solid_background(slide, (255, 255, 255))`
- 标题文字：黑色加粗，字体大小 ≥ 28pt
- 副标题/小标题：黑色加粗，字体大小 ≥ 24pt
- 正文文字：黑色，字体大小 **≥ 20pt**（简易版硬性要求，确保答辩老师能看清）
- 字体：微软雅黑
- 无装饰元素、无渐变
- 无动画（或仅最简单的淡入）
- 布局简洁：标题 + 正文/图片为主
- 图片宽度 ≥ 幻灯片宽度的60%

**普通版代码生成示例**：

```python
from scripts.spire.engine import PPTEngine
import spire.presentation as sp

engine = PPTEngine()

for slide_info in slides:
    slide = engine.add_slide()
    engine.set_solid_background(slide, (255, 255, 255))

    # 标题（alpha=255白底填充，alpha=0透明填充在Spire中不生效）
    title_shape = engine.create_card(slide, sp.ShapeType.Rectangle,
        48, 24, 864, 50, (255,255,255), 255, shadow=False)
    engine.add_text_to_shape(title_shape, slide_info["title"],
        font_name="微软雅黑", font_size=28, bold=True, color=(0,0,0))

    # 内容
    if slide_info.get("image"):
        engine.add_image(slide, slide_info["image"],
            192, 90, 576, 380)
        # 图片下方图号标题
        cap_shape = engine.create_card(slide, sp.ShapeType.Rectangle,
            192, 470, 576, 30, (255,255,255), 255, shadow=False)
        engine.add_text_to_shape(cap_shape, slide_info["caption"],
            font_name="微软雅黑", font_size=14, bold=False, color=(80,80,80))
    else:
        content_shape = engine.create_card(slide, sp.ShapeType.Rectangle,
            48, 90, 864, 420, (255,255,255), 255, shadow=False)
        engine.add_text_to_shape(content_shape, slide_info["content"],
            font_name="微软雅黑", font_size=20, bold=False, color=(0,0,0))

# ⚠️ 关键：remove_borders=True 自动用python-pptx后处理移除所有shape边框
# Spire的Line.Visible=False无效（Line对象无Visible属性），边框只能通过python-pptx移除
engine.save("output.pptx", remove_borders=True)
```

⚠️ Spire边框BUG：见引擎限制表格第4项

#### 普通版跳过的步骤

- 跳过4步风格询问（白底黑字已确定）
- 跳过装饰元素分配
- 跳过动画分配（或仅最简单的淡入）
- 跳过视觉质检中的装饰遮挡检测（无装饰）
- 保留内容质检

### 专业版

专业版走完整的4步风格询问流程，但**内容结构仍遵循上述6部分通用结构**，图片处理也必须遵循上述通用图片处理流程（含AI识图验证）。

---

## ⚠️ REQUIRED: 4步风格询问流程

**在生成PPT前，必须通过AskUserQuestion与用户交互确认视觉偏好。**

> **前置条件**：如果检测到仁爱学院论文且用户选择了"普通版"，则跳过本章节，直接进入普通版生成流程。
>
> **重要概念区分**（避免歧义）：
>
> - **"简洁"指生成的PPT内容/排版简洁**——每页元素少、文字为主、装饰克制
> - **风格询问流程本身要详细充分**——必要时拆成多轮、多问题，绝不可因为"想保持简洁"而省略询问
> - 错误示例：用户说"简洁"后跳过4步询问直接生成 → 错过配色/字体/章节策略等关键决策
> - 正确示例：用户说"简洁"后仍按完整4步走，得到的"简洁"只影响最终PPT的视觉密度

### Step 1: 用途与规模

询问用户：

- PPT用途/场景（如：学术答辩、商务汇报、产品发布等）
- 大致页数
- 内容来源（文档路径/口头描述）

### Step 2: 视觉风格偏好

根据Step 1的场景，询问视觉风格偏好：

- 暗色系（赛博暗夜/深海商务/星空紫罗兰/极客黑）
- 亮色系（学术象牙白/暖阳橙/樱花粉/翡翠绿）
- 展示每个选项的文字描述

### Step 3: 配色与字体

根据Step 2的风格筛选匹配的配色方案和字体方案：

- 展示3-5个推荐配色方案（带描述）
- 展示3-5个推荐字体方案
- 询问章节配色策略：统一配色 / 章节间变化

### Step 4: 内容与特殊要求

询问：

- 是否有已有图片素材（如有，提示放入「图片素材」文件夹）
- 特殊要求（动画强度、是否需要图表等）

---

## ⚠️ REQUIRED: 标准化工作目录

**路径规则（铁律）**：除非用户明确指定了其他目录，否则所有PPT相关文件必须在以下路径结构中：

```text
{工作区根目录}/玄锐暮PPT/{项目名}/
```

- **工作区根目录**：自动检测（通过 CLAUDE.md / .git / .claude 标记文件向上查找）
- **玄锐暮PPT**：固定文件夹名，不存在时必须立即创建
- **项目名**：根据PPT用途命名（如"毕业设计"、"商务汇报"等）

**示例**：工作区根目录为 `D:\XiTongWenJianJia\ZhuoMian\燃烧之陨我的世界服务端`，项目名为"毕业设计"时：

```text
D:\XiTongWenJianJia\ZhuoMian\燃烧之陨我的世界服务端\
└── 玄锐暮PPT/
    └── 毕业设计/
        ├── 生成/          # 生成的PPT文件
        ├── 临时/          # 临时文件（图表、截图等）
        ├── 图片素材/      # 用户提供的和自动生成的图片
        ├── 其他素材/      # 字体、图标等其他资源
        ├── 质检/          # QA输出
        └── pptx-checkpoints/          # 检查点文档（上下文溢出恢复）
            ├── 进度总览.md              # 总入口：当前步骤、完成状态、迭代信息
            ├── 步骤1-检查点.md          # 每步骤独立检查点
            └── ...
```

```python
from scripts.spire.workspace import create_project_workspace, get_project_paths

# 创建项目目录（自动检测工作区根目录，无需手动指定 base_dir）
paths = create_project_workspace(project_name="毕业设计")

# 用户明确指定目录时才传入 base_dir
# paths = create_project_workspace(project_name="毕业设计", base_dir="D:/custom/path")

# 获取路径
paths.output  # {工作区根目录}/玄锐暮PPT/毕业设计/生成/
paths.images  # {工作区根目录}/玄锐暮PPT/毕业设计/图片素材/
paths.qa      # {工作区根目录}/玄锐暮PPT/毕业设计/质检/
```

**⚠️ 关键**：`base_dir` 参数默认为 `None`，此时自动检测工作区根目录。仅在用户明确要求使用其他目录时才传入 `base_dir`。

### 工作区自动清理

**最终PPT交付后，必须执行清理**：

```python
from scripts.spire.workspace import cleanup_project

# 交付后清理临时文件和质检产物，保留最终PPT和图片素材
cleaned = cleanup_project("毕业设计")

# 如果用户要求保留检查点文件（用于后续恢复）
# cleaned = cleanup_project("毕业设计", keep_checkpoints=True)
```

#### 清理范围

- `临时/` 目录：所有生成脚本、中间产物
- `质检/` 目录：截图、报告
- `pptx-checkpoints/` 目录：检查点文件（除非 `keep_checkpoints=True`）

#### 保留

- `生成/` 目录：最终PPT文件
- `图片素材/` 目录：用户可能手动添加了图片

---

## Reading Content

```bash
python -m markitdown presentation.pptx
```

---

## Creating from Scratch

**Read [spire-engine.md](spire-engine.md) for full engine API details.**

### Quick Start

```python
from scripts.spire.engine import PPTEngine
from scripts.spire.themes import combine, suggest_combination
from scripts.spire.layouts import match_layout, ContentType
from scripts.spire.decorations import assign_decorations, render_decoration
from scripts.spire.shapes_animations import assign_slide_animations, apply_slide_animations, AnimationLibrary

engine = PPTEngine()

# 选择主题
theme = suggest_combination("商务汇报")

# 为每页选择不同布局
used_layouts = []
lib = AnimationLibrary()

for i in range(9):
    content_type = ContentType.CONTENT  # 根据内容选择
    layout = match_layout(content_type, used_layouts)
    used_layouts.append(layout.name)

    slide = engine.add_slide()
    engine.set_gradient_background(slide, theme.bg_start, theme.bg_end)

    # ... 创建元素 ...

    # ⚠️ 关键：按角色分组分配动画，确保每个元素都有动画
    shapes_by_role = {
        "title": [title_shape],
        "card": [card1, card2, card3],
    }
    anim_map = assign_slide_animations(shapes_by_role)
    apply_slide_animations(engine, slide, anim_map)

    # 页面切换
    engine.set_transition(slide, lib.TRANSITIONS[i % len(lib.TRANSITIONS)][1])

engine.save("output.pptx", remove_borders=True)
```

### ⚠️ 免费版限制

最多10页幻灯片（含1页空白水印页），有效内容9页。超过9页需分批生成后手动拼接。

### 可用动画 (21种入场 + 21种切换)

**入场动画**: fade, fly, float, zoom, spin, bounce, expand, strips, wipe, split, wheel, checkerboard, blinds, dissolve,
diamond, circle, appear, box, comb, flash_once, peek

**页面切换**: fade, push, cover, wedge, split, blinds, wheel, fall_over, dissolve, ripple, shred, switch, reveal,
honeycomb, flash, morph, wipe, checker, comb, newsflash, random

---

## 布局模板池 (34种)

**Read [themes.md](themes.md) for full layout details.**

34种独特布局，按类型分类（每页zone数≤4，遵循简洁原则）：

| 类型   | 数量 | 说明                  |
| ------ | ---- | --------------------- |
| 封面类 | 5    | 封面页的不同视觉方案  |
| 目录类 | 3    | 目录/议程页的不同排列 |
| 内容类 | 14   | 文字为主的内容页      |
| 数据类 | 5    | 图表/统计/对比展示    |
| 流程类 | 5    | 流程图/架构图/时间线  |
| 结尾类 | 3    | 总结/致谢/问答页      |

### 核心规则：每页必须使用不同的布局模板

### 简洁规则：每个zone对应一个shape

每个zone对应一个shape，文字直接写在shape内，不要创建额外的不可见矩形！

---

## 装饰元素系统

9种装饰类型，每页分配不同的装饰组合：

- 渐变色带（顶部/底部/左侧/右侧）
- 几何装饰（圆形/三角形/菱形/六边形，半透明）
- 水平线/竖线/对角线（实线/虚线）
- 圆点阵列
- 括号装饰
- 交叉线/连接线

### ⚠️ 装饰元素与文字的关系（铁律）

> **装饰元素不需要避开任何特定区域，但绝对不能遮挡文字。**

| 规则             | 说明                                                                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **唯一硬约束**   | 装饰不能遮挡任何文字（包括标题、副标题、卡片内文字、要点文字等）                                                                       |
| **程序化检测**   | 装饰 vs 文字的重叠属于 `critical` 级别问题，程序化重叠检测能识别                                                                       |
| **唯一可靠验证** | **只能通过截图（视觉）确认装饰是否遮挡文字**——程序化检测的"无重叠"不能保证视觉上不挡字（如：装饰在标题色块边缘外、但视觉上与色块粘连） |

#### 典型违规

- 装饰元素位于 (30, 30, 50, 50) 区域，标题色块位于 (48, 20, 864, 60) → 装饰的右半部分覆盖标题"第1个字符"位置
- 装饰元素位于右下角，卡片内容延伸出卡片边界 → 装饰压在卡片文字上

#### 修复方法

1. **生成后必看截图**（见 QA 章节）
2. 看到装饰挡字 → 调整装饰位置（装饰位置可变，不用固定避开某区域）
3. 调整后再看截图确认

#### 为什么不能靠程序化检测兜底

- 装饰是半透明的，可能视觉上明显挡字但 bounding box 不算"重叠"
- 文字 shape 的 bounding box 与装饰 shape 的 bounding box 边缘相邻时，程序化检测会判定"无重叠"，但视觉上仍然粘连
- **截图是唯一可靠验证**

---

## 动画分配策略

### 铁律：每个可见元素都必须有入场动画

同级元素使用相同动画，不同级元素使用不同动画。

### 方法1：按角色分组分配（推荐，确保每个元素都有动画）

```python
from scripts.spire.shapes_animations import assign_slide_animations, apply_slide_animations, AnimationLibrary

# 创建元素后，按角色分组
shapes_by_role = {
    "title": [title_shape],
    "card": [card1, card2, card3],
    "decoration": [deco1, deco2],
}

# 为每页的所有元素分配动画
anim_map = assign_slide_animations(shapes_by_role)
# 结果：title用淡入，card用飞入，decoration用缩放（同级元素同动画）

# 应用动画到幻灯片
apply_slide_animations(engine, slide, anim_map)

# 页面切换效果（每页不同）
lib = AnimationLibrary()
engine.set_transition(slide, lib.TRANSITIONS[slide_idx % len(lib.TRANSITIONS)][1])
```

### 方法2：每页单动画（仅用于简单场景）

```python
from scripts.spire.shapes_animations import assign_animations
animations = assign_animations(num_slides=9)
# ⚠️ 此方法每页只返回1个动画效果，不保证所有元素都有动画
```

### 动画分配规则

- **同级元素**（相同role，如都是card）使用相同的入场动画，按顺序依次触发
- **不同级元素**（不同role，如title vs card）使用不同的入场动画
- 16种入场动画按角色轮换分配，确保视觉多样性

---

## 章节配色策略

```python
from scripts.spire.themes import generate_chapter_colors, ChapterColorStrategy

# 统一配色
colors = generate_chapter_colors(ChapterColorStrategy.UNIFIED, "商务蓝", 4)

# 章节间变化
colors = generate_chapter_colors(ChapterColorStrategy.PER_CHAPTER, "商务蓝", 4)
```

---

## 四维度主题系统

**Read [themes.md](themes.md) for full details.**

8 BackgroundStyle × 15 ColorScheme × 8 FontScheme × 34 LayoutTemplate = **5760种组合**

---

## ⚠️ REQUIRED: Pre-Generation Planning

**Before writing any code, you MUST complete these planning steps:**

### Step 1: 4步风格询问（必须先完成）

见上方「4步风格询问流程」章节。

### Step 2: Output Content Design Plan

Present a structured plan covering:

1. **Theme Selection** (from 4-dimension system)
2. **Chapter Color Strategy** (UNIFIED or PER_CHAPTER)
3. **叙事脊柱（Claim Spine）**——每页必须有论点，不是填满页面
4. **Slide-by-Slide Outline** with layout assignment and layout family

#### 叙事脊柱（铁律）

**每页非附录幻灯片必须声明以下4项**：

| 项目             | 说明                                        | 示例                                             |
| ---------------- | ------------------------------------------- | ------------------------------------------------ |
| **Kicker**       | 1-3词角色标签，命名这页的角色               | `需求聚焦`、`增长引擎`、`技术选型`               |
| **Claim Title**  | 结论性标题，不是topic标签                   | "核心需求集中在数据管理与可视化" 而非 "需求分析" |
| **Proof Object** | 一个核心证据对象（图表/表格/时间线/对比图） | 用例图 + 功能结构图                              |
| **Support Note** | 简洁事实来源                                | 基于用户调研和竞品分析                           |

**标题质量判断**：如果换一个公司/项目名后标题仍然适用，说明标题不够具体，需要锐化。

#### 反面示例

- "需求分析" → 这是topic，不是claim
- "系统设计" → 这是topic，不是claim

#### 正面示例

- "用户核心需求集中在数据管理与可视化展示" → 这是claim
- "管线架构比单体架构更适合高频事件处理" → 这是claim

#### Example planning output

```markdown
## Presentation Plan

**Theme:** 赛博暗夜 × 霓虹科技 × 等宽极客 **Chapter Colors:** PER_CHAPTER (霓虹科技 → 科技青 → 数据绿) **Motif:**
Rounded cards with gradient backgrounds

### Claim Spine

- 论点弧线：[一句话概括整个PPT的叙事弧线]
- 目标受众：[谁在看这个PPT]

### Slides:

1. [封面] Kicker: — | Claim: [项目名] — [一句话定位] | Layout: 封面类
2. [目录] Kicker: 路线图 | Claim: 三个关键问题驱动本次汇报 | Layout: 目录类
3. [内容] Kicker: 需求聚焦 | Claim: 核心需求集中在数据管理与可视化 | Proof: 用例图 | Layout: 内容类-左文右图
4. [内容] Kicker: 技术选型 | Claim: 管线架构比单体更适合高频事件 | Proof: 架构对比图 | Layout: 流程类
5. [内容] Kicker: 增长引擎 | Claim: 模块化设计支持快速扩展 | Proof: 模块依赖图 | Layout: 数据类 ... N+1. [致谢] Kicker:
   — | Claim: 感谢聆听 | Layout: 结尾类
```

#### 布局族节奏控制

规划时必须标注每页的**布局族**（封面/目录/内容/数据/流程/结尾），并遵守以下约束：

- 同一布局族不连续出现超过2页
- 内容族之间穿插数据族或流程族，制造节奏感
- 10页PPT至少使用4种不同布局族
- 不超过2个card-grid布局（整个PPT）

### Step 3: Pre-Generate External Assets

For figures marked `[External]`, generate them BEFORE writing code.

#### ⚠️ CRITICAL: Color Consistency

All generated diagrams and charts MUST use the same color palette as the presentation.

### Step 4: Verify Assets Before Proceeding

**Only proceed after:**

- [ ] Style inquiry completed (4 steps)
- [ ] Content plan is complete and approved (with claim spine)
- [ ] All `[External]` assets are generated
- [ ] Working directory created
- [ ] 检查点已生成：`pptx-checkpoints/步骤1-检查点.md` ~ `pptx-checkpoints/步骤3-检查点.md`
- [ ] 进度总览已更新

---

## 完整工作流（含检查点操作）

### 步骤1：仁爱检测 + 版本选择

- [ ] 检查 `pptx-checkpoints/步骤1-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 用 `markitdown` 提取文档文本，检查"天津仁爱学院"关键字
- [ ] 如检测到 → 进入仁爱论文答辩PPT流程（询问版本）
- [ ] 如未检测到 → 跳过仁爱分支
- [ ] 检查点必记：是否检测到仁爱学院、版本选择结果、内容来源路径
- [ ] 生成 `pptx-checkpoints/步骤1-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤2：4步风格询问

- [ ] 检查 `pptx-checkpoints/步骤2-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 执行4步风格询问（用途→风格→配色字体→特殊要求）
- [ ] 仁爱普通版跳过此步骤
- [ ] 检查点必记：4步询问结果（主题、配色策略、字体、动画偏好）
- [ ] 生成 `pptx-checkpoints/步骤2-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤3：内容规划（含叙事脊柱）

- [ ] 检查 `pptx-checkpoints/步骤3-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 编写叙事脊柱：每页声明 kicker + claim title + proof object + support note
- [ ] 标注每页布局族，遵守节奏控制约束
- [ ] 规划外部资源清单（图表等）
- [ ] 检查点必记：叙事脊柱全文、布局族分配、外部资源列表
- [ ] 生成 `pptx-checkpoints/步骤3-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤4：外部资源生成

- [ ] 检查 `pptx-checkpoints/步骤4-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 生成所有标记为 `[External]` 的图表和图片
- [ ] 确保颜色与PPT配色一致
- [ ] 检查点必记：已生成的资源文件路径列表
- [ ] 生成 `pptx-checkpoints/步骤4-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤5：代码生成

- [ ] 检查 `pptx-checkpoints/步骤5-检查点.md` 是否存在，存在则从中恢复进度
- [ ] **验证步骤4的外部资源文件是否真实存在且可用**（逐个检查路径，不存在则回到步骤4重新生成）
- [ ] 按叙事脊柱和规划编写Spire引擎代码
- [ ] 每页使用不同布局，遵守布局族节奏控制
- [ ] 每页元素≤6个，装饰≤2个
- [ ] 所有元素分配入场动画
- [ ] `engine.save(remove_borders=True)`
- [ ] 检查点必记：生成PPT路径、页数、每页布局名、叙事脊柱执行情况
- [ ] 生成 `pptx-checkpoints/步骤5-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤6：视觉质检

- [ ] 检查 `pptx-checkpoints/步骤6-检查点.md` 是否存在，存在则从中恢复进度
- [ ] AI识图能力检查
- [ ] 截图 + 程序化重叠检测（合并执行，使用 `visual_inspector.py`）
- [ ] **深度布局检测（必做）**：使用 `validate_layout.py` 检测文字溢出容器、低对比度、空白页、箭头悬空等问题
- [ ] 修复 critical 级别问题和装饰遮挡
- [ ] 检查点必记：质检结果、修复的问题列表、是否通过视觉质检
- [ ] 生成 `pptx-checkpoints/步骤6-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤7：内容质检 + 评分

- [ ] 检查 `pptx-checkpoints/步骤7-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 用 `markitdown` 提取文本，检查内容完整性
- [ ] 逐项检查反模式清单（13项）
- [ ] 执行5维度评分（内容完整性/视觉节奏/文字可读性/装饰不干扰/整体一致性）
- [ ] 总分≥20/25且无维度<3 → 通过
- [ ] 不达标 → 迭代最弱2-3页，回到步骤5重新生成，然后重新执行步骤6（视觉质检）+ 步骤7（内容质检+评分）
- [ ] 最多3轮迭代
- [ ] 检查点必记：评分结果、反模式命中列表、迭代轮次
- [ ] 生成 `pptx-checkpoints/步骤7-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

### 步骤8：交付 + 清理

- [ ] 检查 `pptx-checkpoints/步骤8-检查点.md` 是否存在，存在则从中恢复进度
- [ ] 确认最终PPT存在且非空
- [ ] 确认页数正确
- [ ] 执行工作区自动清理（`cleanup_project`）
- [ ] 向用户交付最终PPT + 评分摘要
- [ ] 如有迭代，报告迭代结果和残余问题
- [ ] 生成 `pptx-checkpoints/步骤8-检查点.md`
- [ ] 更新 `pptx-checkpoints/进度总览.md`

---

## Design System

### ⚠️ 简洁优先原则（铁律）

元素越少越好，**文字内容才是核心**。

1. **每页元素上限**：每页不超过6个可见元素（含标题、卡片、装饰）
2. **一个卡片 = 一个shape**：不要在一个卡片内再创建多个不可见矩形放文字，直接用 `add_text_to_shape`
   在卡片shape内写多行文字
3. **装饰元素最多1-2个**：每页只放1-2个装饰元素（色带/几何/线条），不要堆砌
4. **文字优先于图形**：如果内容丰富，用文字填充卡片，而不是创建更多卡片
5. **避免嵌套shape**：不要创建"不可见矩形"（alpha=0）仅用于定位文字，这是元素爆炸的根源

**错误做法（元素爆炸）**：

```python
# ❌ 每个文字片段都创建一个不可见矩形
num_shape = engine.create_card(slide, sp.ShapeType.Ellipse, ..., alpha=0)  # 不需要！
t_shape = engine.create_card(slide, sp.ShapeType.Rectangle, ..., alpha=0)  # 不需要！
d_shape = engine.create_card(slide, sp.ShapeType.Rectangle, ..., alpha=0)  # 不需要！
```

**正确做法（简洁）**：

```python
# ✅ 一个卡片shape内直接写多行文字
card = engine.create_card(slide, sp.ShapeType.RoundCornerRectangle, x, y, w, h, ...)
engine.add_text_to_shape(card, "标题\n\n详细内容行1\n详细内容行2\n详细内容行3", ...)
```

### Before Starting

- **Pick a bold, content-informed color palette**: If swapping your colors into a completely different presentation
  would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp
  accent.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or
  commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored
  circles, thick single-side borders.

### For Each Slide

**保持简洁，文字内容为主。** 每页不超过6个可见元素。

#### ⚠️ CRITICAL: 每页布局必须不同

- 使用34种布局模板池，每页选取不同布局
- 标题位置不固定：左上、居中、右侧、底部、左侧竖排
- 卡片形状多样化：圆角矩形、矩形、椭圆、六边形、无边框
- 装饰元素每页不同：渐变色带、几何装饰、分隔线、圆点阵列等
- 动画效果每页不同

#### Layout options

- Two-column (text left, illustration on right)
- Icon + text rows
- 2x2 or 2x3 grid
- Half-bleed image with content overlay
- Large stat callouts
- Timeline or process flow
- Quote/callout slides
- Section dividers

### Typography

**Title fonts MUST be serif.** Cover title, slide titles, and subtitles must use a serif font.

**Professional Mode**: Use the 8 FontScheme from [themes.md](themes.md) for CJK-optimized options.

### Spacing

- 0.5" minimum margins (in 960×540 point system: ~48pt)
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **⚠️ Don't repeat the same layout** — every slide MUST use a different layout from the pool
- **⚠️ Don't exceed 9 content pages** per PPT file (Spire free version limit)
- **⚠️ Don't use OOXML XML injection for animations** — WPS incompatible, use Spire native only
- **⚠️ Don't forget to run the 4-step style inquiry before generating**
- **⚠️ Don't forget to create the working directory first**
- **⚠️ Don't create invisible rectangles for text** — use `add_text_to_shape` directly on card shapes, one card = one
  shape
- **⚠️ Don't exceed 6 visible elements per slide** — less is more, text content is king
- **⚠️ Don't add more than 2 decoration elements per slide** — one color band + one geometric is enough
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't use low-contrast elements** — icons AND text need strong contrast against background
- **NEVER use horizontal lines to separate title and body** — use whitespace or background color instead
- **⚠️ Don't leave slides blank** — every slide must have at least one visible element
- **⚠️ Spire边框BUG：见引擎限制表格第4项**
- **⚠️ Don't use `alpha=0` for white-background PPT** — Spire透明填充不生效，用 `alpha=255` + 匹配背景色代替

---

## QA (Required)

**Read [visual-qa.md](visual-qa.md) for full details.**

### ⚠️ AI识图能力检查（必须首先执行）

视觉质检需要AI具备识图能力。**在执行视觉质检前，必须先确认：**

- **有识图能力**：正常执行全流程（截图 + 程序化重叠检测 + 截图视觉分析）
- **无识图能力**：必须使用 `AskUserQuestion` 询问用户选择：
  - A. 换有识图能力的模型
  - B. 仅执行程序化重叠检测（不需要识图，但会漏掉"装饰挡字"等视觉问题）
  - C. 跳过视觉质检，仅内容质检

**绝对不可在无识图能力时静默跳过视觉质检！**

### 视觉质检

**Read [visual-qa.md](visual-qa.md) for full details.**

视觉质检 = 截图 + 程序化重叠检测（必须合并在同一步完成）。

#### 核心规则

1. 视觉质检和内容质检都必须执行
2. `blank_slide` 是生成缺陷，不可跳过
3. 发现问题后修复并重新质检，最多3轮
4. 质检输出目录：`{工作区根目录}/玄锐暮PPT/{项目名}/质检/`
5. **重叠检测中 `critical` 级别（两个有文字的元素重叠）必须修复**
6. **截图视觉分析中"装饰挡字""装饰粘连色块"必须修复**
7. **无识图能力时必须先询问用户**
8. **不要拆开"截图"和"程序化检测"成两个独立步骤**——必须合并

### 内容质检

```bash
python -m markitdown output.pptx
```

### 反模式检查清单（交付前必须逐项检查）

以下反模式发现即修复，不可交付：

| #   | 反模式                            | 说明                                        |
| --- | --------------------------------- | ------------------------------------------- |
| 1   | 标题是topic而非conclusion         | "需求分析"→"核心需求集中在数据管理与可视化" |
| 2   | chart有legend但应该用direct label | 直接标注比图例更清晰                        |
| 3   | equal-role boxes不对齐/不等高     | 同级卡片必须视觉一致                        |
| 4   | 3页连续同布局族                   | 你已有"每页不同布局"，但布局族层面也需变化  |
| 5   | box系统暗示了内容不支持的分组     | 装饰性容器无实际分组意义则删除              |
| 6   | proof object太薄无法支撑claim     | 一页只有一个薄图表撑不起论点                |
| 7   | body copy只为了填满空间           | 删掉不增加信息的文字                        |
| 8   | 可见容器比内容更抢眼              | 装饰不应压过信息                            |
| 9   | rounded cards作为默认脚手架       | 仅当数据关系需要包含时使用圆角卡片          |
| 10  | 标题换公司名后仍适用              | 标题不够具体，需锐化                        |
| 11  | 文字溢出容器边界                  | 卡片内文字必须完整可见                      |
| 12  | 低对比度元素                      | 文字和图标需要与背景强对比                  |
| 13  | 空白页                            | 每页至少一个可见元素                        |

### PPT质量评分标准（交付门控）

**评分规则**：每个维度1-5分，总分≥20/25且无维度低于3分才能交付。不达标则迭代最弱2-3页后重新评分。

| 维度           | 1分                 | 3分                    | 5分                      | 最低要求 |
| -------------- | ------------------- | ---------------------- | ------------------------ | -------- |
| **内容完整性** | 多页无claim         | 每页有内容但部分无论点 | 每页有kicker+claim+proof | ≥3       |
| **视觉节奏**   | 大部分页面同布局    | 有变化但节奏单调       | 4+种布局族，节奏感强     | ≥3       |
| **文字可读性** | 字号/对比度严重不足 | 基本可读但部分偏小     | 字号/对比度/间距均优     | ≥4       |
| **装饰不干扰** | 多处遮挡            | 少量视觉冲突           | 无遮挡无冲突             | ≥4       |
| **整体一致性** | 视觉系统混乱        | 基本统一但局部不一致   | 一个视觉系统贯穿始终     | ≥3       |

#### 迭代规则

- 评分不达标必须迭代最弱2-3页，偏好大胆重建弱页而非微调
- 最多3轮迭代，3轮后仍未达标则向用户报告当前结果和剩余问题
- 每轮迭代后重新评分

---

## Dependencies

- `pip install Spire.Presentation` — PPT引擎（动画、渐变、阴影、3D）
- `pip install python-pptx` — PPTX操作
- `pip install "markitdown[pptx]"` — 文本提取
- `pip install Pillow` — 缩略图
- `pip install lxml` — XML处理
- `pip install matplotlib numpy` — 图表生成

Full requirements: `pip install -r requirements.txt`

---

## Appendix: 模板编辑（补充功能）

**Read [editing.md](editing.md) for full details.**

模板编辑是补充功能，用于修改已生成PPT的文字内容（不受页数限制）。从零创建PPT请使用Spire引擎。

| 修改类型      | 推荐方法              | 限制              |
| ------------- | --------------------- | ----------------- |
| 修改文字内容  | 模板编辑（XML工作流） | 不能修改动画/渐变 |
| 修改动画/渐变 | Spire引擎重新加载编辑 | 受10页限制        |
| 大幅修改      | 重新生成              | 无                |
