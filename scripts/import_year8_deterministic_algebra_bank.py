from pathlib import Path
import sys

from sympy import Eq, Rational, expand, factor, simplify, solve, symbols

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-maths-deterministic-algebra"
SUBJECT = "Maths"

x, y, a, b = symbols("x y a b")


def row(topic, difficulty, question, answer, marks, explanation=""):
    return {
        "subject": SUBJECT,
        "topic": topic,
        "difficulty_level": difficulty,
        "question": question,
        "answer": answer,
        "marks": marks,
        "source": SOURCE,
        "explanation": explanation,
    }


def fmt_expr(expr):
    text = str(expr)
    text = text.replace("**", "^").replace("*", "")
    return text


def fmt_number(value):
    if getattr(value, "q", None) == 1:
        return str(int(value))
    return str(value)


def build_algebra_expressions():
    rows = []
    specs = [
        (3, 5, 2, 2),
        (4, -3, 7, 3),
        (5, 2, -4, 3),
        (2, 6, 3, 3),
        (7, -5, 4, 4),
        (3, 4, 8, 4),
    ]
    for index, (p, q, r, difficulty) in enumerate(specs, start=1):
        expr = p * x + q * x - r * x + (index + 2)
        answer = simplify(expr)
        rows.append(
            row(
                "Algebra Expressions",
                difficulty,
                f"Simplify fully: {p}x {'+' if q >= 0 else '-'} {abs(q)}x {'+' if -r >= 0 else '-'} {abs(r)}x + {index + 2}.",
                fmt_expr(answer),
                2,
                "Collect the x terms first, then keep the constant term.",
            )
        )
    advanced_specs = [
        ("Simplify fully: 4x + 3 - 2x + 7 - 5x.", simplify(4 * x + 3 - 2 * x + 7 - 5 * x), 3, 4),
        ("Simplify fully: 3a + 5b - 2a + 4b - 7.", simplify(3 * a + 5 * b - 2 * a + 4 * b - 7), 3, 4),
        ("Simplify fully: 2x^2 + 5x - 3x^2 + 4 - x + 9.", simplify(2 * x ** 2 + 5 * x - 3 * x ** 2 + 4 - x + 9), 4, 5),
        ("Simplify fully: 6y - 2(3 - y) + 5.", simplify(6 * y - 2 * (3 - y) + 5), 4, 5),
        ("Simplify fully: 3(2x - 1) + 4(x + 5) - 2x.", simplify(3 * (2 * x - 1) + 4 * (x + 5) - 2 * x), 4, 5),
        ("Simplify fully: 5a - 2b + 3a + 7b - 4 + b.", simplify(5 * a - 2 * b + 3 * a + 7 * b - 4 + b), 3, 4),
        ("Simplify fully: x^2 + 4x - 7 + 3x^2 - 6x + 10.", simplify(x ** 2 + 4 * x - 7 + 3 * x ** 2 - 6 * x + 10), 4, 5),
        ("Simplify fully: 2(3x - 4) - 5(x + 1) + 3.", simplify(2 * (3 * x - 4) - 5 * (x + 1) + 3), 4, 5),
    ]
    for question_text, answer, marks, difficulty in advanced_specs:
        rows.append(
            row(
                "Algebra Expressions",
                difficulty,
                question_text,
                fmt_expr(answer),
                marks,
                "Expand any brackets first, then collect like terms carefully.",
            )
        )
    return rows


def build_forming_expressions():
    rows = []
    prompts = [
        (
            "A rectangle has width x cm and length x + 5 cm. Write an expression for its perimeter and simplify.",
            simplify(2 * x + 2 * (x + 5)),
            3,
            3,
        ),
        (
            "A cinema ticket costs p pounds and a drink costs q pounds. Write an expression for the cost of 3 tickets and 2 drinks.",
            3 * symbols("p") + 2 * symbols("q"),
            2,
            3,
        ),
        (
            "A number x is increased by 7 and then multiplied by 4. Write the resulting expression in expanded form.",
            expand(4 * (x + 7)),
            2,
            3,
        ),
        (
            "A gardener buys x plants at GBP 3 each and y bags of compost at GBP 5 each. Write an expression for the total cost.",
            3 * x + 5 * y,
            2,
            3,
        ),
        (
            "The perimeter of a triangle is found by adding sides x + 2, x + 5, and 2x - 1. Write a simplified expression for the perimeter.",
            simplify((x + 2) + (x + 5) + (2 * x - 1)),
            3,
            4,
        ),
    ]
    for question, answer, marks, difficulty in prompts:
        rows.append(
            row(
                "Forming Expressions",
                difficulty,
                question,
                fmt_expr(answer),
                marks,
                "Translate each part of the description into algebra before simplifying.",
            )
        )
    return rows


