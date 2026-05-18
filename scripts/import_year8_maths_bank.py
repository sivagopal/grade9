from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-maths-ks3-bank"
LEGACY_SOURCES = ("year8-maths-topic-pack", "year8-maths-ks3-bank", "year8-algebra-pack")
SUBJECT = "Maths"


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


def build_number_skills():
    rows = []
    for n in range(1, 11):
        rows.append(row("Number Skills", 1, f"A club raises GBP {245 + 12 * n} on Friday and GBP {138 + 9 * n} on Saturday. How much is raised altogether?", f"GBP {383 + 21 * n}.", 2, "Add the two amounts carefully, keeping the place values aligned."))
        rows.append(row("Number Skills", 2, f"Work out 6 x ({14 + n}) - {27 + 2 * n}.", f"{57 + 4 * n}.", 2, "Evaluate the bracket first, then multiply, then subtract."))
        rows.append(row("Number Skills", 2, f"Write {3400 + 125 * n} as the product of a single digit and a power of 10.", f"{34 + n} x 10^2.", 2, "Factor out 100 from the number."))
        rows.append(row("Number Skills", 3, f"A coach seats {24 + n} people. How many full coaches are needed for {420 + 17 * n} students?", f"{((420 + 17 * n) + (24 + n) - 1) // (24 + n)} coaches.", 3, "Divide the number of students by the coach size and round up because a part-filled coach still counts."))
        rows.append(row("Number Skills", 3, f"Work out the highest common factor of {36 + 3 * n} and {60 + 5 * n}.", f"{_hcf(36 + 3 * n, 60 + 5 * n)}.", 2, "List factors or use prime factorisation, then choose the greatest common factor."))
    return rows


def build_negative_numbers():
    rows = []
    for n in range(1, 11):
        rows.append(row("Negative Numbers", 1, f"At 6 am the temperature is {-7 + n} degrees C. By midday it rises by {9 + n} degrees. What is the new temperature?", f"{2 + 2 * n} degrees C.", 2, "Add the rise to the starting negative temperature."))
        rows.append(row("Negative Numbers", 2, f"Work out {-18 - n} - ({7 + n}).", f"{-25 - 2 * n}.", 2, "Subtracting a positive number moves further left on the number line."))
        rows.append(row("Negative Numbers", 2, f"Calculate ({-5 - n}) x ({-3}).", f"{15 + 3 * n}.", 2, "A negative multiplied by a negative is positive."))
        rows.append(row("Negative Numbers", 3, f"A lift starts on floor {-2 - n}, goes up {9 + n} floors and then down {5 + 2 * n} floors. Which floor does it finish on?", f"Floor {2 - 2 * n}.", 3, "Track each change step by step from the starting floor."))
        rows.append(row("Negative Numbers", 3, f"Put these in order from smallest to largest: {-8 - n}, {3 - n}, {-1 + n}, {-5 + n}.", _ordered_list([-8 - n, 3 - n, -1 + n, -5 + n]), 3, "Negative numbers further left on the number line are smaller."))
    return rows


def build_fractions():
    rows = []
    for n in range(1, 11):
        rows.append(row("Fractions", 1, f"Work out 1/{2 + n % 3} + 1/{3 + n % 4}.", _fraction_add(1, 2 + n % 3, 1, 3 + n % 4), 3, "Find a common denominator, then add the numerators."))
        rows.append(row("Fractions", 2, f"Work out {2 + n}/{5 + n % 4} - 1/{5 + n % 4}.", _simplify_fraction(1 + n, 5 + n % 4), 2, "The denominators are equal, so subtract the numerators."))
        rows.append(row("Fractions", 2, f"Find 3/{4 + n % 3} of {24 + 6 * n}.", f"{3 * (24 + 6 * n) // (4 + n % 3)}.", 2, "Divide by the denominator, then multiply by the numerator."))
        rows.append(row("Fractions", 3, f"A recipe needs 2/3 of a litre of milk for one batch. How much milk is needed for {2 + n} batches?", _mixed_or_fraction(2 * (2 + n), 3), 3, "Multiply the fraction by the number of batches."))
        rows.append(row("Fractions", 3, f"Which is larger: {3 + n}/8 or {2 + n}/6? Give a reason.", _compare_fractions(3 + n, 8, 2 + n, 6), 3, "Use a common denominator or compare decimal values."))
    return rows


