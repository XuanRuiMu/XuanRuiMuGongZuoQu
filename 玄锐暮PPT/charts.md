# 图表生成

## 快速使用

```python
from scripts.charts.auto_charts import AutoChartGenerator, ChartData, ChartConfig, create_chart_image

# 方式1：便捷函数
img_bytes = create_chart_image("bar", {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [120, 190, 150, 230],
    "title": "季度营收"
})

# 方式2：完整配置
generator = AutoChartGenerator(ChartConfig(dpi=200, show_value=True))
data = ChartData(labels=["Q1", "Q2", "Q3", "Q4"], values=[120, 190, 150, 230], series_name="2024营收")
img_bytes = generator.generate_bar_chart(data, output_path="chart_1200x750.png")
```

## 支持的图表类型

| 类型        | 方法                                       | 说明                           |
| ----------- | ------------------------------------------ | ------------------------------ |
| 柱状图      | `generate_bar_chart(data, chart_type)`     | vertical/horizontal/grouped    |
| 折线图      | `generate_line_chart(data, trend_line)`    | 可选趋势线                     |
| 饼图/环形图 | `generate_pie_chart(data, donut, explode)` | donut=环形, explode=突出最大值 |
| 雷达图      | `generate_radar_chart(categories, values)` | 多维评估(0-100)                |
| 对比图      | `generate_comparison_chart(data)`          | 双系列柱状对比                 |

## 配色方案

```python
ChartConfig(color_scheme="professional")  # professional/vibrant/warm/cool/monochrome
```

## CJK中文支持

已内置中文字体配置（SimHei/Microsoft YaHei），无需额外设置。

## 与Spire配合

```python
# 图表图片插入Spire幻灯片
shape = slide.Shapes.AppendShape(sp.ShapeType.Rectangle, rect)
shape.Fill.FillType = sp.FillFormatType.Picture
shape.Fill.PictureFill.Picture.Url = "chart.png"
```
