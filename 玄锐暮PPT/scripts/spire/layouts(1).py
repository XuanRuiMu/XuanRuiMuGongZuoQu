from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
import random


class ContentType(Enum):
    COVER = "cover"
    TOC = "toc"
    CONTENT = "content"
    DATA = "data"
    FLOW = "flow"
    ENDING = "ending"


class ShapeType(Enum):
    ROUNDED_RECT = "rounded_rect"
    RECT = "rect"
    ELLIPSE = "ellipse"
    HEXAGON = "hexagon"
    DIAMOND = "diamond"
    NO_BORDER = "no_border"
    GRADIENT_BLOCK = "gradient_block"


@dataclass
class ZoneSpec:
    shape: ShapeType
    x: float
    y: float
    w: float
    h: float
    role: str = "content"


@dataclass
class TitleSpec:
    x: float
    y: float
    w: float
    h: float
    alignment: str = "left"
    position: str = "top_left"


@dataclass
class DecorationHint:
    dec_type: str
    position: str
    params: Dict = field(default_factory=dict)


@dataclass
class LayoutSpec:
    name: str
    content_type: ContentType
    title: TitleSpec
    zones: List[ZoneSpec]
    decorations: List[DecorationHint] = field(default_factory=list)
    description: str = ""
    suitable_for: List[str] = field(default_factory=list)


