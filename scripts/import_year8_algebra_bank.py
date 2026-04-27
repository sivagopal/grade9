from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


def add(rows, topic, difficulty, question, answer, marks):
    rows.append(
        {
            "subject": "Maths",
            "topic": topic,
            "difficulty_level": difficulty,
            "question": question,
            "answer": answer,
            "marks": marks,
            "source": "year8-algebra-pack",
        }
    )


def build_questions():
    rows = []

    for i, (a, b, c) in enumerate(
        [
            (2, 3, 5),
            (4, 2, 7),
            (3, 5, 4),
            (6, 1, 2),
            (5, 4, 9),
            (7, 2, 3),
            (8, 3, 6),
            (9, 4, 1),
            (10, 5, 8),
            (11, 2, 7),
        ],
        start=1,
    ):
        add(
            rows,
            "Algebra Expressions",
            1,
            f"Question {i}: Simplify {a}x + {b}x - {c}x.",
            f"{a + b - c}x. Award 1 mark for combining like terms correctly.",
            1,
        )

    base = len(rows)
    for i, (a, b, c) in enumerate(
        [
            (2, 3, 4),
            (3, 5, 1),
            (4, 2, 6),
            (5, 1, 3),
            (6, 4, 2),
            (7, 3, 5),
            (8, 2, 7),
            (9, 1, 4),
            (10, 5, 6),
            (11, 4, 8),
        ],
        start=1,
    ):
        add(
            rows,
            "Expanding Brackets",
            1,
            f"Question {base + i}: Expand {a}(x + {b}) - {c}.",
            f"{a}x + {a * b - c}. Award 1 mark for multiplying into the bracket and 1 mark for the simplified expression.",
            2,
        )

    base = len(rows)
    for i, (a, b, total) in enumerate(
        [
            (3, 5, 20),
            (4, 7, 31),
            (5, 2, 27),
            (6, 4, 40),
            (7, 3, 31),
            (8, 6, 46),
            (9, 1, 28),
            (2, 9, 19),
            (11, 5, 49),
            (12, 8, 56),
        ],
        start=1,
    ):
        x = (total - b) // a
        add(
            rows,
            "Solving Equations",
            2,
            f"Question {base + i}: Solve {a}x + {b} = {total}.",
            f"x = {x}. Award 1 mark for subtracting {b} and 1 mark for dividing by {a}.",
            2,
        )

    base = len(rows)
    for i, (expr, x_val, answer) in enumerate(
        [
            ("3x + 4", 5, 19),
            ("2x - 7", 9, 11),
            ("5x + 1", 6, 31),
            ("4x - 3", 8, 29),
            ("7x + 2", 3, 23),
            ("6x - 5", 4, 19),
            ("9x + 6", 2, 24),
            ("8x - 1", 7, 55),
            ("10x + 3", 5, 53),
            ("11x - 4", 6, 62),
        ],
        start=1,
    ):
        add(
            rows,
            "Substitution",
            2,
            f"Question {base + i}: Work out {expr} when x = {x_val}.",
            f"{answer}. Award 1 mark for correct substitution and 1 mark for the final answer.",
            2,
        )

    base = len(rows)
    for i, (apples, bananas, pens) in enumerate(
        [
            (3, 2, 1),
            (4, 5, 2),
            (2, 6, 3),
            (5, 3, 4),
            (6, 2, 5),
            (7, 4, 2),
            (8, 1, 6),
            (9, 3, 3),
            (10, 2, 4),
            (11, 5, 1),
        ],
        start=1,
    ):
        add(
            rows,
            "Forming Expressions",
            2,
            f"Question {base + i}: A shop sells apples for x pounds each, bananas for y pounds each and pens for 50p each. Write an expression for the total cost of {apples} apples, {bananas} bananas and {pens} pens.",
            f"{apples}x + {bananas}y + {pens / 2:g}. Award 1 mark for the x term, 1 mark for the y term, and 1 mark for including the constant pen cost.",
            3,
        )

    base = len(rows)
    for i, (start_value, step) in enumerate(
        [
            (4, 3),
            (7, 2),
            (10, 5),
            (1, 4),
            (6, 6),
            (9, 7),
            (12, 8),
            (5, 9),
            (3, 10),
            (8, 11),
        ],
        start=1,
    ):
        nth = f"{step}n + {start_value - step}"
        add(
            rows,
            "Sequences",
            3,
            f"Question {base + i}: Find the nth term of the sequence {start_value}, {start_value + step}, {start_value + 2 * step}, {start_value + 3 * step}.",
            f"{nth}. Award 1 mark for the common difference {step} and 1 mark for the correct nth term.",
            2,
        )

    base = len(rows)
    for i, (p, q) in enumerate(
        [
            (2, 5),
            (3, 7),
            (4, 9),
            (5, 11),
            (6, 13),
            (7, 15),
            (8, 17),
            (9, 19),
            (10, 21),
            (11, 23),
        ],
        start=1,
    ):
        add(
            rows,
            "Factorising",
            3,
            f"Question {base + i}: Factorise {p}x + {p * q}.",
            f"{p}(x + {q}). Award 1 mark for identifying the common factor {p} and 1 mark for the bracket.",
            2,
        )

    base = len(rows)
    for i, (a, b, c, total) in enumerate(
        [
            (2, 3, 4, 18),
            (3, 2, 5, 25),
            (4, 1, 6, 26),
            (5, 4, 3, 42),
            (6, 2, 7, 43),
            (7, 3, 5, 51),
            (8, 1, 9, 55),
            (9, 2, 4, 67),
            (10, 5, 6, 95),
            (11, 4, 7, 103),
        ],
        start=1,
    ):
        x = (total + c - b) // a
        add(
            rows,
            "Multi-step Equations",
            4,
            f"Question {base + i}: Solve {a}x + {b} - {c} = {total}.",
            f"x = {x}. Award 1 mark for simplifying the left side, 1 mark for isolating the x term, and 1 mark for the correct solution.",
            3,
        )

    base = len(rows)
    for i, (length_const, width_const, perimeter) in enumerate(
        [
            (3, 1, 30),
            (4, 2, 40),
            (5, 3, 50),
            (6, 4, 60),
            (7, 5, 70),
            (8, 6, 80),
            (9, 7, 90),
            (10, 8, 100),
            (11, 9, 110),
            (12, 10, 120),
        ],
        start=1,
    ):
        x = (perimeter // 2 - length_const - width_const) // 2
        add(
            rows,
            "Perimeter and Algebra",
            4,
            f"Question {base + i}: A rectangle has length x + {length_const} cm and width x + {width_const} cm. Its perimeter is {perimeter} cm. Find x.",
            f"x = {x}. Award 1 mark for forming 2(x + {length_const}) + 2(x + {width_const}) = {perimeter}, 1 mark for simplifying, and 1 mark for solving.",
            3,
        )

    base = len(rows)
    for i, (a, b, c, d) in enumerate(
        [
            (2, 3, 4, 5),
            (3, 4, 5, 6),
            (4, 5, 6, 7),
            (5, 6, 7, 8),
            (6, 7, 8, 9),
            (7, 8, 9, 10),
            (8, 9, 10, 11),
            (9, 10, 11, 12),
            (10, 11, 12, 13),
            (11, 12, 13, 14),
        ],
        start=1,
    ):
        add(
            rows,
            "Algebra Challenge",
            5,
            f"Question {base + i}: Expand and simplify {a}(x + {b}) + {c}(x - {d}).",
            f"{a + c}x + {a * b - c * d}. Award 1 mark for each correct expansion and 1 mark for the fully simplified expression.",
            3,
        )

    assert len(rows) == 100, len(rows)
    return rows


def main():
    rows = build_questions()
    db = PlannerDB()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 algebra questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
