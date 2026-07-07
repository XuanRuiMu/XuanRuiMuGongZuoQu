from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import random
import spire.presentation as sp


class DecorationType(Enum):
    GRADIENT_BAND = "gradient_band"
    GEOMETRIC = "geometric"
    HORIZONTAL_LINE = "horizontal_line"
    VERTICAL_LINE = "vertical_line"
    DIAGONAL_LINE = "diagonal_line"
    DOTS_ARRAY = "dots_array"
    BRACKET = "bracket"
    CROSS_LINES = "cross_lines"
    CONNECTING_LINE = "connecting_line"


@dataclass
class DecorationSpec:
    dec_type: DecorationType
    position: str
    params: Dict = field(default_factory=dict)


GRADIENT_BAND_TEMPLATES = [
    {"position": "top", "height": 4, "color_ratio": 0.8},
    {"position": "bottom", "height": 6, "color_ratio": 0.6},
    {"position": "left", "width": 6, "color_ratio": 0.7},
    {"position": "right", "width": 6, "color_ratio": 0.7},
]

GEOMETRIC_TEMPLATES = [
    {"shape": "circle", "size": 80, "alpha": 40},
    {"shape": "circle", "size": 120, "alpha": 25},
    {"shape": "triangle", "size": 60, "alpha": 35},
    {"shape": "hexagon", "size": 50, "alpha": 30},
    {"shape": "diamond", "size": 60, "alpha": 35},
]

LINE_TEMPLATES = [
    {"style": "solid", "width": 2, "alpha": 180},
    {"style": "dash", "width": 1.5, "alpha": 150},
    {"style": "solid", "width": 3, "alpha": 200},
]

POSITION_MAP = {
    "top": (0, 0),
    "bottom": (0, 540),
    "left": (0, 0),
    "right": (960, 0),
    "top_left": (0, 0),
    "top_right": (960, 0),
    "bottom_left": (0, 540),
    "bottom_right": (960, 540),
    "center": (480, 270),
    "above_title": (0, 0),
    "middle": (0, 270),
}


def assign_decorations(layout_decorations: List[DecorationSpec], used_decoration_keys: List[str]) -> List[DecorationSpec]:
    result = []
    for dec in layout_decorations:
        key = f"{dec.dec_type.value}_{dec.position}"
        if key not in used_decoration_keys:
            result.append(dec)
            used_decoration_keys.append(key)
        else:
            alt = _find_alternative(dec, used_decoration_keys)
            if alt:
                result.append(alt)
                used_decoration_keys.append(f"{alt.dec_type.value}_{alt.position}")
    return result


def _find_alternative(original: DecorationSpec, used_keys: List[str]) -> Optional[DecorationSpec]:
    if original.dec_type == DecorationType.GRADIENT_BAND:
        for template in GRADIENT_BAND_TEMPLATES:
            pos = template["position"]
            key = f"gradient_band_{pos}"
            if key not in used_keys:
                return DecorationSpec(DecorationType.GRADIENT_BAND, pos, template)
    elif original.dec_type == DecorationType.GEOMETRIC:
        for template in GEOMETRIC_TEMPLATES:
            shape = template["shape"]
            for pos_name in ["top_right", "bottom_left", "bottom_right", "top_left"]:
                key = f"geometric_{pos_name}"
                if key not in used_keys:
                    return DecorationSpec(DecorationType.GEOMETRIC, pos_name, {**template, "shape": shape})
    elif original.dec_type in (DecorationType.HORIZONTAL_LINE, DecorationType.VERTICAL_LINE):
        for style in ["solid", "dash"]:
            key = f"{original.dec_type.value}_{original.position}_{style}"
            if key not in used_keys:
                return DecorationSpec(original.dec_type, original.position, {"style": style, "width": 2, "alpha": 150})
    return None