def build_decimals():
    rows = []
    for n in range(1, 11):
        a = round(12.4 + 0.6 * n, 1)
        b = round(3.7 + 0.4 * n, 1)
        rows.append(row("Decimals", 1, f"Work out {a} + {b}.", f"{round(a + b, 1)}.", 2, "Align the decimal points before adding."))
        c = round(18.5 + 0.7 * n, 1)
        d = round(4.3 + 0.2 * n, 1)
        rows.append(row("Decimals", 2, f"Work out {c} - {d}.", f"{round(c - d, 1)}.", 2, "Align decimal places, then subtract."))
        rows.append(row("Decimals", 2, f"A pen costs GBP {round(1.8 + 0.1 * n, 2)}. What is the cost of 6 pens?", f"GBP {round((1.8 + 0.1 * n) * 6, 2):.2f}.", 2, "Multiply the decimal by 6 and keep money to 2 decimal places."))
        rows.append(row("Decimals", 3, f"Round {round(24.356 + 0.111 * n, 3)} to 2 decimal places.", f"{round(round(24.356 + 0.111 * n, 3), 2):.2f}.", 2, "Look at the third decimal place to decide whether to round up."))
        rows.append(row("Decimals", 3, f"A runner completes {round(2.4 + 0.3 * n, 1)} km on Monday and {round(3.1 + 0.2 * n, 1)} km on Tuesday. How much further is this than a 5 km run?", f"{round((2.4 + 0.3 * n) + (3.1 + 0.2 * n) - 5, 1)} km.", 3, "Add the two distances first, then compare with 5 km."))
    return rows


def build_percentages():
    rows = []
    for n in range(1, 11):
        rows.append(row("Percentages", 1, f"Find {10 + 5 * n}% of {80 + 12 * n}.", f"{(10 + 5 * n) * (80 + 12 * n) / 100:g}.", 2, "Find 10% or 1% first, then scale."))
        rows.append(row("Percentages", 2, f"A jumper costing GBP {40 + 5 * n} is reduced by {15 + n}%. What is the sale price?", f"GBP {round((40 + 5 * n) * (100 - (15 + n)) / 100, 2):.2f}.", 3, "Find the discount, then subtract it from the original price."))
        rows.append(row("Percentages", 3, f"A school roll rises from {480 + 12 * n} to {516 + 15 * n}. Find the percentage increase.", f"{round(((516 + 15 * n) - (480 + 12 * n)) / (480 + 12 * n) * 100, 1)}%.", 3, "Increase divided by original, then multiply by 100."))
        rows.append(row("Percentages", 3, f"After a {20 + n}% increase, a bicycle costs GBP {372 + 12 * n}. What was the original price?", f"GBP {round((372 + 12 * n) / ((120 + n) / 100), 2):.2f}.", 4, "Treat the final amount as 120 + n percent of the original and divide."))
        rows.append(row("Percentages", 4, f"In a test, {28 + 2 * n} out of {35 + 2 * n} answers are correct. What percentage is this correct to 1 decimal place?", f"{round((28 + 2 * n) / (35 + 2 * n) * 100, 1)}%.", 3, "Write the score as a fraction, convert to a percentage, then round."))
    return rows


