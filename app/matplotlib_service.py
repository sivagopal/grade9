import math
import re
from urllib.error import URLError
from urllib.request import urlopen
from fractions import Fraction
from io import BytesIO

from PIL import Image

from app.paths import APP_ROOT, MATPLOTLIB_CONFIG_DIR


NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
COLOR_COUNT_PATTERN = re.compile(r"(\d+)\s*(red|blue|yellow|green|purple|orange)\b", flags=re.IGNORECASE)
COLOR_PALETTE = {
    "red": "#d62839",
    "blue": "#2a6fdb",
    "yellow": "#f4c542",
    "green": "#2b9348",
    "purple": "#7b2cbf",
    "orange": "#f77f00",
}
LIVE_ASSET_SUBJECTS = {"Maths", "Further Maths"}


def _import_plt():
    import os

    os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CONFIG_DIR))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def enrich_questions_with_dynamic_assets(questions):
    enriched = []
    for question in questions:
        item = dict(question)
        if item.get("subject") in LIVE_ASSET_SUBJECTS and not item.get("asset_path") and question_supports_live_asset(item):
            item["asset_dynamic"] = True
        enriched.append(item)
    return enriched


def question_supports_live_asset(question):
    if question.get("subject") not in LIVE_ASSET_SUBJECTS:
        return False
    return _choose_renderer(question) is not None


