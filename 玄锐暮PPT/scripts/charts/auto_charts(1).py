import io
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


@dataclass
class ChartData:
    labels: List[str]
    values: List[float]
    series_name: str = "系列1"
    secondary_values: Optional[List[float]] = None


@dataclass
class ChartConfig:
    width: float = 10
    height: float = 6
    dpi: int = 150
    title: str = ""
    title_size: int = 16
    label_size: int = 12
    show_value: bool = True
    color_scheme: str = "professional"


class ColorScheme:
    PROFESSIONAL = ["#2E5090", "#4A7FB5", "#6BAED6", "#9ECAE1", "#C6DBEF", "#2171B5", "#08519C", "#08306B"]
    VIBRANT = ["#E63946", "#F4A261", "#2A9D8F", "#264653", "#E9C46A", "#F77F00", "#D62828", "#023E8A"]
    WARM = ["#D62828", "#F77F00", "#FCBF49", "#EAE2B7", "#F4A261", "#E76F51", "#D4A373", "#CCD5AE"]
    COOL = ["#023E8A", "#0077B6", "#0096C7", "#00B4D8", "#48CAE4", "#90E0EF", "#ADE8F4", "#CAF0F8"]
    MONOCHROME = ["#1B1B1B", "#3D3D3D", "#5F5F5F", "#818181", "#A3A3A3", "#C5C5C5", "#E0E0E0", "#F5F5F5"]

    _SCHEMES = {
        "professional": PROFESSIONAL,
        "vibrant": VIBRANT,
        "warm": WARM,
        "cool": COOL,
        "monochrome": MONOCHROME,
    }

    @classmethod
    def get_colors(cls, scheme: str, n: int) -> List[str]:
        base = cls._SCHEMES.get(scheme, cls.PROFESSIONAL)
        if n <= len(base):
            return base[:n]
        colors = []
        for i in range(n):
            idx = i % len(base)
            colors.append(base[idx])
        return colors


