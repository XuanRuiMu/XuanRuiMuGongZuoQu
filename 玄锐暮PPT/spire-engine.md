# Spire.Presentation 专业引擎

## 适用场景

- 需要动画效果（入场动画 + 页面切换）
- 需要渐变背景、阴影、3D效果
- 需要圆角卡片等高级形状
- WPS兼容性要求

## ⚠️ 免费版限制

- 最多10页幻灯片（含1页空白页）
- 有效内容9页
- 超过9页需分批生成后手动拼接

## 引擎初始化

```python
from scripts.spire.engine import PPTEngine
engine = PPTEngine()
```

## 坐标系统

16:9幻灯片尺寸：**960×540** 点（不是英寸或像素）

所有坐标和尺寸均使用点（point）为单位。

## 渐变背景

```python
slide = engine.add_slide()
engine.set_gradient_background(slide, (5, 8, 20), (20, 26, 62))
```

## 纯色背景

```python
engine.set_solid_background(slide, (10, 10, 10))
```

## 圆角卡片（带阴影）

```python
import spire.presentation as sp
card = engine.create_card(
    slide, sp.ShapeType.RoundCornerRectangle,
    x=50, y=100, width=400, height=200,
    fill_color=(30, 40, 60), alpha=220, shadow=True
)
```

## 文字设置

```python
engine.add_text_to_shape(
    card, "标题文字",
    font_name="微软雅黑", font_size=24,
    bold=True, color=(255, 255, 255)
)
```

⚠️ **重要**:

- `TextRanges[0]` 不是 `TextRange`
- `TriState.TTrue/TFalse` 不是布尔值
- 必须显式创建 `sp.TextFont("微软雅黑")`

## 动画效果

### ⚠️ 铁律：每个可见元素都必须有入场动画

```python
from scripts.spire.shapes_animations import assign_slide_animations, apply_slide_animations, AnimationLibrary

# 方法1（推荐）：按角色分组，确保每个元素都有动画
shapes_by_role = {
    "title": [title_shape],
    "card": [card1, card2, card3],
    "decoration": [deco1, deco2],
}
anim_map = assign_slide_animations(shapes_by_role)
apply_slide_animations(engine, slide, anim_map)
# 同级元素用相同动画，不同级用不同动画

# 方法2：手动为单个元素添加动画
engine.add_animation(slide, shape, sp.AnimationEffectType.Fade)

# 页面切换
engine.set_transition(slide, sp.TransitionType.Wheel)
```

### 21种入场动画

| 效果   | 枚举值    |     | 效果 | 枚举值         |
| ------ | --------- | --- | ---- | -------------- |
| 淡入   | `Fade`    |     | 飞入 | `Fly`          |
| 浮入   | `Float`   |     | 缩放 | `Zoom`         |
| 旋转   | `Spin`    |     | 弹跳 | `Bounce`       |
| 展开   | `Expand`  |     | 条纹 | `Strips`       |
| 擦除   | `Wipe`    |     | 分裂 | `Split`        |
| 轮子   | `Wheel`   |     | 棋盘 | `Checkerboard` |
| 百叶窗 | `Blinds`  |     | 溶解 | `Dissolve`     |
| 菱形   | `Diamond` |     | 圆圈 | `Circle`       |
| 出现   | `Appear`  |     | 方框 | `Box`          |
| 梳齿   | `Comb`    |     | 闪烁 | `FlashOnce`    |
| 窥视   | `Peek`    |     |      |                |

### 21种页面切换

| 效果     | 枚举值     |     | 效果     | 枚举值      |
| -------- | ---------- | --- | -------- | ----------- |
| 淡入淡出 | `Fade`     |     | 推入     | `Push`      |
| 覆盖     | `Cover`    |     | 楔入     | `Wedge`     |
| 分裂     | `Split`    |     | 百叶窗   | `Blinds`    |
| 轮子     | `Wheel`    |     | 翻转下落 | `FallOver`  |
| 溶解     | `Dissolve` |     | 波纹     | `Ripple`    |
| 粉碎     | `Shred`    |     | 切换     | `Switch`    |
| 揭示     | `Reveal`   |     | 蜂巢     | `Honeycomb` |
| 闪光     | `FLash`    |     | 变形     | `Morph`     |
| 擦除     | `Wipe`     |     | 棋盘     | `Checker`   |
| 梳齿     | `Comb`     |     | 新闻     | `Newsflash` |
| 随机     | `Random`   |     |          |             |

## 高级特效

- **3D效果**: `shape.ThreeD.ExtrusionDepth = 80`
- **图表**: `slide.Charts.Add(sp.ChartType.ColumnClustered, rect, data_range)`
- **表格**: `slide.Shapes.AppendTable(rect, rows, cols)`
- **图片填充**: `shape.Fill.FillType = sp.FillFormatType.Picture`
- **超链接**: `shape.ClickAction.Address = "https://example.com"`
- **渐变边框**: `shape.Line.FillFormat.FillType = sp.FillFormatType.Gradient`
- **形状旋转**: `shape.Rotation = 45`

## 形状库

```python
from scripts.spire.shapes_animations import ShapeLibrary
print(ShapeLibrary.list_shapes())
# 矩形, 圆角矩形, 椭圆, 菱形, 六边形, 八边形, 五边形, 三角形,
# 右箭头, 左箭头, 上箭头, 下箭头, 月亮, 加号, 星形, 心形
```

## 保存

```python
engine.save("output.pptx")
```

## 插入图片

```python
image = engine.add_image(slide, "chart.png", 50, 100, 400, 300)
```

⚠️ **重要**: 图片路径必须是绝对路径或相对于运行目录的正确路径。

## 装饰形状

```python
# 半透明装饰圆形
shape = engine.add_decorative_shape(
    slide, sp.ShapeType.Ellipse,
    x=800, y=20, width=100, height=100,
    fill_color=(59, 130, 246), alpha=30, rotation=0
)

# 旋转的菱形装饰
shape = engine.add_decorative_shape(
    slide, sp.ShapeType.Diamond,
    x=50, y=400, width=60, height=60,
    fill_color=(255, 213, 79), alpha=40, rotation=45
)
```

## 装饰线

```python
# 实线
engine.add_line(slide, 48, 270, 912, 270, (59, 130, 246), width=2)

# 虚线
engine.add_line(slide, 48, 270, 912, 270, (59, 130, 246), width=1.5,
                dash_style=sp.LineDashStyleType.Dash)
```

## 渐变填充形状

```python
# 渐变填充的矩形
shape = engine.add_gradient_shape(
    slide, sp.ShapeType.Rectangle,
    x=0, y=0, width=960, height=6,
    color_start=(59, 130, 246), color_end=(6, 182, 212), alpha=220
)
```

## 禁止使用的失败技术

| 错误用法                    | 正确用法                       |
| --------------------------- | ------------------------------ |
| `ShapeType.Arrow`           | `ShapeType.RightArrow`         |
| `ShapeType.Oval`            | `ShapeType.Ellipse`            |
| `TextParagraph.TextRange`   | `TextParagraph.TextRanges[0]`  |
| `ParagraphCollection.Add()` | `ParagraphCollection.Append()` |
| `ISlide.SaveAsImage(w,h)`   | `ISlide.SaveAsImageByWH(w,h)`  |
| 布尔值设粗体                | `TriState.TTrue/TFalse`        |
