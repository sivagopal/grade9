import os
import tempfile
from pathlib import Path


SUBJECT_MATHS = "Maths"
SUBJECT_FURTHER_MATHS = "Further Maths"
SOURCE = "seed-matplotlib"
STATIC_DIR = Path(__file__).resolve().parent / "static" / "generated" / "question_bank"


def _import_plt():
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "gcse_grade9_mpl"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _row(subject, topic, difficulty, question, answer, explanation, marks, asset_path):
    return {
        "subject": subject,
        "topic": topic,
        "difficulty_level": difficulty,
        "question": question,
        "answer": answer,
        "explanation": explanation,
        "marks": marks,
        "source": SOURCE,
        "asset_path": asset_path,
    }


def _save_figure(fig, filename):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    output_path = STATIC_DIR / filename
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    fig.clf()
    return f"generated/question_bank/{filename}"


def _coordinate_geometry_intersection():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    xs = list(range(-2, 7))
    ys_1 = [2 * x + 1 for x in xs]
    ys_2 = [-x + 7 for x in xs]
    ax.plot(xs, ys_1, label="y = 2x + 1", linewidth=2.2)
    ax.plot(xs, ys_2, label="y = -x + 7", linewidth=2.2)
    ax.set_xlim(-2, 6)
    ax.set_ylim(-1, 10)
    ax.set_xticks(range(-2, 7))
    ax.set_yticks(range(-1, 11))
    ax.grid(True, alpha=0.35)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Coordinate Geometry")
    asset_path = _save_figure(fig, "coordinate_geometry_intersection.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_MATHS,
        topic="Coordinate Geometry",
        difficulty=5,
        question=(
            "The diagram shows the lines y = 2x + 1 and y = -x + 7. "
            "Find their point of intersection and explain why that point also solves a pair of simultaneous equations."
        ),
        answer="(2, 5). The intersection lies on both lines, so its coordinates satisfy both equations at the same time.",
        explanation=(
            "Set the two equations equal because both describe y at the crossing point. "
            "So 2x + 1 = -x + 7, giving 3x = 6 and x = 2. Substitute to get y = 5. "
            "Any intersection of two graphs is a simultaneous solution because the same coordinate pair must satisfy both rules."
        ),
        marks=4,
        asset_path=asset_path,
    )


def _coordinate_geometry_triangle_area():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    points = {"A": (-3, 1), "B": (5, 1), "C": (1, 7)}
    xs = [points["A"][0], points["B"][0], points["C"][0], points["A"][0]]
    ys = [points["A"][1], points["B"][1], points["C"][1], points["A"][1]]
    ax.plot(xs, ys, linewidth=2.2)
    for label, (x_coord, y_coord) in points.items():
        ax.scatter([x_coord], [y_coord], s=40)
        ax.text(x_coord + 0.15, y_coord + 0.2, f"{label}{(x_coord, y_coord)}", fontsize=9)
    ax.set_xlim(-5, 7)
    ax.set_ylim(-1, 9)
    ax.set_xticks(range(-5, 8))
    ax.set_yticks(range(-1, 10))
    ax.grid(True, alpha=0.35)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Triangle on Coordinate Axes")
    asset_path = _save_figure(fig, "coordinate_geometry_triangle_area.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_MATHS,
        topic="Coordinate Geometry",
        difficulty=5,
        question=(
            "Triangle ABC is shown. Work out the area of triangle ABC and justify your method clearly."
        ),
        answer="24 square units.",
        explanation=(
            "AB is horizontal from x = -3 to x = 5, so the base is 8 units. "
            "The perpendicular height from C to the line y = 1 is 6 units. "
            "Use area = 1/2 x base x height = 1/2 x 8 x 6 = 24. "
            "A strong justification explains why AB can be treated as the base and why the height is perpendicular."
        ),
        marks=4,
        asset_path=asset_path,
    )


def _algebra_graph_intersection():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    xs = [x / 2 for x in range(-2, 17)]
    ys_1 = [2 * x - 3 for x in xs]
    ys_2 = [9 - x for x in xs]
    ax.plot(xs, ys_1, label="y = 2x - 3", linewidth=2.2)
    ax.plot(xs, ys_2, label="y = 9 - x", linewidth=2.2)
    ax.set_xlim(-1, 8)
    ax.set_ylim(-5, 11)
    ax.set_xticks(range(-1, 9))
    ax.set_yticks(range(-5, 12, 2))
    ax.grid(True, alpha=0.35)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Algebra Through Graphs")
    asset_path = _save_figure(fig, "algebra_graph_intersection.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_MATHS,
        topic="Algebra",
        difficulty=5,
        question=(
            "Two mobile phone plans are modelled by the lines y = 2x - 3 and y = 9 - x, where x is the number of weeks after a promotion starts "
            "and y is the effective cost in pounds. Use the graph and algebra to determine when the plans cost the same, then explain which plan is cheaper before and after that week."
        ),
        answer="They cost the same after 4 weeks, when y = 5. For fewer than 4 weeks, y = 2x - 3 is cheaper. For more than 4 weeks, y = 9 - x is cheaper.",
        explanation=(
            "Equal cost means the lines intersect, so solve 2x - 3 = 9 - x. This gives 3x = 12, so x = 4 and y = 5. "
            "To compare before and after, inspect which line sits lower on the graph because a lower y-value means a cheaper plan."
        ),
        marks=5,
        asset_path=asset_path,
    )