def render_decoration(engine, slide, dec_spec: DecorationSpec, theme_colors: Dict):
    primary = theme_colors.get("primary", (59, 130, 246))
    secondary = theme_colors.get("secondary", (96, 165, 250))
    accent = theme_colors.get("accent", (6, 182, 212))

    if dec_spec.dec_type == DecorationType.GRADIENT_BAND:
        _render_gradient_band(engine, slide, dec_spec, primary, secondary)
    elif dec_spec.dec_type == DecorationType.GEOMETRIC:
        _render_geometric(engine, slide, dec_spec, primary, accent)
    elif dec_spec.dec_type == DecorationType.HORIZONTAL_LINE:
        _render_h_line(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.VERTICAL_LINE:
        _render_v_line(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.DIAGONAL_LINE:
        _render_diagonal_line(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.DOTS_ARRAY:
        _render_dots(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.BRACKET:
        _render_bracket(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.CROSS_LINES:
        _render_cross(engine, slide, dec_spec, primary)
    elif dec_spec.dec_type == DecorationType.CONNECTING_LINE:
        _render_connecting(engine, slide, dec_spec, secondary)


def _render_gradient_band(engine, slide, spec, color1, color2):
    params = spec.params
    pos = spec.position
    if pos == "top":
        h = params.get("height", 4)
        engine.add_gradient_shape(slide, sp.ShapeType.Rectangle, 0, 0, 960, h, color1, color2, alpha=220)
    elif pos == "bottom":
        h = params.get("height", 6)
        engine.add_gradient_shape(slide, sp.ShapeType.Rectangle, 0, 540 - h, 960, h, color1, color2, alpha=220)
    elif pos == "left":
        w = params.get("width", 6)
        engine.add_gradient_shape(slide, sp.ShapeType.Rectangle, 0, 0, w, 540, color1, color2, alpha=220)
    elif pos == "right":
        w = params.get("width", 6)
        engine.add_gradient_shape(slide, sp.ShapeType.Rectangle, 960 - w, 0, w, 540, color1, color2, alpha=220)


def _render_geometric(engine, slide, spec, color, accent):
    params = spec.params
    shape_name = params.get("shape", "circle")
    size = params.get("size", 80)
    alpha = params.get("alpha", 30)
    pos = spec.position

    shape_map = {
        "circle": sp.ShapeType.Ellipse,
        "triangle": sp.ShapeType.Triangle,
        "hexagon": sp.ShapeType.Hexagon,
        "diamond": sp.ShapeType.Diamond,
    }
    shape_type = shape_map.get(shape_name, sp.ShapeType.Ellipse)

    if pos == "top_right":
        x, y = 960 - size - 20, 20
    elif pos == "bottom_left":
        x, y = 20, 540 - size - 20
    elif pos == "bottom_right":
        x, y = 960 - size - 20, 540 - size - 20
    elif pos == "top_left":
        x, y = 20, 20
    elif pos == "center":
        x, y = 480 - size // 2, 270 - size // 2
    else:
        x, y = 960 - size - 20, 20

    engine.add_decorative_shape(slide, shape_type, x, y, size, size, color, alpha=alpha)


def _render_h_line(engine, slide, spec, color):
    params = spec.params
    y = params.get("y", 270)
    style = params.get("style", "solid")
    dash = sp.LineDashStyleType.Dash if style == "dash" else None
    engine.add_line(slide, 48, y, 912, y, color, width=params.get("width", 2), dash_style=dash)


def _render_v_line(engine, slide, spec, color):
    params = spec.params
    x = params.get("x", 30)
    h = params.get("height", 400)
    style = params.get("style", "solid")
    dash = sp.LineDashStyleType.Dash if style == "dash" else None
    engine.add_line(slide, x, 70, x, 70 + h, color, width=params.get("width", 2), dash_style=dash)


def _render_diagonal_line(engine, slide, spec, color):
    engine.add_line(slide, 0, 540, 960, 0, color, width=1, dash_style=sp.LineDashStyleType.Dash)


def _render_dots(engine, slide, spec, color):
    params = spec.params
    rows = params.get("rows", 2)
    cols = params.get("cols", 4)
    pos = spec.position
    dot_size = 6
    gap = 20

    if pos in ("top_right", "right"):
        start_x = 960 - cols * gap - 20
        start_y = 30
    elif pos in ("bottom_left", "left"):
        start_x = 30
        start_y = 540 - rows * gap - 30
    elif pos == "top":
        start_x = 400
        start_y = 30
    else:
        start_x = 30
        start_y = 30

    for r in range(rows):
        for c in range(cols):
            x = start_x + c * gap
            y = start_y + r * gap
            engine.add_decorative_shape(slide, sp.ShapeType.Ellipse, x, y, dot_size, dot_size, color, alpha=120)


def _render_bracket(engine, slide, spec, color):
    params = spec.params
    x = params.get("x", 60)
    h = params.get("height", 300)
    engine.add_line(slide, x, 100, x, 100 + h, color, width=3)
    engine.add_line(slide, x, 100, x + 20, 100, color, width=3)
    engine.add_line(slide, x, 100 + h, x + 20, 100 + h, color, width=3)


def _render_cross(engine, slide, spec, color):
    engine.add_line(slide, 480, 100, 480, 520, color, width=1, dash_style=sp.LineDashStyleType.Dash)
    engine.add_line(slide, 48, 270, 912, 270, color, width=1, dash_style=sp.LineDashStyleType.Dash)


def _render_connecting(engine, slide, spec, color):
    pos = spec.position
    if pos == "horizontal":
        y = spec.params.get("y", 260)
        engine.add_line(slide, 100, y, 860, y, color, width=2, dash_style=sp.LineDashStyleType.Dash)
    elif pos == "circular":
        engine.add_decorative_shape(slide, sp.ShapeType.Ellipse, 330, 150, 300, 240, color, alpha=30)