def build_substitution():
    rows = []
    specs = [
        (2 * x ** 2 - 3 * x + 4, -2, 3, 3),
        (3 * x ** 2 + 2 * x - 5, 4, 3, 4),
        (2 * a + 3 * b, {a: 5, b: -2}, 2, 3),
        ((x + 3) * (x - 1), 6, 3, 4),
        ((a - b) ** 2, {a: 7, b: 3}, 3, 4),
        ((2 * x + 1) / 3, 7, 2, 3),
    ]
    for expr, value, marks, difficulty in specs:
        if isinstance(value, dict):
            substituted = simplify(expr.subs(value))
            assignment = ", ".join(f"{symbol} = {number}" for symbol, number in value.items())
            question = f"When {assignment}, work out {fmt_expr(expr)}."
        else:
            substituted = simplify(expr.subs({x: value}))
            question = f"When x = {value}, work out {fmt_expr(expr)}."
        rows.append(
            row(
                "Substitution",
                difficulty,
                question,
                fmt_number(substituted),
                marks,
                "Substitute carefully, keeping brackets around negative values where needed.",
            )
        )
    return rows


def build_expanding_brackets():
    rows = []
    specs = [
        ("Expand and simplify: 3(2x + 5) - 4(x - 1).", 3 * (2 * x + 5) - 4 * (x - 1), 3, 4),
        ("Expand and simplify: -2(3x - 7) + 5(x + 4).", -2 * (3 * x - 7) + 5 * (x + 4), 3, 5),
        ("Expand and simplify: 4(x + 6) + 2(x - 3).", 4 * (x + 6) + 2 * (x - 3), 3, 5),
        ("Expand and simplify: 5(x - 4) - 3(2x + 1).", 5 * (x - 4) - 3 * (2 * x + 1), 3, 5),
        ("Expand and simplify: (2x - 1)(x + 3).", (2 * x - 1) * (x + 3), 4, 5),
        ("Expand and simplify: (x - 5)(x + 2).", (x - 5) * (x + 2), 4, 5),
    ]
    for question_text, expr, marks, difficulty in specs:
        answer = expand(expr)
        rows.append(
            row(
                "Expanding Brackets",
                difficulty,
                question_text,
                fmt_expr(answer),
                marks,
                "Multiply every term in each bracket before collecting like terms.",
            )
        )
    return rows


def build_factorising():
    rows = []
    specs = [
        (6 * x + 15, 2, 4),
        (2 * x ** 2 + 10 * x, 2, 4),
        (x ** 2 + 9 * x + 20, 3, 5),
        (x ** 2 - x - 20, 3, 5),
        (2 * x ** 2 + 7 * x + 3, 4, 5),
        (3 * x ** 2 - 12 * x, 3, 4),
    ]
    for expr, marks, difficulty in specs:
        answer = factor(expr)
        rows.append(
            row(
                "Factorising",
                difficulty,
                f"Factorise fully: {fmt_expr(expr)}.",
                fmt_expr(answer),
                marks,
                "Take out any common factor first, then look for a quadratic factorisation if needed.",
            )
        )
    return rows


def build_solving_equations():
    rows = []
    equations = [
        ("Solve: 5x - 7 = 3x + 11.", Eq(5 * x - 7, 3 * x + 11), 3, 4),
        ("Solve: 7 - 2(x - 3) = 13.", Eq(7 - 2 * (x - 3), 13), 3, 4),
        ("Solve: 2(x + 5) + 3(x - 1) = 4x + 17.", Eq(2 * (x + 5) + 3 * (x - 1), 4 * x + 17), 4, 5),
        ("Solve: 3(2x - 1) = 4x + 14.", Eq(3 * (2 * x - 1), 4 * x + 14), 4, 5),
        ("Solve: 3x/2 + 4 = 13.", Eq(Rational(3, 2) * x + 4, 13), 4, 5),
        ("Solve: 4x - 9 = 2x + 15.", Eq(4 * x - 9, 2 * x + 15), 3, 4),
    ]
    for question_text, equation, marks, difficulty in equations:
        solution = solve(equation, x)[0]
        rows.append(
            row(
                "Solving Equations",
                difficulty,
                question_text,
                f"x = {fmt_number(solution)}",
                marks,
                "Keep the equation balanced at each step and check the final value by substitution.",
            )
        )
    return rows