LAYOUT_POOL: List[LayoutSpec] = [
    LayoutSpec(
        name="居中大标题",
        content_type=ContentType.COVER,
        title=TitleSpec(96, 162, 768, 108, "center", "center"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 192, 300, 576, 72, "subtitle"),
        ],
        decorations=[DecorationHint("gradient_band", "bottom", {"height": 6})],
        description="标题居中，副标题在下方卡片中",
        suitable_for=["封面", "首页"],
    ),
    LayoutSpec(
        name="左文右装饰",
        content_type=ContentType.COVER,
        title=TitleSpec(48, 120, 540, 90, "left", "left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 240, 540, 60, "subtitle"),
            ZoneSpec(ShapeType.GRADIENT_BLOCK, 620, 40, 300, 460, "decoration"),
        ],
        decorations=[DecorationHint("vertical_line", "left", {"x": 30, "height": 400})],
        description="左侧标题和副标题，右侧大渐变色块装饰",
        suitable_for=["封面", "首页"],
    ),
    LayoutSpec(
        name="全幅渐变底",
        content_type=ContentType.COVER,
        title=TitleSpec(96, 180, 768, 100, "center", "center"),
        zones=[
            ZoneSpec(ShapeType.NO_BORDER, 96, 310, 768, 60, "subtitle"),
        ],
        decorations=[
            DecorationHint("gradient_band", "top", {"height": 8}),
            DecorationHint("geometric", "bottom_right", {"shape": "circle", "size": 120}),
        ],
        description="全幅渐变背景，标题居中，顶部色带+右下几何装饰",
        suitable_for=["封面", "首页"],
    ),
    LayoutSpec(
        name="底部标题上方视觉",
        content_type=ContentType.COVER,
        title=TitleSpec(96, 380, 768, 80, "center", "bottom"),
        zones=[
            ZoneSpec(ShapeType.GRADIENT_BLOCK, 180, 60, 600, 280, "visual"),
            ZoneSpec(ShapeType.NO_BORDER, 96, 460, 768, 50, "subtitle"),
        ],
        decorations=[DecorationHint("horizontal_line", "above_title", {"y": 370})],
        description="上方大视觉区域，标题在底部",
        suitable_for=["封面", "首页"],
    ),
    LayoutSpec(
        name="分屏式",
        content_type=ContentType.COVER,
        title=TitleSpec(48, 160, 420, 90, "left", "left"),
        zones=[
            ZoneSpec(ShapeType.NO_BORDER, 48, 280, 420, 60, "subtitle"),
            ZoneSpec(ShapeType.GRADIENT_BLOCK, 500, 0, 460, 540, "decoration"),
        ],
        decorations=[DecorationHint("dots_array", "left_bottom", {"rows": 3, "cols": 5})],
        description="左半屏文字，右半屏渐变色块，左下圆点装饰",
        suitable_for=["封面", "首页"],
    ),
    LayoutSpec(
        name="卡片网格目录",
        content_type=ContentType.TOC,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 270, 180, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 345, 100, 270, 180, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 642, 100, 270, 180, "item"),
        ],
        decorations=[DecorationHint("gradient_band", "top", {"height": 4})],
        description="3卡片横排目录，每个卡片内写多行文字（编号+标题+描述）",
        suitable_for=["目录", "议程", "概览"],
    ),
    LayoutSpec(
        name="时间线目录",
        content_type=ContentType.TOC,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 140, 180, 120, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 270, 220, 180, 120, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 300, 180, 120, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 714, 380, 180, 120, "item"),
        ],
        decorations=[DecorationHint("connecting_line", "horizontal", {"y": 340})],
        description="阶梯式排列，用连接线串联",
        suitable_for=["目录", "流程概览"],
    ),
    LayoutSpec(
        name="图标列表目录",
        content_type=ContentType.TOC,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 110, 864, 80, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 210, 864, 80, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 310, 864, 80, "item"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 410, 864, 80, "item"),
        ],
        decorations=[DecorationHint("vertical_line", "left", {"x": 30, "height": 380})],
        description="横条列表式目录，每个条目内写编号+标题+描述",
        suitable_for=["目录", "议程"],
    ),
    LayoutSpec(
        name="左上标题右下三卡片",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 24, 576, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 528, 110, 390, 120, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 528, 260, 390, 120, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 110, 450, 380, "main"),
        ],
        decorations=[DecorationHint("gradient_band", "top", {"height": 4})],
        description="左上标题，左侧大内容区，右侧两张卡片",
        suitable_for=["功能介绍", "特性展示", "概述"],
    ),
    LayoutSpec(
        name="底部标题上方双栏",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 440, 864, 60, "left", "bottom"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 40, 420, 370, "left_col"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 40, 420, 370, "right_col"),
        ],
        decorations=[DecorationHint("horizontal_line", "above_title", {"y": 430})],
        description="标题在底部，上方双栏内容",
        suitable_for=["对比", "双栏内容", "优缺点"],
    ),
    LayoutSpec(
        name="居中标题环形围绕",
        content_type=ContentType.CONTENT,
        title=TitleSpec(180, 20, 600, 60, "center", "top_center"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 120, 400, 180, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 512, 120, 400, 180, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 280, 320, 400, 180, "card"),
        ],
        decorations=[DecorationHint("geometric", "center", {"shape": "circle"})],
        description="居中标题，下方三卡片倒三角排列",
        suitable_for=["核心概念", "三大要素", "围绕主题"],
    ),
    LayoutSpec(
        name="左侧竖排标题右侧内容",
        content_type=ContentType.CONTENT,
        title=TitleSpec(20, 80, 60, 400, "center", "left_vertical"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 120, 40, 800, 220, "main"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 120, 290, 800, 210, "secondary"),
        ],
        decorations=[DecorationHint("vertical_line", "left", {"x": 100, "height": 480})],
        description="左侧竖排标题，右侧上下两个内容区",
        suitable_for=["章节分隔", "重点内容", "分类说明"],
    ),
    LayoutSpec(
        name="右侧标题左侧内容",
        content_type=ContentType.CONTENT,
        title=TitleSpec(540, 40, 380, 80, "right", "top_right"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 40, 460, 460, "main"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 540, 150, 380, 170, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 540, 350, 380, 150, "card"),
        ],
        decorations=[DecorationHint("gradient_band", "right", {"width": 6})],
        description="右侧标题和卡片，左侧大内容区",
        suitable_for=["图文混排", "主次内容"],
    ),
    LayoutSpec(
        name="上下分区",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 864, 180, "upper"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 310, 864, 200, "lower"),
        ],
        decorations=[DecorationHint("horizontal_line", "middle", {"y": 290})],
        description="标题左上，上下两个等宽内容区",
        suitable_for=["两层内容", "概述+详情"],
    ),
    LayoutSpec(
        name="对角线分区",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 400, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 500, 200, "upper_left"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 412, 240, 500, 200, "lower_right"),
        ],
        decorations=[
            DecorationHint("diagonal_line", "center", {}),
            DecorationHint("geometric", "top_right", {"shape": "triangle", "size": 80}),
        ],
        description="对角线排列两个内容区，右上三角装饰",
        suitable_for=["对比", "因果", "前后"],
    ),
    LayoutSpec(
        name="卡片瀑布流",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 270, 400, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 345, 100, 270, 400, "card"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 642, 100, 270, 400, "card"),
        ],
        decorations=[DecorationHint("dots_array", "top_right", {"rows": 2, "cols": 4})],
        description="三栏等高卡片，每个卡片内写多行内容",
        suitable_for=["多要点", "特性列表", "功能展示"],
    ),
    LayoutSpec(
        name="引用式",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.NO_BORDER, 120, 140, 720, 300, "quote"),
        ],
        decorations=[
            DecorationHint("bracket", "left", {"x": 60, "height": 320}),
            DecorationHint("gradient_band", "bottom", {"height": 4}),
        ],
        description="大引号装饰+引用文字区域",
        suitable_for=["引用", "名言", "核心观点"],
    ),
    LayoutSpec(
        name="要点列表式",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 864, 130, "point"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 250, 864, 130, "point"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 400, 864, 110, "point"),
        ],
        decorations=[DecorationHint("vertical_line", "left", {"x": 30, "height": 420})],
        description="3个横条要点，每个要点内写标题+描述",
        suitable_for=["要点", "列表", "步骤"],
    ),
    LayoutSpec(
        name="三栏等分",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 270, 400, "col"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 345, 100, 270, 400, "col"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 642, 100, 270, 400, "col"),
        ],
        decorations=[DecorationHint("gradient_band", "top", {"height": 4})],
        description="三栏等宽内容区",
        suitable_for=["三方面", "对比", "分类"],
    ),
    LayoutSpec(
        name="左图右文",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.RECT, 48, 100, 420, 400, "image"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 100, 420, 400, "text"),
        ],
        decorations=[DecorationHint("geometric", "top_right", {"shape": "hexagon", "size": 50})],
        description="左侧图片区，右侧文字内容",
        suitable_for=["图文", "截图说明", "界面展示"],
    ),
    LayoutSpec(
        name="大数字说明",
        content_type=ContentType.DATA,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.NO_BORDER, 48, 120, 300, 200, "big_number"),
            ZoneSpec(ShapeType.NO_BORDER, 360, 160, 552, 140, "description"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 360, 864, 150, "detail"),
        ],
        decorations=[DecorationHint("gradient_band", "left", {"width": 6})],
        description="左侧大数字+右侧说明+底部详情卡片",
        suitable_for=["数据展示", "关键指标", "统计"],
    ),
    LayoutSpec(
        name="左图表右要点",
        content_type=ContentType.DATA,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.RECT, 48, 100, 520, 400, "chart"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 592, 100, 320, 400, "insight"),
        ],
        decorations=[DecorationHint("vertical_line", "center", {"x": 570, "height": 420})],
        description="左侧图表区，右侧要点卡片（内写多行要点）",
        suitable_for=["数据分析", "图表解读", "报告"],
    ),
    LayoutSpec(
        name="对比双栏",
        content_type=ContentType.DATA,
        title=TitleSpec(48, 20, 864, 60, "center", "top_center"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 420, 400, "left"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 100, 420, 400, "right"),
        ],
        decorations=[DecorationHint("vertical_line", "center", {"x": 470, "height": 420})],
        description="左右双栏对比，中间竖线分隔",
        suitable_for=["对比", "前后", "优劣"],
    ),
    LayoutSpec(
        name="统计卡片行",
        content_type=ContentType.DATA,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 270, 180, "stat"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 345, 100, 270, 180, "stat"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 642, 100, 270, 180, "stat"),
        ],
        decorations=[DecorationHint("gradient_band", "bottom", {"height": 4})],
        description="3个统计卡片横排，每个卡片内写大数字+标签+描述",
        suitable_for=["数据总览", "KPI", "仪表盘"],
    ),
    LayoutSpec(
        name="雷达图解读",
        content_type=ContentType.DATA,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ELLIPSE, 180, 140, 300, 300, "chart"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 540, 120, 380, 320, "insight"),
        ],
        decorations=[DecorationHint("geometric", "top_left", {"shape": "hexagon", "size": 40})],
        description="左侧圆形图表区，右侧解读卡片（内写多行洞察）",
        suitable_for=["雷达图", "评估", "能力分析"],
    ),
    LayoutSpec(
        name="水平流程",
        content_type=ContentType.FLOW,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 160, 160, 120, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 258, 160, 160, 120, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 468, 160, 160, 120, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 678, 160, 160, 120, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 340, 864, 170, "detail"),
        ],
        decorations=[DecorationHint("connecting_line", "horizontal", {"y": 220})],
        description="水平四步骤+底部详情区",
        suitable_for=["流程", "步骤", "阶段"],
    ),
    LayoutSpec(
        name="垂直流程",
        content_type=ContentType.FLOW,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 864, 80, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 200, 864, 80, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 300, 864, 80, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 400, 864, 80, "step"),
        ],
        decorations=[DecorationHint("vertical_line", "left", {"x": 30, "height": 400})],
        description="垂直堆叠的步骤条",
        suitable_for=["流程", "步骤", "层级"],
    ),
    LayoutSpec(
        name="环形流程",
        content_type=ContentType.FLOW,
        title=TitleSpec(48, 20, 864, 60, "center", "top_center"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 120, 200, 100, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 712, 120, 200, 100, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 340, 200, 100, "step"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 712, 340, 200, 100, "step"),
            ZoneSpec(ShapeType.ELLIPSE, 360, 180, 240, 180, "center"),
        ],
        decorations=[DecorationHint("connecting_line", "circular", {})],
        description="四角步骤环绕中心圆形",
        suitable_for=["循环流程", "闭环", "迭代"],
    ),
    LayoutSpec(
        name="架构分层",
        content_type=ContentType.FLOW,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 180, 100, 600, 80, "layer"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 140, 200, 680, 80, "layer"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 100, 300, 760, 80, "layer"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 60, 400, 840, 80, "layer"),
        ],
        decorations=[DecorationHint("gradient_band", "left", {"width": 4})],
        description="金字塔式分层架构，逐层加宽",
        suitable_for=["架构", "分层", "体系"],
    ),
    LayoutSpec(
        name="时间线",
        content_type=ContentType.FLOW,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 200, 180, 120, "event"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 276, 200, 180, 120, "event"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 504, 200, 180, 120, "event"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 732, 200, 180, 120, "event"),
        ],
        decorations=[
            DecorationHint("connecting_line", "horizontal", {"y": 260}),
            DecorationHint("dots_array", "top", {"rows": 1, "cols": 4}),
        ],
        description="水平时间线，事件卡片在线上",
        suitable_for=["时间线", "里程碑", "发展历程"],
    ),
    LayoutSpec(
        name="居中致谢",
        content_type=ContentType.ENDING,
        title=TitleSpec(180, 160, 600, 100, "center", "center"),
        zones=[
            ZoneSpec(ShapeType.NO_BORDER, 180, 300, 600, 60, "subtitle"),
        ],
        decorations=[
            DecorationHint("gradient_band", "bottom", {"height": 6}),
            DecorationHint("geometric", "top_right", {"shape": "circle", "size": 80}),
        ],
        description="居中大标题致谢，底部色带",
        suitable_for=["致谢", "结束"],
    ),
    LayoutSpec(
        name="总结要点致谢",
        content_type=ContentType.ENDING,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 420, 200, "summary"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 100, 420, 200, "summary"),
            ZoneSpec(ShapeType.NO_BORDER, 48, 340, 864, 60, "thanks"),
        ],
        decorations=[DecorationHint("horizontal_line", "middle", {"y": 320})],
        description="上方两个总结卡片，下方致谢文字",
        suitable_for=["总结+致谢", "收尾"],
    ),
    LayoutSpec(
        name="问答页",
        content_type=ContentType.ENDING,
        title=TitleSpec(180, 180, 600, 120, "center", "center"),
        zones=[
            ZoneSpec(ShapeType.ELLIPSE, 380, 340, 200, 120, "qna_icon"),
        ],
        decorations=[
            DecorationHint("geometric", "bottom_left", {"shape": "diamond", "size": 60}),
            DecorationHint("geometric", "top_right", {"shape": "circle", "size": 50}),
        ],
        description="居中Q&A标题，下方圆形图标",
        suitable_for=["问答", "Q&A", "互动"],
    ),
    LayoutSpec(
        name="四象限",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 420, 200, "quadrant"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 100, 420, 200, "quadrant"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 320, 420, 200, "quadrant"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 492, 320, 420, 200, "quadrant"),
        ],
        decorations=[DecorationHint("cross_lines", "center", {})],
        description="2×2四象限布局，十字线分隔",
        suitable_for=["四象限", "矩阵", "分类"],
    ),
    LayoutSpec(
        name="左侧大卡片右侧列表",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "left", "top_left"),
        zones=[
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 100, 500, 400, "main"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 572, 100, 340, 400, "list"),
        ],
        decorations=[DecorationHint("vertical_line", "center", {"x": 550, "height": 420})],
        description="左侧大内容卡片，右侧列表卡片（内写多行要点）",
        suitable_for=["主次内容", "详情+要点"],
    ),
    LayoutSpec(
        name="顶部横幅+下方内容",
        content_type=ContentType.CONTENT,
        title=TitleSpec(48, 20, 864, 60, "center", "top_center"),
        zones=[
            ZoneSpec(ShapeType.GRADIENT_BLOCK, 0, 90, 960, 100, "banner"),
            ZoneSpec(ShapeType.ROUNDED_RECT, 48, 220, 864, 300, "content"),
        ],
        decorations=[DecorationHint("gradient_band", "top", {"height": 4})],
        description="顶部渐变横幅，下方大内容区",
        suitable_for=["章节标题", "分隔页", "重点内容"],
    ),
]