def build_ratio():
    rows = []
    for n in range(1, 11):
        a = 2 + n % 4
        b = 3 + n % 5
        multiplier = 6 + n
        total = (a + b) * multiplier
        rows.append(row("Ratio and Proportion", 2, f"Share GBP {total} in the ratio {a}:{b}.", f"GBP {a * multiplier} and GBP {b * multiplier}.", 3, "Find the value of one part, then multiply by each ratio number."))
        rows.append(row("Ratio and Proportion", 2, f"A recipe for 4 people uses {180 + 10 * n} g of flour. How much flour is needed for 10 people?", f"{(180 + 10 * n) * 10 / 4:g} g.", 3, "Scale up using a multiplier of 10/4."))
        rows.append(row("Ratio and Proportion", 3, f"Simplify the ratio {18 + 3 * n}:{30 + 5 * n}.", _simplify_ratio(18 + 3 * n, 30 + 5 * n), 2, "Divide both parts of the ratio by the highest common factor."))
        rows.append(row("Ratio and Proportion", 3, f"Blue paint and white paint are mixed in the ratio {1 + n % 3}:{4 + n % 4}. If {20 + 5 * n} litres of white paint are used, how much blue paint is needed?", f"{round((20 + 5 * n) * (1 + n % 3) / (4 + n % 4), 2):g} litres.", 3, "Match the known amount to its ratio part, then scale to the other part."))
        rows.append(row("Ratio and Proportion", 4, f"On a map, 3 cm represents {12 + n} km. What real distance is represented by {7 + n} cm?", f"{round((12 + n) * (7 + n) / 3, 2):g} km.", 3, "Use direct proportion: divide by 3 to get 1 cm, then multiply by the new map length."))
    return rows


def build_algebra():
    rows = []
    for n in range(1, 11):
        rows.append(row("Algebra", 1, f"Simplify {3 + n}x + {5 + n}x - {2 + n}x.", f"{6 + n}x.", 2, "Collect the like terms by adding and subtracting the coefficients."))
        rows.append(row("Algebra", 2, f"Write an expression for the total cost of {4 + n} notebooks at p pounds each and one ruler costing GBP {2 + n}.", f"{4 + n}p + {2 + n}.", 2, "Multiply the number of notebooks by p, then add the fixed cost."))
        rows.append(row("Algebra", 2, f"The perimeter of a rectangle is 2(3x + {n}) + 2(x + {4 + n}). Simplify the perimeter.", f"{8}x + {8 + 4 * n}.", 3, "Expand both brackets or double each side length, then collect like terms."))
        rows.append(row("Algebra", 3, f"When x = {2 + n}, work out 3x^2 - 2x + 5.", f"{3 * (2 + n) ** 2 - 2 * (2 + n) + 5}.", 3, "Substitute the value of x carefully, square first, then follow the order of operations."))
        rows.append(row("Algebra", 4, f"A number x is increased by {4 + n}, then the result is multiplied by 3. Write an expression for this and simplify it.", f"3(x + {4 + n}) = 3x + {12 + 3 * n}.", 3, "Translate the words into algebra, then expand the bracket."))
    return rows


def build_substitution():
    rows = []
    for n in range(1, 11):
        rows.append(row("Substitution", 1, f"When a = {2 + n} and b = {4 + n}, work out a + 2b.", f"{(2 + n) + 2 * (4 + n)}.", 2, "Replace a and b with their values, then calculate."))
        rows.append(row("Substitution", 2, f"When x = {3 + n}, work out 2x^2 - 5.", f"{2 * (3 + n) ** 2 - 5}.", 2, "Square x first, then multiply by 2, then subtract 5."))
        rows.append(row("Substitution", 2, f"When m = {1 + n} and n = {5 + n}, work out 3m + n.", f"{3 * (1 + n) + (5 + n)}.", 2, "Substitute each value into the expression."))
        rows.append(row("Substitution", 3, f"When p = {2 + n} and q = {6 + n}, work out (p + q) / 2.", f"{((2 + n) + (6 + n)) / 2:g}.", 2, "Add p and q, then divide by 2."))
        rows.append(row("Substitution", 4, f"When x = {n}, y = {n + 2} and z = {n + 4}, work out x(y + z).", f"{n * ((n + 2) + (n + 4))}.", 3, "Evaluate the bracket first, then multiply by x."))
    return rows