class AutoChartGenerator:
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()

    def generate_bar_chart(self, data: ChartData, chart_type: str = "vertical", output_path: str = None) -> bytes:
        fig, ax = plt.subplots(figsize=(self.config.width, self.config.height), dpi=self.config.dpi)
        colors = ColorScheme.get_colors(self.config.color_scheme, len(data.labels))
        x = np.arange(len(data.labels))

        if chart_type == "horizontal":
            bars = ax.barh(x, data.values, color=colors)
            ax.set_yticks(x)
            ax.set_yticklabels(data.labels, fontsize=self.config.label_size)
            if self.config.show_value:
                for bar, val in zip(bars, data.values):
                    ax.text(bar.get_width() + max(data.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                            f"{val}", va="center", fontsize=self.config.label_size - 2)
        else:
            bars = ax.bar(x, data.values, color=colors)
            ax.set_xticks(x)
            ax.set_xticklabels(data.labels, fontsize=self.config.label_size)
            if self.config.show_value:
                for bar, val in zip(bars, data.values):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(data.values) * 0.01,
                            f"{val}", ha="center", va="bottom", fontsize=self.config.label_size - 2)

        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.title_size)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        return self._save_figure(fig, output_path)

    def generate_line_chart(self, data: ChartData, trend_line: bool = False, output_path: str = None) -> bytes:
        fig, ax = plt.subplots(figsize=(self.config.width, self.config.height), dpi=self.config.dpi)
        colors = ColorScheme.get_colors(self.config.color_scheme, 2)
        x = np.arange(len(data.labels))

        ax.plot(x, data.values, marker="o", color=colors[0], linewidth=2, markersize=6, label=data.series_name)
        if data.secondary_values is not None:
            ax.plot(x, data.secondary_values, marker="s", color=colors[1], linewidth=2, markersize=6, label="对比系列")

        if trend_line:
            z = np.polyfit(x, data.values, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), linestyle="--", color=colors[0], alpha=0.5, label="趋势线")

        ax.set_xticks(x)
        ax.set_xticklabels(data.labels, fontsize=self.config.label_size)
        if self.config.show_value:
            for xi, val in zip(x, data.values):
                ax.text(xi, val + max(data.values) * 0.02, f"{val}", ha="center", fontsize=self.config.label_size - 2)

        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.title_size)
        ax.legend(fontsize=self.config.label_size)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        return self._save_figure(fig, output_path)

    def generate_pie_chart(self, data: ChartData, donut: bool = False, explode: bool = False, output_path: str = None) -> bytes:
        fig, ax = plt.subplots(figsize=(self.config.width, self.config.height), dpi=self.config.dpi)
        colors = ColorScheme.get_colors(self.config.color_scheme, len(data.labels))

        explode_vals = None
        if explode:
            explode_vals = [0.05] * len(data.labels)
            max_idx = data.values.index(max(data.values))
            explode_vals[max_idx] = 0.12

        wedges, texts, autotexts = ax.pie(
            data.values,
            labels=data.labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            explode=explode_vals,
            pctdistance=0.75 if donut else 0.6,
            textprops={"fontsize": self.config.label_size},
        )

        if donut:
            centre_circle = plt.Circle((0, 0), 0.50, fc="white")
            ax.add_artist(centre_circle)

        for autotext in autotexts:
            autotext.set_fontsize(self.config.label_size - 2)

        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.title_size)
        plt.tight_layout()
        return self._save_figure(fig, output_path)

    def generate_radar_chart(self, categories: List[str], values: List[float], title: str = "", output_path: str = None) -> bytes:
        n = len(categories)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles_plot = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(self.config.width, self.config.height), dpi=self.config.dpi, subplot_kw=dict(polar=True))
        colors = ColorScheme.get_colors(self.config.color_scheme, 1)
        ax.plot(angles_plot, values_plot, "o-", linewidth=2, color=colors[0])
        ax.fill(angles_plot, values_plot, alpha=0.25, color=colors[0])
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=self.config.label_size)
        ax.set_ylim(0, max(values) * 1.15)

        chart_title = title or self.config.title
        if chart_title:
            ax.set_title(chart_title, fontsize=self.config.title_size, pad=20)
        plt.tight_layout()
        return self._save_figure(fig, output_path)

    def generate_comparison_chart(self, data: ChartData, output_path: str = None) -> bytes:
        fig, ax = plt.subplots(figsize=(self.config.width, self.config.height), dpi=self.config.dpi)
        colors = ColorScheme.get_colors(self.config.color_scheme, 2)
        x = np.arange(len(data.labels))
        width = 0.35

        if data.secondary_values is None:
            raise ValueError("对比图需要提供 secondary_values")

        bars1 = ax.bar(x - width / 2, data.values, width, label=data.series_name, color=colors[0])
        bars2 = ax.bar(x + width / 2, data.secondary_values, width, label="对比系列", color=colors[1])

        ax.set_xticks(x)
        ax.set_xticklabels(data.labels, fontsize=self.config.label_size)
        ax.legend(fontsize=self.config.label_size)

        if self.config.show_value:
            for bar, val in zip(bars1, data.values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(data.values) * 0.01,
                        f"{val}", ha="center", va="bottom", fontsize=self.config.label_size - 2)
            for bar, val in zip(bars2, data.secondary_values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(data.secondary_values) * 0.01,
                        f"{val}", ha="center", va="bottom", fontsize=self.config.label_size - 2)

        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.title_size)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        return self._save_figure(fig, output_path)

    def _save_figure(self, fig, output_path: str = None) -> bytes:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=self.config.dpi, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_bytes = buf.getvalue()
        buf.close()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(img_bytes)

        return img_bytes


def create_chart_image(chart_type: str, data_dict: Dict[str, Any], config_dict: Dict[str, Any] = None) -> bytes:
    config = ChartConfig(**config_dict) if config_dict else ChartConfig()
    generator = AutoChartGenerator(config)
    data = ChartData(
        labels=data_dict.get("labels", []),
        values=data_dict.get("values", []),
        series_name=data_dict.get("series_name", "系列1"),
        secondary_values=data_dict.get("secondary_values"),
    )

    chart_type = chart_type.lower()
    if chart_type in ("bar", "bar_vertical"):
        return generator.generate_bar_chart(data, chart_type="vertical")
    elif chart_type == "bar_horizontal":
        return generator.generate_bar_chart(data, chart_type="horizontal")
    elif chart_type == "line":
        return generator.generate_line_chart(data)
    elif chart_type == "line_trend":
        return generator.generate_line_chart(data, trend_line=True)
    elif chart_type == "pie":
        return generator.generate_pie_chart(data)
    elif chart_type == "donut":
        return generator.generate_pie_chart(data, donut=True)
    elif chart_type == "pie_explode":
        return generator.generate_pie_chart(data, explode=True)
    elif chart_type == "radar":
        return generator.generate_radar_chart(data.labels, data.values, title=config.title)
    elif chart_type == "comparison":
        return generator.generate_comparison_chart(data)
    else:
        raise ValueError(f"不支持的图表类型: {chart_type}")