def _algebra_region_problem():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    xs = [x / 2 for x in range(0, 21)]
    ys_budget = [12 - x / 2 for x in xs]
    ys_ratio = [x - 2 for x in xs]
    ax.plot(xs, ys_budget, label="x + 2y = 24", linewidth=2.2)
    ax.plot(xs, ys_ratio, label="y = x - 2", linewidth=2.2)
    ax.axvline(8, linewidth=2.2, color="#0d5c35", linestyle="--", label="x = 8")
    ax.fill([2, 8, 8], [0, 6, 0], alpha=0.16, color="#1fb66c")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.set_xticks(range(0, 11))
    ax.set_yticks(range(0, 13, 2))
    ax.grid(True, alpha=0.35)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Feasible Region")
    asset_path = _save_figure(fig, "algebra_feasible_region.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_MATHS,
        topic="Algebra",
        difficulty=5,
        question=(
            "A school is buying x science journals and y maths journals. The graph shows the budget condition x + 2y <= 24, the policy condition y <= x - 2, and a storage limit x <= 8. "
            "Using the diagram, find the greatest possible value of x + y for whole-number solutions and justify why your choice is optimal."
        ),
        answer="The greatest possible value is 14, achieved at x = 8 and y = 6.",
        explanation=(
            "The feasible region is bounded by the axes and the two lines. To maximise x + y, inspect the corner points because a linear objective reaches its maximum at a vertex of the region. "
            "With the storage limit x <= 8, the key vertices are (2, 0), (8, 0), and (8, 6). The best valid corner is (8, 6), giving x + y = 14."
        ),
        marks=5,
        asset_path=asset_path,
    )


def _algebra_sequence_model():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    xs = [1, 2, 3, 4, 5]
    ys = [5, 9, 13, 17, 21]
    ax.scatter(xs, ys, s=48, color="#10824a")
    ax.plot(xs, ys, linewidth=2.2, color="#1fb66c")
    for x_coord, y_coord in zip(xs, ys):
        ax.text(x_coord + 0.06, y_coord + 0.4, f"({x_coord}, {y_coord})", fontsize=9)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(3, 23)
    ax.set_xticks(xs)
    ax.set_yticks(range(5, 24, 4))
    ax.grid(True, alpha=0.35)
    ax.set_title("Pattern to Equation")
    asset_path = _save_figure(fig, "algebra_sequence_model.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_MATHS,
        topic="Algebra",
        difficulty=5,
        question=(
            "The diagram shows the total number of tiles needed to build pattern number x. Write a formula for the number of tiles y in terms of x, then work out which pattern number would use 73 tiles."
        ),
        answer="y = 4x + 1, so 73 tiles occurs when x = 18.",
        explanation=(
            "The points increase by 4 each time, so the relationship is linear with gradient 4. Using the first point, 5 = 4(1) + c, so c = 1 and y = 4x + 1. "
            "Set 73 = 4x + 1, giving 72 = 4x and x = 18."
        ),
        marks=4,
        asset_path=asset_path,
    )


def _matrix_transformation():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    original = [(1, 1), (3, 1), (2, 4), (1, 1)]
    image = [(-1, 1), (-1, 3), (-4, 2), (-1, 1)]
    ax.plot([p[0] for p in original], [p[1] for p in original], linewidth=2.2, label="Original")
    ax.plot([p[0] for p in image], [p[1] for p in image], linewidth=2.2, label="Image")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-1, 5)
    ax.set_xticks(range(-5, 6))
    ax.set_yticks(range(-1, 6))
    ax.grid(True, alpha=0.35)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Matrix Transformation")
    asset_path = _save_figure(fig, "matrices_rotation.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_FURTHER_MATHS,
        topic="Matrices",
        difficulty=5,
        question=(
            "The image shape is the result of transforming the original triangle by a 2 x 2 matrix about the origin. "
            "State the matrix and describe the transformation geometrically."
        ),
        answer="[[0, -1], [1, 0]]. A 90 degree anticlockwise rotation about the origin.",
        explanation=(
            "Track basis behaviour or map vertices. The point (1, 1) goes to (-1, 1), which matches the rule (x, y) -> (-y, x). "
            "That rule is represented by the matrix [[0, -1], [1, 0]]. "
            "Geometrically, this is a 90 degree anticlockwise rotation about the origin."
        ),
        marks=4,
        asset_path=asset_path,
    )


