import spire.presentation as sp
from pathlib import Path
import os
import sys
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


@dataclass
class OverlapIssue:
    slide_index: int
    shape_a: str
    shape_b: str
    overlap_area: Tuple[float, float, float, float]  # (x, y, w, h)
    severity: str  # "critical" | "warning"


class PPTVisualInspector:
    RESOLUTIONS = {
        "default": (1000, 562),
        "hd": (1920, 1080),
        "2k": (2560, 1440),
        "4k": (3840, 2160),
    }

    def __init__(self, ppt_path: str, resolution: str = "default"):
        self.ppt_path = Path(ppt_path)
        if not self.ppt_path.exists():
            raise FileNotFoundError(f"PPT文件不存在: {self.ppt_path}")
        if resolution not in self.RESOLUTIONS:
            raise ValueError(f"不支持的分辨率: {resolution}，可选: {list(self.RESOLUTIONS.keys())}")
        self.resolution = self.RESOLUTIONS[resolution]
        self.output_dir = self.ppt_path.parent / f"_{self.ppt_path.stem}_质检"
        self.output_dir.mkdir(exist_ok=True)

    def detect_overlaps(self, min_overlap_ratio: float = 0.05) -> List[OverlapIssue]:
        """程序化检测幻灯片中元素之间的重叠问题。

        Args:
            min_overlap_ratio: 最小重叠比例阈值，低于此值的不报告（默认5%）

        Returns:
            重叠问题列表
        """
        presentation = sp.Presentation()
        presentation.LoadFromFile(str(self.ppt_path))
        issues = []

        for i in range(presentation.Slides.Count):
            slide = presentation.Slides[i]
            shapes_info = []
            for j in range(slide.Shapes.Count):
                shape = slide.Shapes[j]
                try:
                    bounds = shape.Bounds
                    x, y, w, h = bounds.X, bounds.Y, bounds.Width, bounds.Height
                    name = shape.Name if hasattr(shape, 'Name') else f"Shape_{j}"
                    # 跳过不可见形状（alpha=0的透明矩形通常是文字容器）
                    has_text = False
                    try:
                        if hasattr(shape, 'TextFrame') and shape.TextFrame and shape.TextFrame.Text:
                            has_text = True
                    except:
                        pass
                    shapes_info.append({
                        "name": name,
                        "index": j,
                        "x": x, "y": y, "w": w, "h": h,
                        "has_text": has_text,
                    })
                except:
                    continue

            # 两两检测重叠
            for a_idx in range(len(shapes_info)):
                for b_idx in range(a_idx + 1, len(shapes_info)):
                    a = shapes_info[a_idx]
                    b = shapes_info[b_idx]
                    overlap = self._compute_overlap(a, b)
                    if overlap is None:
                        continue
                    ox, oy, ow, oh = overlap
                    overlap_area = ow * oh
                    a_area = a["w"] * a["h"]
                    b_area = b["w"] * b["h"]
                    min_area = min(a_area, b_area)
                    if min_area == 0:
                        continue
                    ratio = overlap_area / min_area
                    if ratio >= min_overlap_ratio:
                        # 判断严重程度：两个都有文字的重叠更严重
                        severity = "critical" if (a["has_text"] and b["has_text"]) else "warning"
                        issues.append(OverlapIssue(
                            slide_index=i,
                            shape_a=a["name"],
                            shape_b=b["name"],
                            overlap_area=(round(ox, 1), round(oy, 1), round(ow, 1), round(oh, 1)),
                            severity=severity,
                        ))

        presentation.Dispose()
        return issues

    @staticmethod
    def _compute_overlap(a: Dict, b: Dict) -> Optional[Tuple[float, float, float, float]]:
        """计算两个矩形的重叠区域，返回 (x, y, w, h) 或 None。"""
        x1 = max(a["x"], b["x"])
        y1 = max(a["y"], b["y"])
        x2 = min(a["x"] + a["w"], b["x"] + b["w"])
        y2 = min(a["y"] + a["h"], b["y"] + b["h"])
        if x1 < x2 and y1 < y2:
            return (x1, y1, x2 - x1, y2 - y1)
        return None

    def generate_report(self, include_overlap_detection: bool = True) -> dict:
        screenshots = self.export_screenshots()
        file_stat = self.ppt_path.stat()

        overlap_issues = []
        if include_overlap_detection:
            overlap_issues = self.detect_overlaps()

        report = {
            "file_info": {
                "name": self.ppt_path.name,
                "path": str(self.ppt_path),
                "size_kb": round(file_stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "resolution": self.resolution,
            },
            "screenshots": screenshots,
            "overlap_detection": {
                "enabled": include_overlap_detection,
                "total_issues": len(overlap_issues),
                "critical_count": sum(1 for i in overlap_issues if i.severity == "critical"),
                "warning_count": sum(1 for i in overlap_issues if i.severity == "warning"),
                "issues": [
                    {
                        "slide": issue.slide_index + 1,
                        "shape_a": issue.shape_a,
                        "shape_b": issue.shape_b,
                        "overlap_area": issue.overlap_area,
                        "severity": issue.severity,
                    }
                    for issue in overlap_issues
                ],
            },
            "analysis_prompt_templates": {
                "visual_qa": self._build_analysis_prompt(),
            },
        }
        report_path = self.output_dir / "inspection_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report

    def export_screenshots(self) -> list:
        presentation = sp.Presentation()
        presentation.LoadFromFile(str(self.ppt_path))
        screenshots = []
        for i in range(presentation.Slides.Count):
            slide = presentation.Slides[i]
            img_path = self.output_dir / f"slide_{i + 1:02d}.png"
            w, h = self.resolution
            image = slide.SaveAsImageByWH(w, h)
            image.Save(str(img_path))
            image.Dispose()
            size_kb = round(img_path.stat().st_size / 1024, 1)
            screenshots.append({
                "page": i + 1,
                "path": str(img_path),
                "size_kb": size_kb,
            })
        presentation.Dispose()
        return screenshots

    def analyze_with_prompt(self, prompt: str = None) -> str:
        """⚠️ 注意：此方法仅返回提示字符串模板，不执行实际AI视觉分析。
        如需AI视觉分析，请将截图发送给AI agent进行识图。"""
        if prompt is None:
            prompt = self._build_analysis_prompt()
        return prompt

    def _build_analysis_prompt(self) -> str:
        return (
            "请对以下PPT截图进行视觉质量分析，按五个维度评分（1-10分），输出JSON格式。\n\n"
            "评分维度及权重：\n"
            "1. 文字可读性(25%): 字体大小是否合适、文字与背景对比度是否足够、是否存在遮挡或重叠\n"
            "2. 布局平衡性(25%): 元素分布是否均衡、留白是否合理、视觉重心是否稳定\n"
            "3. 配色协调性(20%): 色彩搭配是否和谐、主色调是否统一、是否有过刺眼或冲突的颜色\n"
            "4. 层次清晰度(15%): 信息层级是否分明、重点是否突出、视觉引导是否清晰\n"
            "5. 整体美观度(15%): 整体视觉效果、专业感、设计感\n\n"
            "输出格式：\n"
            "```json\n"
            "{\n"
            '  "文字可读性": {"score": 0, "weight": 0.25, "comment": ""},\n'
            '  "布局平衡性": {"score": 0, "weight": 0.25, "comment": ""},\n'
            '  "配色协调性": {"score": 0, "weight": 0.20, "comment": ""},\n'
            '  "层次清晰度": {"score": 0, "weight": 0.15, "comment": ""},\n'
            '  "整体美观度": {"score": 0, "weight": 0.15, "comment": ""},\n'
            '  "weighted_total": 0,\n'
            '  "overall_comment": ""\n'
            "}\n"
            "```\n\n"
            "请逐页分析后给出汇总评分。"
        )