def build_multistep_equations():
    rows = []
    equations = [
        ("Solve: 4(x - 2) + 6 = 30.", Eq(4 * (x - 2) + 6, 30), 4, 4),
        ("Solve: 3(x + 4) - 2 = 28.", Eq(3 * (x + 4) - 2, 28), 4, 4),
        ("Solve: 2(3x - 5) + 7 = x + 20.", Eq(2 * (3 * x - 5) + 7, x + 20), 4, 5),
        ("Solve: 5 - 3(x - 2) = 2x + 10.", Eq(5 - 3 * (x - 2), 2 * x + 10), 4, 5),
        ("Solve: (x - 4)/3 + 5 = 9.", Eq((x - 4) / 3 + 5, 9), 4, 5),
    ]
    for question_text, equation, marks, difficulty in equations:
        solution = solve(equation, x)[0]
        rows.append(
            row(
                "Multi-step Equations",
                difficulty,
                question_text,
                f"x = {fmt_number(solution)}",
                marks,
                "Expand or clear fractions first if that makes the equation cleaner.",
            )
        )
    return rows


def build_algebra_challenge():
    rows = []
    simultaneous_specs = [
        (Eq(2 * x + y, 17), Eq(x - y, 1), 5),
        (Eq(3 * x + 2 * y, 19), Eq(x + y, 7), 5),
        (Eq(4 * x - y, 9), Eq(2 * x + y, 11), 5),
        (Eq(5 * x + 3 * y, 31), Eq(x - y, 2), 5),
    ]
    for first, second, difficulty in simultaneous_specs:
        solution = solve((first, second), (x, y), dict=True)[0]
        rows.append(
            row(
                "Algebra Challenge",
                difficulty,
                f"Solve simultaneously: {fmt_expr(first.lhs)} = {fmt_expr(first.rhs)} and {fmt_expr(second.lhs)} = {fmt_expr(second.rhs)}.",
                f"x = {fmt_number(solution[x])}, y = {fmt_number(solution[y])}",
                5,
                "Use substitution or elimination, then check both values in both equations.",
            )
        )

    challenge_questions = [
        (
            "The sum of three consecutive integers is 93. Find the integers.",
            "30, 31 and 32",
            4,
            5,
        ),
        (
            "A rectangle has width x and length x + 5. Its perimeter is 42. Find x and then the area.",
            "x = 8, area = 104 square units",
            5,
            5,
        ),
        (
            "Two cinema tickets and three drinks cost GBP 21. One ticket costs twice as much as one drink. Work out the cost of one ticket and one drink.",
            "Ticket GBP 6, drink GBP 3",
            4,
            5,
        ),
    ]
    for question, answer, marks, difficulty in challenge_questions:
        rows.append(
            row(
                "Algebra Challenge",
                difficulty,
                question,
                answer,
                marks,
                "Define the variable clearly before forming the equation or pair of equations.",
            )
        )
    return rows