def match_layout(content_type: ContentType, used_layout_names: List[str]) -> Optional[LayoutSpec]:
    available = [l for l in LAYOUT_POOL if l.content_type == content_type and l.name not in used_layout_names]
    if not available:
        available = [l for l in LAYOUT_POOL if l.content_type == content_type]
    if not available:
        available = [l for l in LAYOUT_POOL if l.name not in used_layout_names]
    if not available:
        available = LAYOUT_POOL
    rng = random.Random(len(used_layout_names))
    rng.shuffle(available)
    return available[0]


def get_layouts_by_type(content_type: ContentType) -> List[LayoutSpec]:
    return [l for l in LAYOUT_POOL if l.content_type == content_type]


def list_all_layouts() -> List[LayoutSpec]:
    return LAYOUT_POOL.copy()


SHAPE_TYPE_MAP = {
    ShapeType.ROUNDED_RECT: "round_corner",
    ShapeType.RECT: "rectangle",
    ShapeType.ELLIPSE: "ellipse",
    ShapeType.HEXAGON: "hexagon",
    ShapeType.DIAMOND: "diamond",
    ShapeType.NO_BORDER: "no_border",
    ShapeType.GRADIENT_BLOCK: "gradient_block",
}


def render_layout(engine, slide, layout_spec: LayoutSpec, content: Dict, theme_colors: Dict):
    import spire.presentation as sp

    card_color = theme_colors.get("card_color", (20, 38, 72))
    title_color = theme_colors.get("title_color", (255, 255, 255))
    text_color = theme_colors.get("text_color", (220, 230, 240))
    font_name = theme_colors.get("font_name", "微软雅黑")

    title_text = content.get("title", "")
    if title_text:
        t = layout_spec.title
        title_shape = engine.create_card(
            slide, sp.ShapeType.Rectangle,
            t.x, t.y, t.w, t.h,
            fill_color=(0, 0, 0), alpha=0, shadow=False
        )
        engine.add_text_to_shape(
            title_shape, title_text,
            font_name=font_name, font_size=28,
            bold=True, color=title_color,
            alignment=sp.TextAlignmentType.Left if t.alignment == "left" else sp.TextAlignmentType.Center
        )

    zone_contents = content.get("zones", [])
    for i, zone in enumerate(layout_spec.zones):
        zone_text = zone_contents[i] if i < len(zone_contents) else ""
        if not zone_text:
            continue

        shape_type_key = SHAPE_TYPE_MAP.get(zone.shape, "round_corner")
        sp_shape = _get_spire_shape(shape_type_key)

        if zone.shape == ShapeType.NO_BORDER:
            shape = engine.create_card(
                slide, sp.ShapeType.Rectangle,
                zone.x, zone.y, zone.w, zone.h,
                fill_color=(0, 0, 0), alpha=0, shadow=False
            )
        elif zone.shape == ShapeType.GRADIENT_BLOCK:
            c1 = theme_colors.get("gradient_start", card_color)
            c2 = theme_colors.get("gradient_end", (30, 55, 100))
            shape = engine.add_gradient_shape(
                slide, sp_shape,
                zone.x, zone.y, zone.w, zone.h,
                c1, c2, alpha=180
            )
        else:
            shape = engine.create_card(
                slide, sp_shape,
                zone.x, zone.y, zone.w, zone.h,
                fill_color=card_color, alpha=200, shadow=True
            )

        engine.add_text_to_shape(
            shape, zone_text,
            font_name=font_name, font_size=16,
            bold=False, color=text_color,
            alignment=sp.TextAlignmentType.Left
        )

    return slide


def _get_spire_shape(shape_key: str):
    import spire.presentation as sp
    mapping = {
        "round_corner": sp.ShapeType.RoundCornerRectangle,
        "rectangle": sp.ShapeType.Rectangle,
        "ellipse": sp.ShapeType.Ellipse,
        "hexagon": sp.ShapeType.Hexagon,
        "diamond": sp.ShapeType.Diamond,
    }
    return mapping.get(shape_key, sp.ShapeType.RoundCornerRectangle)