def build_expanding_brackets():
    rows = []
    for n in range(1, 11):
        rows.append(row("Expanding Brackets", 1, f"Expand {2 + n}(x + {3 + n}).", f"{2 + n}x + {(2 + n) * (3 + n)}.", 2, "Multiply the bracket term by term."))
        rows.append(row("Expanding Brackets", 2, f"Expand 3(2x - {1 + n}).", f"6x - {3 * (1 + n)}.", 2, "Multiply 3 by both terms inside the bracket."))
        rows.append(row("Expanding Brackets", 2, f"Expand -2(x - {4 + n}).", f"-2x + {2 * (4 + n)}.", 2, "A negative multiplier changes the signs when you expand."))
        rows.append(row("Expanding Brackets", 3, f"Expand and simplify 2(x + {2 + n}) + 3(x - {1 + n}).", f"5x + {4 + 2 * n - 3 - 3 * n}.", 3, "Expand each bracket and then collect like terms."))
        rows.append(row("Expanding Brackets", 4, f"Expand and simplify {2 + n}({1 + n}x + 3).", f"{(2 + n) * (1 + n)}x + {3 * (2 + n)}.", 3, "Multiply the outer term by each term inside the bracket."))
    return rows


def build_factorising():
    rows = []
    for n in range(1, 11):
        rows.append(row("Factorising", 1, f"Factorise {4 + n}x + {2 * (4 + n)}.", f"{4 + n}(x + 2).", 2, "Take out the highest common factor."))
        rows.append(row("Factorising", 2, f"Factorise fully {3 + n}x - {6 + 2 * n}.", f"{3 + n}(x - 2).", 2, "Both terms share a factor of 3 + n."))
        rows.append(row("Factorising", 3, f"Factorise x^2 + {5 + n}x.", f"x(x + {5 + n}).", 2, "Take x out as a common factor."))
        rows.append(row("Factorising", 3, f"Factorise x^2 + {7 + n}x + {10 + 3 * n} where the factors are given by inspection.", _factorise_quadratic(7 + n, 10 + 3 * n), 3, "Find two numbers that add to the x coefficient and multiply to the constant term."))
        rows.append(row("Factorising", 4, f"Factorise 2x^2 + {4 + 2 * n}x.", f"2x(x + {2 + n}).", 3, "Take out the highest common factor 2x."))
    return rows


def build_solving_equations():
    rows = []
    for n in range(1, 11):
        rows.append(row("Solving Equations", 1, f"Solve x + {4 + n} = {11 + 2 * n}.", f"x = {7 + n}.", 2, "Subtract the constant from both sides."))
        rows.append(row("Solving Equations", 2, f"Solve {3 + n}x = {24 + 6 * n}.", f"x = {(24 + 6 * n) // (3 + n)}.", 2, "Divide both sides by the coefficient of x."))
        rows.append(row("Solving Equations", 2, f"Solve 2x - {3 + n} = {11 + n}.", f"x = {7 + n}.", 3, "Add the constant to both sides, then divide by 2."))
        rows.append(row("Solving Equations", 3, f"Solve 5x + {2 + n} = {37 + 4 * n}.", f"x = {(35 + 3 * n) / 5:g}.", 3, "Subtract first, then divide by 5."))
        rows.append(row("Solving Equations", 4, f"Solve 4(x + {2 + n}) = {36 + 8 * n}.", f"x = {7 + n}.", 3, "Either divide first or expand the bracket, then isolate x."))
    return rows