def render_asset_png_bytes(question):
    renderer = _choose_renderer(question)
    if renderer is None:
        return None

    plt = _import_plt()
    fig = renderer(question, plt)
    if fig is None:
        return None
    output = BytesIO()
    fig.savefig(output, format="PNG", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    output.seek(0)
    return output.getvalue()


def load_question_asset_image(question):
    asset_path = question.get("asset_path")
    if asset_path:
        if isinstance(asset_path, str) and asset_path.startswith(("http://", "https://")):
            try:
                with urlopen(asset_path, timeout=6) as response:
                    content_type = str(response.headers.get("Content-Type", "")).lower()
                    if "image" not in content_type and not asset_path.lower().split("?", 1)[0].endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
                        return None
                    image = Image.open(BytesIO(response.read()))
                    if image.mode not in {"RGB", "L"}:
                        image = image.convert("RGB")
                    return image
            except (OSError, URLError, ValueError):
                return None
        absolute = APP_ROOT / "static" / asset_path
        if absolute.exists():
            image = Image.open(absolute)
            if image.mode not in {"RGB", "L"}:
                image = image.convert("RGB")
            return image

    image_bytes = render_asset_png_bytes(question)
    if image_bytes is None:
        return None
    image = Image.open(BytesIO(image_bytes))
    if image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")
    return image


def _choose_renderer(question):
    topic = (question.get("topic") or "").lower()
    text = (question.get("question") or "").lower()

    if "coordinate geometry" in topic and _has_coordinate_geometry_signal(text):
        return _render_coordinate_geometry
    if ("statistics" in topic or "probability" in topic) and _has_probability_or_statistics_signal(text):
        return _render_statistics_probability
    if ("graph" in topic or "graph" in text) and _has_graph_signal(text):
        return _render_graph
    if ("transform" in topic or "rotation" in topic or "reflection" in topic) and _has_transformation_signal(text):
        return _render_transformation
    return None


def _has_coordinate_geometry_signal(text):
    if _parse_line_equation(text):
        return True
    coordinate_pairs = re.findall(r"\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)", text)
    return len(coordinate_pairs) >= 2


def _has_probability_or_statistics_signal(text):
    color_counts = _extract_color_counts(text)
    if len(color_counts) >= 2:
        return True
    if "probability" in text:
        numbers = [abs(float(value)) for value in _extract_numbers(text) if float(value) != 0]
        return len(numbers) >= 3
    return False


def _has_graph_signal(text):
    if _parse_line_equation(text):
        return True
    coordinate_pairs = re.findall(r"\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)", text)
    return len(coordinate_pairs) >= 2


def _has_transformation_signal(text):
    coordinate_pairs = re.findall(r"\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)", text)
    has_transform_word = any(word in text for word in ["rotate", "rotation", "reflect", "reflection", "translate", "translation"])
    return has_transform_word and len(coordinate_pairs) >= 2


def _style_axes(ax, title, xlim=None, ylim=None, equal=False):
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if equal:
        ax.set_aspect("equal", adjustable="box")


def _extract_numbers(text):
    values = []
    for match in NUMBER_PATTERN.findall(text):
        try:
            number = float(match)
        except ValueError:
            continue
        if number.is_integer():
            values.append(int(number))
        else:
            values.append(number)
    return values


def _fraction_text(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _extract_color_counts(text):
    counts = []
    for count, color in COLOR_COUNT_PATTERN.findall(text or ""):
        counts.append((color.lower(), int(count)))
    return counts


def _parse_rectangle_dimensions(text):
    length_match = re.search(r"length\s+(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
    width_match = re.search(r"width\s+(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
    if length_match and width_match:
        return float(length_match.group(1)), float(width_match.group(1))
    numbers = [value for value in _extract_numbers(text) if value > 0]
    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    return 8.0, 5.0


def _parse_cuboid_dimensions(text):
    numbers = [float(value) for value in _extract_numbers(text) if value > 0]
    if len(numbers) >= 3:
        return numbers[0], numbers[1], numbers[2]
    return 6.0, 4.0, 3.0


def _parse_line_equation(text):
    compact = text.replace(" ", "")
    match = re.search(r"y=([+-]?\d+(?:\.\d+)?)x([+-]\d+(?:\.\d+)?)?", compact)
    if match:
        slope = float(match.group(1))
        intercept = float(match.group(2) or 0)
        return slope, intercept
    match = re.search(r"y=x([+-]\d+(?:\.\d+)?)?", compact)
    if match:
        return 1.0, float(match.group(1) or 0)
    match = re.search(r"y=-x([+-]\d+(?:\.\d+)?)?", compact)
    if match:
        return -1.0, float(match.group(1) or 0)
    return None


def _render_coordinate_geometry(question, plt):
    slope_intercept = _parse_line_equation(question.get("question", ""))
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    if slope_intercept:
        slope, intercept = slope_intercept
        xs = [x / 2 for x in range(-12, 13)]
        ys = [slope * x + intercept for x in xs]
        ax.plot(xs, ys, linewidth=2.2, color="#177e89")
    else:
        points = [value for value in _extract_numbers(question.get("question", ""))[:4]]
        if len(points) >= 4:
            x1, y1, x2, y2 = points[:4]
            ax.plot([x1, x2], [y1, y2], linewidth=2.2, color="#177e89")
            ax.scatter([x1, x2], [y1, y2], color="#084c61", s=45)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    _style_axes(ax, "Coordinate Geometry", xlim=(-8, 8), ylim=(-8, 8), equal=True)
    return fig


def _render_statistics_probability(question, plt):
    text = question.get("question", "")
    numbers = [abs(float(value)) for value in _extract_numbers(text) if float(value) != 0][:6]
    probability_context = (question.get("topic", "").lower() + " " + text.lower())
    color_counts = _extract_color_counts(text)
    if "probability" in probability_context and color_counts:
        if "without replacement" in probability_context or "two counters" in probability_context or "two balls" in probability_context:
            fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8))
            _render_counter_bag_axis(axes[0], plt, color_counts, title="Bag Model")
            _render_tree_axis(axes[1], color_counts, title="Without Replacement Tree")
        else:
            fig, ax = plt.subplots(figsize=(6.6, 5.2))
            _render_counter_bag_axis(ax, plt, color_counts, title="Bag Model")
            total = sum(count for _, count in color_counts)
            summary = "Total = " + str(total) + "    " + "    ".join(
                f"P({color[0].upper()}) = {_fraction_text(Fraction(count, total))}"
                for color, count in color_counts[:3]
            )
            ax.text(3.0, 0.1, summary, ha="center", va="bottom", fontsize=8.5, color="#38404a")
    elif "probability" in probability_context:
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        weights = numbers[:4] if len(numbers) >= 3 else [1, 2, 3, 4]
        labels = [f"O{i + 1}" for i in range(len(weights))]
        ax.pie(weights, labels=labels, autopct=lambda pct: f"{pct:.0f}%")
        ax.set_title("Probability Model")
    else:
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        values = numbers[:5] if len(numbers) >= 4 else [3, 5, 7, 9, 11]
        labels = [chr(ord("A") + i) for i in range(len(values))]
        ax.bar(labels, values, color="#4d908e")
        ax.set_ylabel("Value")
        _style_axes(ax, "Statistics Snapshot")
    return fig


def _render_counter_bag_axis(ax, plt, color_counts, title="Bag Model"):
    ax.set_title(title)
    ax.set_xlim(-0.2, 6.2)
    ax.set_ylim(-0.1, 7.1)
    ax.axis("off")
    bag_x = [0.8, 5.2, 5.6, 5.1, 4.9, 1.1, 0.9, 0.4, 0.8]
    bag_y = [1.1, 1.1, 5.2, 6.2, 6.6, 6.6, 6.2, 5.2, 1.1]
    ax.fill(bag_x, bag_y, color="#f6efe1", alpha=0.96, edgecolor="#8c6d46", linewidth=2.2)
    positions = [
        (1.45, 5.4), (2.35, 5.35), (3.25, 5.45), (4.15, 5.35),
        (1.25, 4.3), (2.15, 4.2), (3.05, 4.25), (3.95, 4.15), (4.75, 4.2),
        (1.55, 3.2), (2.45, 3.1), (3.35, 3.15), (4.25, 3.05),
        (1.8, 2.0), (2.7, 2.0), (3.6, 1.95), (4.45, 2.05),
    ]
    index = 0
    legend_lines = []
    for color_name, count in color_counts:
        legend_lines.append(f"{count} {color_name}")
        for _ in range(count):
            x_coord, y_coord = positions[index % len(positions)]
            index += 1
            circle = plt.Circle(
                (x_coord, y_coord),
                0.28,
                facecolor=COLOR_PALETTE.get(color_name, "#577590"),
                edgecolor="#24303e" if color_name != "yellow" else "#8d6e00",
                linewidth=1.4,
            )
            ax.add_patch(circle)
    ax.text(3.0, 0.45, " | ".join(legend_lines), ha="center", fontsize=9, color="#47311d")


def _render_tree_axis(ax, color_counts, title="Tree Diagram"):
    total = sum(count for _, count in color_counts[:3])
    counts = color_counts[:3]
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    root_x, first_x, second_x = 0.08, 0.42, 0.82
    first_y = [0.78, 0.5, 0.22]
    second_y = {
        0: [0.88, 0.76, 0.64],
        1: [0.6, 0.48, 0.36],
        2: [0.32, 0.2, 0.08],
    }
    ax.text(root_x - 0.02, 0.95, "1st draw", fontsize=9, fontweight="bold")
    ax.text(first_x - 0.02, 0.95, "2nd draw", fontsize=9, fontweight="bold")
    for first_index, (first_color, first_count) in enumerate(counts):
        y1 = first_y[first_index]
        first_probability = Fraction(first_count, total)
        ax.plot([root_x, first_x], [0.5, y1], color="#5c677d", linewidth=1.6)
        ax.text(root_x + 0.02, (0.5 + y1) / 2 + 0.025, first_color.title(), fontsize=8)
        ax.text(root_x + 0.015, (0.5 + y1) / 2 - 0.045, _fraction_text(first_probability), fontsize=7.5, color="#33415c")
        remaining_total = total - 1
        for second_index, (second_color, second_count) in enumerate(counts):
            remaining_count = second_count - 1 if second_color == first_color else second_count
            y2 = second_y[first_index][second_index]
            second_probability = Fraction(max(remaining_count, 0), remaining_total)
            ax.plot([first_x, second_x], [y1, y2], color="#5c677d", linewidth=1.25)
            ax.text(first_x + 0.015, (y1 + y2) / 2 + 0.018, second_color.title(), fontsize=7)
            ax.text(first_x + 0.012, (y1 + y2) / 2 - 0.04, _fraction_text(second_probability), fontsize=7, color="#33415c")
            ax.text(second_x + 0.015, y2 - 0.01, f"{first_color[0].upper()}{second_color[0].upper()}", fontsize=7)


def _render_graph(question, plt):
    text = question.get("question", "")
    equation = _parse_line_equation(text)
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    if equation:
        slope, intercept = equation
        xs = [x / 2 for x in range(-6, 21)]
        ys = [slope * x + intercept for x in xs]
        ax.plot(xs, ys, linewidth=2.2, color="#277da1")
    else:
        numbers = [float(value) for value in _extract_numbers(text)]
        if len(numbers) >= 4:
            xs = list(range(1, min(6, len(numbers)) + 1))
            ys = numbers[: len(xs)]
        else:
            xs = [1, 2, 3, 4, 5]
            ys = [2, 4, 6, 8, 10]
        ax.plot(xs, ys, marker="o", linewidth=2.0, color="#277da1")
    _style_axes(ax, "Graph Model")
    return fig


def _render_sequence(question, plt):
    numbers = [float(value) for value in _extract_numbers(question.get("question", ""))]
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    if len(numbers) >= 4:
        ys = numbers[:4]
    else:
        ys = [5, 9, 13, 17]
    xs = list(range(1, len(ys) + 1))
    ax.plot(xs, ys, marker="o", linewidth=2.2, color="#90be6d")
    for x_coord, y_coord in zip(xs, ys):
        ax.text(x_coord + 0.05, y_coord + 0.2, f"({x_coord}, {int(y_coord) if y_coord.is_integer() else y_coord})", fontsize=8)
    _style_axes(ax, "Sequence Pattern")
    return fig


def _render_transformation(question, plt):
    base = [(1, 1), (4, 1), (3, 3), (1, 1)]
    rotated = [(-y, x) for x, y in base]
    fig, ax = plt.subplots(figsize=(5.8, 5.4))
    ax.plot([p[0] for p in base], [p[1] for p in base], linewidth=2.2, color="#f3722c", label="Original")
    ax.plot([p[0] for p in rotated], [p[1] for p in rotated], linewidth=2.2, color="#577590", label="Image")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.legend(frameon=False)
    _style_axes(ax, "Transformation Sketch", xlim=(-5, 6), ylim=(-5, 6), equal=True)
    return fig


def _render_cuboid_measure(question, plt):
    length, width, height = _parse_cuboid_dimensions(question.get("question", ""))
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    front = [(0, 0), (length, 0), (length, height), (0, height), (0, 0)]
    dx, dy = width * 0.45, width * 0.35
    back = [(x + dx, y + dy) for x, y in front]
    ax.plot([p[0] for p in front], [p[1] for p in front], color="#6a4c93", linewidth=2.0)
    ax.plot([p[0] for p in back], [p[1] for p in back], color="#6a4c93", linewidth=2.0)
    for start, end in zip(front[:-1], back[:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color="#6a4c93", linewidth=1.8)
    ax.text(length / 2, -0.6, f"{length:g}", ha="center")
    ax.text(length + 0.3, height / 2, f"{height:g}", va="center")
    ax.text(length + dx / 2, height + dy / 2, f"{width:g}", va="bottom")
    ax.axis("off")
    ax.set_title("Cuboid Diagram")
    return fig


def _render_rectangle_measure(question, plt):
    length, width = _parse_rectangle_dimensions(question.get("question", ""))
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    rect_x = [0, length, length, 0, 0]
    rect_y = [0, 0, width, width, 0]
    ax.plot(rect_x, rect_y, linewidth=2.2, color="#43aa8b")
    ax.text(length / 2, -0.4, f"{length:g}", ha="center")
    ax.text(length + 0.25, width / 2, f"{width:g}", va="center")
    _style_axes(ax, "Rectangle Measure", xlim=(-1, max(10, length + 2)), ylim=(-1, max(8, width + 2)), equal=True)
    return fig


def _render_geometry(question, plt):
    numbers = [float(value) for value in _extract_numbers(question.get("question", ""))]
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    triangle = [(0, 0), (6, 0), (2.2, 4.5), (0, 0)]
    ax.plot([p[0] for p in triangle], [p[1] for p in triangle], linewidth=2.2, color="#f94144")
    labels = numbers[:2] if len(numbers) >= 2 else [50, 60]
    ax.text(0.8, 0.35, f"{labels[0]:g}°")
    ax.text(4.8, 0.35, f"{labels[1]:g}°")
    ax.text(2.1, 3.7, "x")
    _style_axes(ax, "Geometry Sketch", xlim=(-1, 7), ylim=(-1, 6), equal=True)
    return fig
