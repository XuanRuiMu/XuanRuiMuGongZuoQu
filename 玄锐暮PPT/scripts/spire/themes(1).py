from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any, List

@dataclass
class BackgroundStyle:
    name: str
    name_en: str
    style_type: str
    colors: list
    text_color_hint: str

@dataclass
class ColorScheme:
    name: str
    name_en: str
    primary: Tuple[int,int,int]
    secondary: Tuple[int,int,int]
    accent: Tuple[int,int,int]
    text_primary: Tuple[int,int,int]
    text_secondary: Tuple[int,int,int]
    text_color_hint: str = "dark_bg"

@dataclass
class FontScheme:
    name: str
    name_en: str
    title_font_cn: str
    title_font_en: str
    body_font_cn: str
    body_font_en: str
    title_size: int
    body_size: int

@dataclass
class LayoutTemplate:
    name: str
    name_en: str
    page_type: str
    zones: Dict[str, Any]

@dataclass
class CombinedTheme:
    background: BackgroundStyle
    colors: ColorScheme
    fonts: FontScheme
    layout: LayoutTemplate

BACKGROUND_STYLES = {
    "赛博暗夜": BackgroundStyle("赛博暗夜", "Cyber Dark", "gradient", [(5,8,20), (20,26,62)], "light"),
    "深海商务": BackgroundStyle("深海商务", "Deep Sea Business", "gradient", [(6,18,32), (19,40,66)], "light"),
    "星空紫罗兰": BackgroundStyle("星空紫罗兰", "Starry Violet", "gradient", [(16,16,36), (36,36,66)], "light"),
    "极客黑": BackgroundStyle("极客黑", "Geek Black", "solid", [(10,10,10)], "light"),
    "学术象牙白": BackgroundStyle("学术象牙白", "Academic Ivory", "gradient", [(245,245,240), (235,235,227)], "dark"),
    "暖阳橙": BackgroundStyle("暖阳橙", "Warm Sun", "gradient", [(255,251,235), (255,224,178)], "dark"),
    "樱花粉": BackgroundStyle("樱花粉", "Sakura Pink", "gradient", [(252,228,236), (248,187,208)], "dark"),
    "翡翠绿": BackgroundStyle("翡翠绿", "Emerald Green", "gradient", [(220,237,200), (165,214,167)], "dark"),
}

COLOR_SCHEMES = {
    "霓虹科技": ColorScheme("霓虹科技", "Neon Tech", (0,255,65), (0,212,255), (255,0,255), (255,255,255), (189,254,250), "dark_bg"),
    "商务蓝": ColorScheme("商务蓝", "Business Blue", (59,130,246), (96,165,250), (6,182,212), (255,255,255), (224,230,237), "dark_bg"),
    "尊贵金": ColorScheme("尊贵金", "Premium Gold", (253,208,43), (251,197,30), (254,243,199), (255,255,255), (241,245,249), "dark_bg"),
    "学术蓝": ColorScheme("学术蓝", "Academic Blue", (37,97,190), (59,130,246), (30,64,175), (30,41,59), (51,51,51), "light_bg"),
    "珊瑚活力": ColorScheme("珊瑚活力", "Coral Energy", (249,97,103), (249,231,149), (47,60,126), (47,60,126), (200,200,200), "light_bg"),
    "森林苔藓": ColorScheme("森林苔藓", "Forest Moss", (44,95,45), (151,188,98), (245,245,245), (30,60,30), (80,80,80), "light_bg"),
    "海洋渐变": ColorScheme("海洋渐变", "Ocean Gradient", (6,90,130), (28,114,147), (33,41,92), (33,41,92), (180,200,220), "light_bg"),
    "炭灰极简": ColorScheme("炭灰极简", "Charcoal Minimal", (54,69,79), (242,242,242), (33,33,33), (33,33,33), (180,180,180), "light_bg"),
    "青绿信任": ColorScheme("青绿信任", "Teal Trust", (2,128,144), (0,168,150), (2,195,154), (2,128,144), (180,210,210), "light_bg"),
    "浆果奶油": ColorScheme("浆果奶油", "Berry Cream", (109,46,70), (162,103,105), (236,226,208), (109,46,70), (180,150,160), "light_bg"),
    "鼠尾草": ColorScheme("鼠尾草", "Sage Calm", (132,181,159), (105,162,151), (80,128,142), (80,128,142), (200,210,210), "light_bg"),
    "樱桃大胆": ColorScheme("樱桃大胆", "Cherry Bold", (153,0,17), (252,246,245), (47,60,126), (47,60,126), (200,200,200), "light_bg"),
    "暖赤陶": ColorScheme("暖赤陶", "Warm Terracotta", (184,80,66), (231,232,209), (167,190,174), (184,80,66), (100,100,100), "light_bg"),
    "科技青": ColorScheme("科技青", "Tech Cyan", (0,212,255), (34,211,238), (6,182,212), (0,212,255), (203,213,225), "dark_bg"),
    "数据绿": ColorScheme("数据绿", "Data Green", (100,255,218), (65,191,83), (24,188,156), (100,255,218), (224,224,224), "dark_bg"),
    # === Minecraft 主题专用色（Minecraft 像素风 答辩场景）===
    # 主色基于 Minecraft 草方块、树叶的草绿 + 皮革/橡木/箱子的皮革棕
    "皮革棕": ColorScheme("皮革棕", "Leather Brown", (160, 110, 60), (210, 170, 110), (95, 65, 35), (60, 35, 20), (120, 95, 70), "light_bg"),
    "Minecraft绿": ColorScheme("Minecraft绿", "Minecraft Green", (95, 145, 60), (155, 195, 90), (60, 95, 35), (40, 60, 20), (90, 110, 80), "light_bg"),
}