def build_multistep_equations():
    rows = []
    for n in range(1, 11):
        rows.append(row("Multi-step Equations", 2, f"Solve 3x + {5 + n} = 2x + {17 + 2 * n}.", f"x = {12 + n}.", 3, "Move x terms to one side and constants to the other."))
        rows.append(row("Multi-step Equations", 3, f"Solve 2( x + {3 + n} ) = {18 + 4 * n}.", f"x = {6 + n}.", 3, "Either divide by 2 first or expand the bracket."))
        rows.append(row("Multi-step Equations", 3, f"Solve 5x - {7 + n} = 3x + {13 + n}.", f"x = {10 + n}.", 3, "Bring the x terms together, then solve the simpler equation."))
        rows.append(row("Multi-step Equations", 4, f"Solve 4(x - {2 + n}) + 6 = {30 + 4 * n}.", f"x = {8 + 2 * n}.", 4, "Expand the bracket, simplify, then isolate x."))
        rows.append(row("Multi-step Equations", 4, f"Solve 3(x + 4) - 2 = {25 + 3 * n}.", f"x = {(15 + 3 * n) / 3:g}.", 4, "Expand, simplify, and work backwards carefully."))
    return rows


def build_sequences():
    rows = []
    for n in range(1, 11):
        start = 4 + n
        step = 2 + n % 4
        rows.append(row("Sequences", 2, f"Find the next two terms in the sequence {start}, {start + step}, {start + 2 * step}, {start + 3 * step}.", f"{start + 4 * step} and {start + 5 * step}.", 2, "Look for the constant difference."))
        rows.append(row("Sequences", 3, f"Find the nth term of the sequence {start}, {start + step}, {start + 2 * step}, {start + 3 * step}.", f"{step}n + {start - step}.", 3, "Use nth term = difference x n + adjustment."))
        rows.append(row("Sequences", 3, f"The nth term of a sequence is {3 + n % 3}n + {2 + n}. Work out the 10th term.", f"{(3 + n % 3) * 10 + 2 + n}.", 2, "Substitute n = 10 into the formula."))
        rows.append(row("Sequences", 4, f"A sequence has nth term {2 + n % 4}n - {1 + n}. Which term is equal to {10 * (2 + n % 4) - (1 + n)}?", f"The 10th term.", 3, "Set the nth term equal to the given value and solve for n."))
        rows.append(row("Sequences", 4, f"Here is a growing pattern with totals {5 + n}, {9 + n}, {13 + n}, {17 + n}. Write a formula for term number t.", f"4t + {1 + n}.", 3, "The difference is 4, so the rule is linear."))
    return rows


def build_graphs():
    rows = []
    for n in range(1, 11):
        m = 2 + n % 3
        c = 1 + n
        rows.append(row("Graphs", 2, f"For the line y = {m}x + {c}, state the gradient and y-intercept.", f"Gradient {m}, y-intercept {c}.", 2, "In y = mx + c, m is the gradient and c is the y-intercept."))
        rows.append(row("Graphs", 2, f"Complete the table of values for y = x + {3 + n} when x = 0, 1, 2, 3.", f"{3 + n}, {4 + n}, {5 + n}, {6 + n}.", 2, "Substitute each x-value into the rule."))
        rows.append(row("Graphs", 3, f"A graph passes through (1, {m + c}) and (3, {3 * m + c}). Find the equation of the line.", f"y = {m}x + {c}.", 3, "Use the change in y over the change in x to find the gradient, then substitute a point."))
        rows.append(row("Graphs", 3, f"Two phone tariffs are modelled by y = {m}x + {c} and y = {m + 1}x + {c - 2}. Which tariff has the larger gradient?", f"The line y = {m + 1}x + {c - 2}.", 2, "Compare the coefficients of x."))
        rows.append(row("Graphs", 4, f"The line y = {m}x + {c} crosses the y-axis at A and the x-axis at B. Find the coordinates of A and B.", f"A = (0, {c}), B = ({-c / m:g}, 0).", 4, "At the y-axis x = 0. At the x-axis y = 0, so solve {m}x + {c} = 0."))
    return rows


