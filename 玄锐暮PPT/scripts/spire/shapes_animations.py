import spire.presentation as sp
import random
from typing import List, Tuple, Dict, Any


class ShapeLibrary:
    SHAPES = [
        ("矩形", sp.ShapeType.Rectangle),
        ("圆角矩形", sp.ShapeType.RoundCornerRectangle),
        ("椭圆", sp.ShapeType.Ellipse),
        ("菱形", sp.ShapeType.Diamond),
        ("六边形", sp.ShapeType.Hexagon),
        ("八边形", sp.ShapeType.Octagon),
        ("五边形", sp.ShapeType.Pentagon),
        ("三角形", sp.ShapeType.Triangle),
        ("右箭头", sp.ShapeType.RightArrow),
        ("左箭头", sp.ShapeType.LeftArrow),
        ("上箭头", sp.ShapeType.UpArrow),
        ("下箭头", sp.ShapeType.DownArrow),
        ("月亮", sp.ShapeType.Moon),
        ("加号", sp.ShapeType.Plus),
        ("星形", sp.ShapeType.FivePointedStar),
        ("心形", sp.ShapeType.Heart),
    ]


class AnimationLibrary:
    EFFECTS = [
        ("淡入", sp.AnimationEffectType.Fade),
        ("飞入", sp.AnimationEffectType.Fly),
        ("浮入", sp.AnimationEffectType.Float),
        ("缩放", sp.AnimationEffectType.Zoom),
        ("旋转", sp.AnimationEffectType.Spin),
        ("弹跳", sp.AnimationEffectType.Bounce),
        ("展开", sp.AnimationEffectType.Expand),
        ("条纹", sp.AnimationEffectType.Strips),
        ("擦除", sp.AnimationEffectType.Wipe),
        ("分裂", sp.AnimationEffectType.Split),
        ("轮子", sp.AnimationEffectType.Wheel),
        ("棋盘", sp.AnimationEffectType.Checkerboard),
        ("百叶窗", sp.AnimationEffectType.Blinds),
        ("溶解", sp.AnimationEffectType.Dissolve),
        ("菱形", sp.AnimationEffectType.Diamond),
        ("圆圈", sp.AnimationEffectType.Circle),
        ("出现", sp.AnimationEffectType.Appear),
        ("方框", sp.AnimationEffectType.Box),
        ("梳齿", sp.AnimationEffectType.Comb),
        ("闪烁", sp.AnimationEffectType.FlashOnce),
        ("窥视", sp.AnimationEffectType.Peek),
    ]

    TRANSITIONS = [
        ("淡入淡出", sp.TransitionType.Fade),
        ("推入", sp.TransitionType.Push),
        ("覆盖", sp.TransitionType.Cover),
        ("楔入", sp.TransitionType.Wedge),
        ("分裂", sp.TransitionType.Split),
        ("百叶窗", sp.TransitionType.Blinds),
        ("轮子", sp.TransitionType.Wheel),
        ("翻转下落", sp.TransitionType.FallOver),
        ("溶解", sp.TransitionType.Dissolve),
        ("波纹", sp.TransitionType.Ripple),
        ("粉碎", sp.TransitionType.Shred),
        ("切换", sp.TransitionType.Switch),
        ("揭示", sp.TransitionType.Reveal),
        ("蜂巢", sp.TransitionType.Honeycomb),
        ("闪光", sp.TransitionType.FLash),
        ("变形", sp.TransitionType.Morph),
        ("擦除", sp.TransitionType.Wipe),
        ("棋盘", sp.TransitionType.Checker),
        ("梳齿", sp.TransitionType.Comb),
        ("新闻", sp.TransitionType.Newsflash),
        ("随机", sp.TransitionType.Random),
    ]

    def get_effect(self, index):
        if 0 <= index < len(self.EFFECTS):
            return self.EFFECTS[index]
        return self.EFFECTS[0]

    def get_transition(self, index):
        if 0 <= index < len(self.TRANSITIONS):
            return self.TRANSITIONS[index]
        return self.TRANSITIONS[0]

    def list_effects(self):
        return [(i, name, effect_type) for i, (name, effect_type) in enumerate(self.EFFECTS)]

    def list_transitions(self):
        return [(i, name, trans_type) for i, (name, trans_type) in enumerate(self.TRANSITIONS)]


def assign_animations(num_slides, seed=42):
    """为每页分配一个入场动画效果和页面切换效果。

    ⚠️ 此函数仅返回每页1个动画效果。如需为每页的多个元素分配动画，
    请使用 assign_slide_animations() 函数。

    Args:
        num_slides: 幻灯片数量
        seed: 随机种子

    Returns:
        List[Tuple[effect_type, transition_type]]: 每页一个(effect, transition)元组
    """
    rng = random.Random(seed)
    lib = AnimationLibrary()

    effects = [eff for _, eff in lib.EFFECTS]
    transitions = [tr for _, tr in lib.TRANSITIONS]

    rng.shuffle(effects)
    rng.shuffle(transitions)

    result = []
    for i in range(num_slides):
        effect = effects[i % len(effects)]
        transition = transitions[i % len(transitions)]
        result.append((effect, transition))

    return result


def assign_slide_animations(shapes_by_role: Dict[str, List[Any]], seed=None) -> Dict[str, List[Any]]:
    """为一页中的所有元素按角色分组分配入场动画。

    核心原则：同级元素（相同role）按顺序拥有相同或不同的入场动画。
    每个元素都必须有动画，不能遗漏。

    Args:
        shapes_by_role: 按角色分组的形状字典，例如：
            {
                "title": [title_shape],
                "card": [card1, card2, card3],
                "decoration": [deco1, deco2],
            }
            值为形状对象列表（传入什么就原样返回，用于后续 engine.add_animation 调用）

        seed: 随机种子（可选，不传则每页不同）

    Returns:
        Dict[str, List[Tuple[shape, effect_type]]]: 按角色分组，每个元素对应的动画效果
            例如：
            {
                "title": [(title_shape, Fade)],
                "card": [(card1, Fly), (card2, Fly), (card3, Fly)],
                "decoration": [(deco1, Zoom), (deco2, Zoom)],
            }

    动画分配规则：
    - 同级元素（相同role）使用相同的入场动画效果，按顺序依次触发
    - 不同级元素使用不同的入场动画效果
    - 21种入场动画按角色轮换分配
    """
    lib = AnimationLibrary()
    all_effects = [eff for _, eff in lib.EFFECTS]

    rng = random.Random(seed) if seed is not None else random.Random()

    # 为每个角色选择一种动画效果
    available_effects = list(all_effects)
    rng.shuffle(available_effects)

    result = {}
    effect_idx = 0

    for role, shapes in shapes_by_role.items():
        # 每个角色选一种动画效果
        chosen_effect = available_effects[effect_idx % len(available_effects)]
        effect_idx += 1

        # 该角色下的所有元素都使用同一种动画
        role_animations = []
        for shape in shapes:
            role_animations.append((shape, chosen_effect))

        result[role] = role_animations

    return result


def apply_slide_animations(engine, slide, animations_map: Dict[str, List[Tuple[Any, Any]]]):
    """将 assign_slide_animations 的结果应用到幻灯片上。

    Args:
        engine: PPTEngine 实例
        slide: 幻灯片对象
        animations_map: assign_slide_animations 的返回值
    """
    for role, anim_list in animations_map.items():
        for shape, effect_type in anim_list:
            try:
                engine.add_animation(slide, shape, effect_type)
            except Exception as e:
                print(f"动画添加失败 [{role}]: {e}")