def _matrix_composition():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.axis("off")
    ax.text(0.05, 0.70, "A = [ 2  1 ]", fontsize=16, family="monospace")
    ax.text(0.05, 0.48, "    [ 1  1 ]", fontsize=16, family="monospace")
    ax.text(0.52, 0.70, "B = [ 1  0 ]", fontsize=16, family="monospace")
    ax.text(0.52, 0.48, "    [ 3  1 ]", fontsize=16, family="monospace")
    ax.text(0.05, 0.14, "Find AB and explain why BA is different.", fontsize=15)
    asset_path = _save_figure(fig, "matrices_composition.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_FURTHER_MATHS,
        topic="Matrices",
        difficulty=5,
        question="Use the matrices in the diagram to find AB. Then explain why BA is not the same matrix.",
        answer="AB = [[5, 1], [4, 1]]. BA = [[2, 1], [7, 4]], so multiplication is not commutative.",
        explanation=(
            "Multiply rows of A by columns of B. "
            "Top-left: 2x1 + 1x3 = 5. Top-right: 2x0 + 1x1 = 1. "
            "Bottom-left: 1x1 + 1x3 = 4. Bottom-right: 1x0 + 1x1 = 1. "
            "Then compute BA separately to see the order changes which row-column pairs interact, so matrix multiplication is not commutative."
        ),
        marks=4,
        asset_path=asset_path,
    )


def _binomial_coefficients():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.axis("off")
    rows = [
        "               1",
        "            1     1",
        "         1     2     1",
        "      1     3     3     1",
        "   1     4     6     4     1",
        "1     5    10    10     5     1",
    ]
    for idx, text in enumerate(rows):
        ax.text(0.08, 0.88 - idx * 0.14, text, fontsize=16, family="monospace")
    ax.text(0.08, 0.04, "Use the highlighted row for (a + b)^5.", fontsize=14)
    asset_path = _save_figure(fig, "binomial_pascal.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_FURTHER_MATHS,
        topic="Binomial Expansion",
        difficulty=5,
        question=(
            "Using the Pascal triangle diagram, expand (2x - 3)^5 and state the coefficient of x^3."
        ),
        answer=(
            "32x^5 - 240x^4 + 720x^3 - 1080x^2 + 810x - 243. "
            "The coefficient of x^3 is 720."
        ),
        explanation=(
            "Use coefficients 1, 5, 10, 10, 5, 1. "
            "Then expand term by term: (2x)^5, 5(2x)^4(-3), 10(2x)^3(-3)^2, 10(2x)^2(-3)^3, 5(2x)(-3)^4, (-3)^5. "
            "Be careful with powers and signs. The x^3 term is 10 x 8x^3 x 9 = 720x^3."
        ),
        marks=5,
        asset_path=asset_path,
    )


def _binomial_unknown_constant():
    plt = _import_plt()
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.axis("off")
    ax.text(0.06, 0.64, "(x + a)^4 = x^4 + 12x^3 + ...", fontsize=20)
    ax.text(0.06, 0.28, "Find a and write the x^2 term.", fontsize=18)
    asset_path = _save_figure(fig, "binomial_unknown_constant.png")
    plt.close(fig)
    return _row(
        subject=SUBJECT_FURTHER_MATHS,
        topic="Binomial Expansion",
        difficulty=5,
        question="The diagram states that (x + a)^4 = x^4 + 12x^3 + ... . Find a and then write the x^2 term.",
        answer="a = 3, and the x^2 term is 54x^2.",
        explanation=(
            "For (x + a)^4, the x^3 term is 4ax^3. "
            "So 4a = 12, giving a = 3. "
            "The x^2 term is 6a^2x^2, so 6 x 9 x^2 = 54x^2."
        ),
        marks=4,
        asset_path=asset_path,
    )


def build_plot_question_bank():
    return [
        _coordinate_geometry_intersection(),
        _coordinate_geometry_triangle_area(),
        _algebra_graph_intersection(),
        _algebra_region_problem(),
        _algebra_sequence_model(),
        _matrix_transformation(),
        _matrix_composition(),
        _binomial_coefficients(),
        _binomial_unknown_constant(),
    ]