def build_gcse_higher_algebra():
    return [
        row(
            "Algebra Challenge",
            5,
            "Solve simultaneously: 2x + 3y = 19 and x - y = 4.",
            "x = 31/5, y = 11/5",
            5,
            "Use substitution from x - y = 4, then solve exactly.",
        ),
        row(
            "Algebra Challenge",
            5,
            "Solve simultaneously: 3x - 2y = 7 and 4x + y = 18.",
            "x = 43/11, y = 26/11",
            5,
            "Eliminate one variable carefully and keep fractional answers exact.",
        ),
        row(
            "Solving Equations",
            5,
            "Solve: 5(2x - 3) - 4(x + 1) = 3(x + 7).",
            "x = 34",
            4,
            "Expand both sides fully before collecting like terms.",
        ),
        row(
            "Solving Equations",
            5,
            "Solve: (3x - 5)/4 = (x + 7)/2.",
            "x = -19",
            4,
            "Clear the denominators first, then solve the linear equation.",
        ),
        row(
            "Multi-step Equations",
            5,
            "Solve: 2(3x - 4) + 5 = 4(x + 6) - 9.",
            "x = 3",
            4,
            "Expand, simplify both sides, and isolate x.",
        ),
        row(
            "Multi-step Equations",
            5,
            "Solve: 7 - (2x - 3) = 3(x + 1) - 5.",
            "x = 12/5",
            4,
            "Be careful with the negative sign before the bracket.",
        ),
        row(
            "Expanding Brackets",
            5,
            "Expand and simplify: (3x - 2)(2x + 5).",
            "6x^2 + 11x - 10",
            4,
            "Multiply every term in the first bracket by every term in the second.",
        ),
        row(
            "Expanding Brackets",
            5,
            "Expand and simplify: (2x - 7)(x - 4).",
            "2x^2 - 15x + 28",
            4,
            "Use a systematic product method to avoid sign errors.",
        ),
        row(
            "Factorising",
            5,
            "Factorise fully: x^2 - 11x + 24.",
            "(x - 3)(x - 8)",
            3,
            "Find two numbers that add to -11 and multiply to 24.",
        ),
        row(
            "Factorising",
            5,
            "Factorise fully: 2x^2 - x - 6.",
            "(2x + 3)(x - 2)",
            4,
            "Split the middle term or use inspection with the leading coefficient.",
        ),
        row(
            "Factorising",
            5,
            "Factorise fully: 3x^2 + x - 10.",
            "(3x - 5)(x + 2)",
            4,
            "Check that the outer and inner products combine to +x.",
        ),
        row(
            "Sequences",
            5,
            "The nth term of a sequence is 4n - 7. Work out which term is equal to 61.",
            "17th term",
            3,
            "Set 4n - 7 equal to 61 and solve for n.",
        ),
        row(
            "Sequences",
            5,
            "A sequence has nth term 5n + 3. A second sequence has nth term 2n + 24. Find the term number where the sequences are equal.",
            "n = 7",
            4,
            "Set the two nth-term expressions equal and solve.",
        ),
        row(
            "Algebra",
            5,
            "When x = -3, work out 2x^2 - 5x - 4.",
            "29",
            3,
            "Substitute carefully and square the negative value correctly.",
        ),
        row(
            "Algebra",
            5,
            "Simplify fully: 4(2x - 3) - 3(x + 5) + 2.",
            "5x - 25",
            3,
            "Expand each bracket and combine like terms.",
        ),
        row(
            "Algebra Challenge",
            5,
            "The perimeter of a rectangle is 58 cm. Its length is 3 cm more than twice its width. Find the width and the length.",
            "Width = 13 cm, length = 29 cm",
            5,
            "Let the width be x and form a perimeter equation.",
        ),
        row(
            "Algebra Challenge",
            5,
            "A number is multiplied by 4, then 9 is subtracted. The result is 7 more than twice the original number. Find the number.",
            "x = 8",
            4,
            "Translate the words directly into an equation before solving.",
        ),
        row(
            "Algebra Challenge",
            5,
            "The sum of two consecutive odd numbers is 68. Find the numbers.",
            "33 and 35",
            4,
            "Represent the numbers as x and x + 2.",
        ),
        row(
            "Forming Expressions",
            5,
            "A rectangle has sides 2x + 1 and x - 3. Write and simplify an expression for its area.",
            "2x^2 - 5x - 3",
            4,
            "Form the product of the side lengths and then expand.",
        ),
        row(
            "Substitution",
            5,
            "When x = -2 and y = 3, work out 2x^2 - xy + 4y.",
            "17",
            4,
            "Substitute both variables carefully and preserve the negative sign in xy.",
        ),
    ]


def build_questions():
    rows = []
    rows.extend(build_algebra_expressions())
    rows.extend(build_forming_expressions())
    rows.extend(build_substitution())
    rows.extend(build_expanding_brackets())
    rows.extend(build_factorising())
    rows.extend(build_solving_equations())
    rows.extend(build_multistep_equations())
    rows.extend(build_algebra_challenge())
    rows.extend(build_gcse_higher_algebra())
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} deterministic algebra questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
