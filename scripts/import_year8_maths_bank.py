from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-maths-topic-pack"
SUBJECT = "Maths"


def row(topic, difficulty, question, answer, marks):
    return {
        "subject": SUBJECT,
        "topic": topic,
        "difficulty_level": difficulty,
        "question": question,
        "answer": answer,
        "marks": marks,
        "source": SOURCE,
    }


def build_number_skills():
    rows = []
    for i in range(1, 101):
        a = 120 + i * 3
        b = 35 + i
        answer = a - b
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Number Skills",
                difficulty,
                f"Number Skills {i}: Work out {a} - {b}.",
                f"{answer}. Award 1 mark for the correct subtraction.",
                1,
            )
        )
    return rows


def build_fractions():
    rows = []
    for i in range(1, 101):
        denom = (i % 9) + 2
        num1 = denom * 2 + (i % denom)
        num2 = denom + (i % denom)
        total = num1 + num2
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Fractions",
                difficulty,
                f"Fractions {i}: Work out {num1}/{denom} + {num2}/{denom}. Give your answer as an improper fraction or mixed number.",
                f"{total}/{denom}. Simplified answer accepted where possible. Award 1 mark for a correct common denominator method and 1 mark for the correct total.",
                2,
            )
        )
    return rows


def build_decimals():
    rows = []
    for i in range(1, 101):
        a = round(1.5 + i * 0.2, 1)
        b = round(0.4 + (i % 7) * 0.3, 1)
        answer = round(a + b, 1)
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Decimals",
                difficulty,
                f"Decimals {i}: Work out {a} + {b}.",
                f"{answer}. Award 1 mark for correct decimal alignment and 1 mark for the correct answer.",
                2,
            )
        )
    return rows


def build_percentages():
    rows = []
    for i in range(1, 101):
        percent = (i % 18 + 2) * 5
        amount = 40 + i * 4
        answer = amount * percent / 100
        difficulty = 2 if i <= 40 else 3 if i <= 75 else 4
        rows.append(
            row(
                "Percentages",
                difficulty,
                f"Percentages {i}: Find {percent}% of {amount}.",
                f"{answer:g}. Award 1 mark for finding 1% or 10% as an intermediate step and 1 mark for the correct percentage value.",
                2,
            )
        )
    return rows


def build_ratio():
    rows = []
    for i in range(1, 101):
        a = (i % 5) + 2
        b = (i % 7) + 3
        total_parts = a + b
        multiplier = (i % 8) + 4
        total = total_parts * multiplier
        first = a * multiplier
        second = b * multiplier
        difficulty = 2 if i <= 40 else 3 if i <= 75 else 4
        rows.append(
            row(
                "Ratio and Proportion",
                difficulty,
                f"Ratio {i}: Share {total} in the ratio {a}:{b}.",
                f"{first} and {second}. Award 1 mark for finding the value of one part and 1 mark for each correct share.",
                3,
            )
        )
    return rows


def build_algebra():
    rows = []
    for i in range(1, 101):
        a = (i % 9) + 2
        b = (i % 8) + 3
        c = (i % 6) + 1
        answer_coeff = a + b - c
        difficulty = 1 if i <= 30 else 2 if i <= 65 else 4
        rows.append(
            row(
                "Algebra",
                difficulty,
                f"Algebra {i}: Simplify {a}x + {b}x - {c}x.",
                f"{answer_coeff}x. Award 1 mark for combining like terms correctly.",
                1,
            )
        )
    return rows


def build_sequences():
    rows = []
    for i in range(1, 101):
        start = (i % 11) + 3
        step = (i % 9) + 2
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Sequences",
                difficulty,
                f"Sequences {i}: Find the nth term of the sequence {start}, {start + step}, {start + 2 * step}, {start + 3 * step}.",
                f"{step}n + {start - step}. Award 1 mark for identifying the common difference {step} and 1 mark for the correct nth term.",
                2,
            )
        )
    return rows


def build_geometry():
    rows = []
    for i in range(1, 101):
        angle1 = 20 + (i % 8) * 10
        angle2 = 30 + (i % 6) * 10
        angle3 = 180 - angle1 - angle2
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Geometry and Angles",
                difficulty,
                f"Geometry {i}: Two angles in a triangle are {angle1} degrees and {angle2} degrees. Find the third angle.",
                f"{angle3} degrees. Award 1 mark for using angles in a triangle sum to 180 and 1 mark for the correct answer.",
                2,
            )
        )
    return rows


def build_area_perimeter():
    rows = []
    for i in range(1, 101):
        length = 5 + (i % 12)
        width = 3 + (i % 9)
        area = length * width
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Area and Perimeter",
                difficulty,
                f"Area and Perimeter {i}: A rectangle has length {length} cm and width {width} cm. Work out its area.",
                f"{area} cm^2. Award 1 mark for using area = length x width and 1 mark for the correct area.",
                2,
            )
        )
    return rows


def build_statistics():
    rows = []
    for i in range(1, 101):
        a = 2 + (i % 5)
        b = 4 + (i % 6)
        c = 6 + (i % 7)
        d = 8 + (i % 8)
        e = 10 + (i % 9)
        total = a + b + c + d + e
        mean = total / 5
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Statistics and Probability",
                difficulty,
                f"Statistics {i}: Find the mean of {a}, {b}, {c}, {d}, {e}.",
                f"{mean:g}. Award 1 mark for finding the total {total} and 1 mark for dividing by 5.",
                2,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_number_skills())
    rows.extend(build_fractions())
    rows.extend(build_decimals())
    rows.extend(build_percentages())
    rows.extend(build_ratio())
    rows.extend(build_algebra())
    rows.extend(build_sequences())
    rows.extend(build_geometry())
    rows.extend(build_area_perimeter())
    rows.extend(build_statistics())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 maths questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