def build_coordinate_geometry():
    rows = []
    for n in range(1, 11):
        x1, y1 = n, 2 + n
        x2, y2 = n + 4, 6 + n
        rows.append(row("Coordinate Geometry", 2, f"Find the midpoint of the line segment joining ({x1}, {y1}) and ({x2}, {y2}).", f"({(x1 + x2) / 2:g}, {(y1 + y2) / 2:g}).", 3, "Average the x-coordinates and y-coordinates separately."))
        rows.append(row("Coordinate Geometry", 3, f"Find the gradient of the line through ({x1}, {y1}) and ({x2}, {y2}).", f"{(y2 - y1) / (x2 - x1):g}.", 3, "Use change in y divided by change in x."))
        rows.append(row("Coordinate Geometry", 3, f"Point A is ({1 + n}, {4 + n}) and point B is ({5 + n}, {4 + n}). Find the distance AB.", f"{4}.", 2, "The points have the same y-coordinate, so count the horizontal difference."))
        rows.append(row("Coordinate Geometry", 4, f"Find the equation of the line with gradient {2 + n % 3} and y-intercept {1 + n}.", f"y = {2 + n % 3}x + {1 + n}.", 2, "Use the straight-line form y = mx + c."))
        rows.append(row("Coordinate Geometry", 4, f"The line y = {2 + n % 3}x + {1 + n} and the line y = -x + {7 + n} intersect. Explain how to find their intersection.", f"Set the equations equal: {2 + n % 3}x + {1 + n} = -x + {7 + n}, then solve for x and substitute back for y.", 4, "At the intersection the y-values are equal, so solve simultaneously."))
    return rows


def build_geometry():
    rows = []
    for n in range(1, 11):
        a = 30 + 3 * n
        b = 40 + 2 * n
        rows.append(row("Geometry and Angles", 1, f"Two angles in a triangle are {a} degrees and {b} degrees. Find the third angle.", f"{180 - a - b} degrees.", 2, "Angles in a triangle add to 180 degrees."))
        rows.append(row("Geometry and Angles", 2, f"Angles on a straight line are 3x and {60 + 2 * n}. Find x.", f"x = {(120 - 2 * n) / 3:g}.", 3, "Angles on a straight line add to 180 degrees."))
        rows.append(row("Geometry and Angles", 3, f"One exterior angle of a triangle is {110 + n} degrees and one opposite interior angle is {45 + n} degrees. Find the other opposite interior angle.", f"{65}.", 3, "An exterior angle equals the sum of the two opposite interior angles."))
        rows.append(row("Geometry and Angles", 3, f"A regular polygon has exterior angle {20 + n} degrees. How many sides does it have?", f"{360 / (20 + n):g} sides.", 3, "Number of sides = 360 divided by the exterior angle."))
        rows.append(row("Geometry and Angles", 4, f"In a triangle, the angles are x, x + {12 + n} and x + {24 + n}. Find x.", f"x = {(144 - 2 * n) / 3:g}.", 4, "Form an equation from the angle sum of 180 degrees."))
    return rows


def build_area_perimeter():
    rows = []
    for n in range(1, 11):
        length = 6 + n
        width = 3 + n % 5
        rows.append(row("Area and Perimeter", 1, f"A rectangle has length {length} cm and width {width} cm. Find its perimeter.", f"{2 * (length + width)} cm.", 2, "Perimeter of a rectangle is 2(length + width)."))
        rows.append(row("Area and Perimeter", 2, f"A rectangle has length {length} cm and width {width} cm. Find its area.", f"{length * width} cm^2.", 2, "Area of a rectangle is length x width."))
        rows.append(row("Area and Perimeter", 3, f"A garden is {length} m by {width + 2} m. Fencing costs GBP {4 + n} per metre. Find the total fencing cost.", f"GBP {2 * (length + width + 2) * (4 + n)}.", 3, "Find the perimeter first, then multiply by the cost per metre."))
        rows.append(row("Area and Perimeter", 3, f"A rectangular floor has area {length * width} m^2 and width {width} m. Find its length.", f"{length} m.", 2, "Length = area / width."))
        rows.append(row("Area and Perimeter", 4, f"A rectangle has sides x + {2 + n} and x + {5 + n}. Write and simplify an expression for its perimeter.", f"4x + {14 + 4 * n}.", 3, "Perimeter is twice the sum of the side lengths."))
    return rows