FONT_SCHEMES = {
    "雅黑现代": FontScheme("雅黑现代", "YaHei Modern", "微软雅黑", "Georgia", "微软雅黑", "Calibri", 36, 18),
    "黑体力量": FontScheme("黑体力量", "Heiti Bold", "黑体", "Arial Black", "微软雅黑", "Calibri", 38, 18),
    "宋体学术": FontScheme("宋体学术", "Songti Academic", "宋体", "Times New Roman", "宋体", "Arial", 32, 18),
    "圆体亲和": FontScheme("圆体亲和", "YuanTi Friendly", "幼圆", "Comic Sans MS", "微软雅黑", "Calibri", 36, 20),
    "行楷艺术": FontScheme("行楷艺术", "XingKai Artistic", "华文行楷", "Palatino Linotype", "微软雅黑", "Calibri Light", 40, 18),
    "琥珀装饰": FontScheme("琥珀装饰", "Hupo Decorative", "华文琥珀", "Impact", "微软雅黑", "Segoe UI", 42, 20),
    "舒体优雅": FontScheme("舒体优雅", "ShuTi Elegant", "方正舒体", "Garamond", "微软雅黑", "Calibri Light", 36, 18),
    "等宽极客": FontScheme("等宽极客", "Mono Geek", "微软雅黑", "Consolas", "微软雅黑", "Consolas", 34, 17),
}

LAYOUT_TEMPLATES = {
    "居中聚焦": LayoutTemplate("居中聚焦", "Center Focus", "cover",
        {"title": {"x_ratio": 0.15, "y_ratio": 0.35, "w_ratio": 0.70, "h_ratio": 0.15},
         "subtitle": {"x_ratio": 0.15, "y_ratio": 0.52, "w_ratio": 0.70, "h_ratio": 0.08}}),
    "列表目录": LayoutTemplate("列表目录", "List TOC", "toc",
        {"title": {"x_ratio": 0.08, "y_ratio": 0.06, "w_ratio": 0.84, "h_ratio": 0.12},
         "content": {"x_ratio": 0.08, "y_ratio": 0.22, "w_ratio": 0.84, "h_ratio": 0.70}}),
    "标题+要点": LayoutTemplate("标题+要点", "Title + Points", "content",
        {"title": {"x_ratio": 0.08, "y_ratio": 0.06, "w_ratio": 0.84, "h_ratio": 0.12},
         "content": {"x_ratio": 0.08, "y_ratio": 0.22, "w_ratio": 0.84, "h_ratio": 0.70}}),
    "左文右图": LayoutTemplate("左文右图", "Text Left Image Right", "data",
        {"title": {"x_ratio": 0.08, "y_ratio": 0.06, "w_ratio": 0.84, "h_ratio": 0.12},
         "text_area": {"x_ratio": 0.08, "y_ratio": 0.22, "w_ratio": 0.45, "h_ratio": 0.70},
         "chart_area": {"x_ratio": 0.57, "y_ratio": 0.22, "w_ratio": 0.35, "h_ratio": 0.70}}),
    "双栏对比": LayoutTemplate("双栏对比", "Two Column Compare", "comparison",
        {"title": {"x_ratio": 0.08, "y_ratio": 0.06, "w_ratio": 0.84, "h_ratio": 0.12},
         "left_col": {"x_ratio": 0.08, "y_ratio": 0.22, "w_ratio": 0.40, "h_ratio": 0.70},
         "right_col": {"x_ratio": 0.52, "y_ratio": 0.22, "w_ratio": 0.40, "h_ratio": 0.70}}),
    "总结致谢": LayoutTemplate("总结致谢", "Summary Thanks", "summary",
        {"title": {"x_ratio": 0.15, "y_ratio": 0.30, "w_ratio": 0.70, "h_ratio": 0.15},
         "content": {"x_ratio": 0.15, "y_ratio": 0.48, "w_ratio": 0.70, "h_ratio": 0.20}}),
}