def build_surface_area_volume():
    rows = []
    for n in range(1, 11):
        l, w, h = 5 + n, 3 + n % 4, 2 + n % 3
        rows.append(row("Surface Area and Volume", 2, f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find its volume.", f"{l * w * h} cm^3.", 2, "Volume of a cuboid is length x width x height."))
        rows.append(row("Surface Area and Volume", 3, f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find its total surface area.", f"{2 * (l * w + l * h + w * h)} cm^2.", 3, "Add the areas of the 3 distinct faces and double the result."))
        cube = 3 + n
        rows.append(row("Surface Area and Volume", 3, f"A cube has side length {cube} cm. Find its surface area.", f"{6 * cube * cube} cm^2.", 2, "A cube has 6 identical square faces."))
        rows.append(row("Surface Area and Volume", 4, f"A right prism has cross-sectional area {12 + 2 * n} cm^2 and length {7 + n} cm. Find its volume.", f"{(12 + 2 * n) * (7 + n)} cm^3.", 3, "Volume of a prism is cross-sectional area x length."))
        rows.append(row("Surface Area and Volume", 4, f"A cuboid has volume {l * w * h} cm^3, length {l} cm and width {w} cm. Find its height.", f"{h} cm.", 3, "Rearrange volume = length x width x height."))
    return rows


def build_transformations():
    rows = []
    for n in range(1, 11):
        rows.append(row("Transformations", 2, f"Translate the point ({2 + n}, {3 + n}) by the vector ({1 + n % 3}, {-2 - n % 2}). State the new coordinates.", f"({2 + n + 1 + n % 3}, {3 + n - 2 - n % 2}).", 2, "Add the vector components to the coordinates."))
        rows.append(row("Transformations", 2, f"Reflect the point ({4 + n}, {2 + n}) in the y-axis. State the image.", f"({-(4 + n)}, {2 + n}).", 2, "Reflection in the y-axis changes the sign of x only."))
        rows.append(row("Transformations", 3, f"Rotate the point ({3 + n}, {1 + n}) 90 degrees anticlockwise about the origin. State the image.", f"({-(1 + n)}, {3 + n}).", 3, "The rule for a 90 degree anticlockwise rotation is (x, y) -> (-y, x)."))
        rows.append(row("Transformations", 3, f"Enlarge the point ({2 + n}, {1 + n}) by scale factor 2 about the origin. State the image.", f"({2 * (2 + n)}, {2 * (1 + n)}).", 2, "Multiply both coordinates by the scale factor."))
        rows.append(row("Transformations", 4, f"Shape A is translated by the vector ({2 + n % 3}, {3 + n % 2}) and then reflected in the x-axis. Describe the effect on the point ({1 + n}, {2 + n}).", f"First to ({1 + n + 2 + n % 3}, {2 + n + 3 + n % 2}), then to ({1 + n + 2 + n % 3}, {-2 - n - 3 - n % 2}).", 4, "Apply the translation first, then reflect by changing the sign of y."))
    return rows


def build_statistics():
    rows = []
    for n in range(1, 11):
        values = [2 + n, 4 + n, 7 + n, 9 + n, 12 + n]
        rows.append(row("Statistics and Probability", 2, f"Find the mean of {', '.join(str(v) for v in values)}.", f"{sum(values) / len(values):g}.", 2, "Add the values and divide by how many there are."))
        values2 = [1 + n, 3 + n, 3 + n, 5 + n, 8 + n]
        rows.append(row("Statistics and Probability", 2, f"Find the median and the range of {', '.join(str(v) for v in values2)}.", f"Median {values2[2]}, range {values2[-1] - values2[0]}.", 3, "For ordered data, the median is the middle value and the range is largest minus smallest."))
        rows.append(row("Statistics and Probability", 3, f"A bag contains {2 + n} red, {3 + n} blue and {5 + n} green counters. Find the probability of selecting a blue counter.", _probability_text(3 + n, (2 + n) + (3 + n) + (5 + n)), 2, "Probability = favourable outcomes / total outcomes."))
        rows.append(row("Statistics and Probability", 3, f"A spinner has sections scored {1 + n}, {2 + n}, {3 + n} and {4 + n}. What is the mean score if each section is equally likely?", f"{((1 + n) + (2 + n) + (3 + n) + (4 + n)) / 4:g}.", 2, "With equally likely outcomes, take the average of the scores."))
        rows.append(row("Statistics and Probability", 4, f"In a class survey, {8 + n} students chose football, {6 + n} chose netball and {4 + n} chose swimming. What fraction chose football?", _probability_text(8 + n, (8 + n) + (6 + n) + (4 + n)), 3, "Write football choices over total students and simplify."))
    return rows


def build_questions():
    rows = []
    rows.extend(build_number_skills())
    rows.extend(build_negative_numbers())
    rows.extend(build_fractions())
    rows.extend(build_decimals())
    rows.extend(build_percentages())
    rows.extend(build_ratio())
    rows.extend(build_algebra())
    rows.extend(build_substitution())
    rows.extend(build_expanding_brackets())
    rows.extend(build_factorising())
    rows.extend(build_solving_equations())
    rows.extend(build_multistep_equations())
    rows.extend(build_sequences())
    rows.extend(build_graphs())
    rows.extend(build_coordinate_geometry())
    rows.extend(build_geometry())
    rows.extend(build_area_perimeter())
    rows.extend(build_surface_area_volume())
    rows.extend(build_transformations())
    rows.extend(build_statistics())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    with db.connect() as conn:
        placeholders = ",".join("?" for _ in LEGACY_SOURCES)
        conn.execute(f"DELETE FROM questions WHERE subject = ? AND source IN ({placeholders})", (SUBJECT, *LEGACY_SOURCES))
        conn.commit()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 maths KS3-style questions into the SQLite question bank.")


def _hcf(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def _simplify_fraction(num, den):
    factor = _hcf(num, den)
    num //= factor
    den //= factor
    return f"{num}" if den == 1 else f"{num}/{den}"


def _fraction_add(a_num, a_den, b_num, b_den):
    total_num = a_num * b_den + b_num * a_den
    total_den = a_den * b_den
    return _simplify_fraction(total_num, total_den)


def _mixed_or_fraction(num, den):
    whole = num // den
    rem = num % den
    if rem == 0:
        return str(whole)
    if whole == 0:
        return f"{rem}/{den}"
    return f"{whole} {rem}/{den}"


def _compare_fractions(a_num, a_den, b_num, b_den):
    left = a_num / a_den
    right = b_num / b_den
    if left > right:
        return f"{a_num}/{a_den} is larger."
    if right > left:
        return f"{b_num}/{b_den} is larger."
    return "They are equal."


def _ordered_list(values):
    return ", ".join(str(value) for value in sorted(values))


def _simplify_ratio(a, b):
    factor = _hcf(a, b)
    return f"{a // factor}:{b // factor}"


def _factorise_quadratic(b_coeff, constant):
    for first in range(1, constant + 1):
        if constant % first != 0:
            continue
        second = constant // first
        if first + second == b_coeff:
            return f"(x + {first})(x + {second})"
    return "No integer factorisation."


def _probability_text(num, den):
    return _simplify_fraction(num, den)


if __name__ == "__main__":
    main()