def combine(background_name: str, color_name: str, font_name: str, layout_name: str) -> CombinedTheme:
    bg = BACKGROUND_STYLES.get(background_name)
    colors = COLOR_SCHEMES.get(color_name)
    fonts = FONT_SCHEMES.get(font_name)
    layout = LAYOUT_TEMPLATES.get(layout_name)
    if not all([bg, colors, fonts, layout]):
        missing = [n for n, v in [(background_name, bg), (color_name, colors), (font_name, fonts), (layout_name, layout)] if not v]
        raise ValueError(f"未找到维度项: {missing}")
    return CombinedTheme(background=bg, colors=colors, fonts=fonts, layout=layout)

def list_backgrounds() -> List[str]:
    return list(BACKGROUND_STYLES.keys())

def list_colors() -> List[str]:
    return list(COLOR_SCHEMES.keys())

def list_fonts() -> List[str]:
    return list(FONT_SCHEMES.keys())

def list_layouts() -> List[str]:
    return list(LAYOUT_TEMPLATES.keys())

def suggest_combination(scenario: str) -> Dict[str, str]:
    scenario_map = {
        "商务汇报": {"background": "深海商务", "color": "商务蓝", "font": "雅黑现代", "layout": "标题+要点"},
        "学术答辩": {"background": "学术象牙白", "color": "学术蓝", "font": "宋体学术", "layout": "标题+要点"},
        "科技发布": {"background": "赛博暗夜", "color": "霓虹科技", "font": "等宽极客", "layout": "左文右图"},
        "产品路演": {"background": "极客黑", "color": "珊瑚活力", "font": "黑体力量", "layout": "居中聚焦"},
        "培训教学": {"background": "暖阳橙", "color": "青绿信任", "font": "圆体亲和", "layout": "标题+要点"},
        "数据分析": {"background": "极客黑", "color": "数据绿", "font": "等宽极客", "layout": "左文右图"},
        "高端发布": {"background": "星空紫罗兰", "color": "尊贵金", "font": "行楷艺术", "layout": "居中聚焦"},
        "创意提案": {"background": "樱花粉", "color": "浆果奶油", "font": "舒体优雅", "layout": "双栏对比"},
    }
    return scenario_map.get(scenario, scenario_map["商务汇报"])

from enum import Enum

class ChapterColorStrategy(Enum):
    UNIFIED = "unified"
    PER_CHAPTER = "per_chapter"

def generate_chapter_colors(strategy, base_color_name, num_chapters):
    base = COLOR_SCHEMES.get(base_color_name)
    if not base:
        raise ValueError(f"配色方案不存在: {base_color_name}")
    
    if strategy == ChapterColorStrategy.UNIFIED:
        return [base] * num_chapters
    
    all_schemes = list(COLOR_SCHEMES.values())
    compatible = [s for s in all_schemes if s.text_color_hint == base.text_color_hint]
    
    if len(compatible) < num_chapters:
        compatible = all_schemes
    
    step = max(1, len(compatible) // num_chapters)
    selected = []
    base_idx = next(i for i, s in enumerate(compatible) if s.name == base.name)
    for i in range(num_chapters):
        idx = (base_idx + i * step) % len(compatible)
        selected.append(compatible[idx])
    
    return selected
