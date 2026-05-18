from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-maths-grade9-bank"
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


def build_percentages():
    return [
        row("Percentages", 4, "A shop increases the price of a coat by 12% and then reduces the new price by 12%. Is the final price the same as the original? Explain using a GBP 80 coat.", "No. GBP 80 rises to GBP 89.60, then falls to GBP 78.85. The final price is GBP 1.15 lower than the original.", 4),
        row("Percentages", 5, "After a 15% discount, a bicycle costs GBP 289. Find the original price.", "GBP 340.", 4),
        row("Percentages", 5, "The population of a town rises by 8% one year and falls by 5% the next. Starting from 25,000, find the final population and the overall percentage change.", "25,650 and an overall increase of 2.6%.", 5),
        row("Percentages", 4, "A student scores 28/35 in one test and 34/45 in another. Which score is better as a percentage, and by how many percentage points?", "28/35 = 80%, 34/45 = 75.6% recurring, so the first is better by about 4.4 percentage points.", 4),
        row("Percentages", 5, "A phone costs GBP 420 including 20% VAT. Work out the price before VAT.", "GBP 350.", 4),
    ]


def build_number_skills():
    return [
        row("Number Skills", 4, "A concert hall has 28 rows of 24 seats. If 517 tickets are sold, how many seats are empty?", "155 seats.", 3),
        row("Number Skills", 5, "A shop buys 240 notebooks for GBP 1.35 each and sells them for GBP 1.90 each. Work out the total profit.", "GBP 132.", 4),
        row("Number Skills", 4, "A water tank starts with 12.5 litres. It is filled by 0.75 litres each minute for 18 minutes. How much water is in the tank then?", "26 litres.", 3),
        row("Number Skills", 5, "Work out (84 / 6) x 1.5 + 17.", "38.", 3),
        row("Number Skills", 5, "A charity receives GBP 248.50 on Friday, GBP 173.75 on Saturday and GBP 96.40 on Sunday. It spends GBP 285.90 on equipment. How much money is left?", "GBP 232.75.", 4),
    ]


def build_negative_numbers():
    return [
        row("Negative Numbers", 4, "The temperature is -7 C at 6 am and 5 C at midday. By how many degrees has it increased?", "12 C.", 2),
        row("Negative Numbers", 5, "A bank account is at -GBP 35. A payment of GBP 62 goes in, then GBP 19 is spent. What is the new balance?", "GBP 8.", 3),
        row("Negative Numbers", 5, "Work out -4 + 3(2 - 7).", "-19.", 3),
        row("Negative Numbers", 4, "A lift starts on floor -3, goes up 11 floors, down 4 floors, then up 6 floors. Which floor does it finish on?", "Floor 10.", 3),
        row("Negative Numbers", 5, "Find the product of -6 and (-3 - 8).", "66.", 3),
    ]


def build_fractions():
    return [
        row("Fractions", 4, "Three quarters of a class are girls. Two fifths of the girls play netball. What fraction of the whole class are girls who play netball?", "3/10.", 4),
        row("Fractions", 5, "Which is greater, 5/6 or 7/9? Show a convincing method.", "5/6 is greater.", 4),
        row("Fractions", 4, "A recipe uses 2/3 litre of juice per jug. How many full jugs can be made from 5 litres, and how much juice is left?", "7 full jugs and 1/3 litre left.", 4),
        row("Fractions", 5, "Work out 1 3/4 - 2/3.", "1 1/12.", 4),
        row("Fractions", 5, "Sam spends 3/8 of his money on a book and 1/4 on lunch. What fraction of his money does he have left?", "3/8.", 3),
    ]


def build_decimals():
    return [
        row("Decimals", 4, "Work out 0.24 x 15.", "3.6.", 2),
        row("Decimals", 4, "A bottle holds 1.75 litres. Eight bottles are filled from a 15 litre container. How much liquid is left?", "1 litre.", 3),
        row("Decimals", 5, "Round 38.476 to 1 decimal place and to 2 significant figures.", "38.5 and 38.", 3),
        row("Decimals", 5, "A taxi fare is GBP 3.60 plus GBP 1.45 per mile. Work out the cost of an 8.2 mile journey.", "GBP 15.49.", 4),
        row("Decimals", 4, "A runner completes 2.45 km, 2.55 km and 2.80 km on three days. Find the mean distance.", "2.6 km.", 3),
    ]


def build_ratio():
    return [
        row("Ratio and Proportion", 4, "Red, blue and green counters are in the ratio 4:5:7. There are 96 counters altogether. How many green counters are there?", "42 counters.", 4),
        row("Ratio and Proportion", 5, "Flour and sugar are mixed in the ratio 5:3. Another mixture is in the ratio 7:4. Which mixture is sweeter, and justify your answer without converting to decimals only.", "The first mixture is sweeter because the sugar fractions are 3/8 and 4/11, and 3/8 is greater than 4/11.", 5),
        row("Ratio and Proportion", 4, "A map uses the scale 1 : 25,000. Two points are 7.2 cm apart on the map. What is the real distance in kilometres?", "1.8 km.", 4),
        row("Ratio and Proportion", 5, "A drink is made from juice and water in the ratio 2:7. How much water must be added to 600 ml of juice to keep the drink in the same ratio?", "2100 ml.", 4),
        row("Ratio and Proportion", 5, "A recipe for 6 people needs 420 g of pasta. A cook has 1.12 kg of pasta. What is the greatest whole number of people the cook can serve using the same proportion?", "16 people.", 4),
    ]


def build_factors_multiples_primes():
    return [
        row("Factors Multiples and Primes", 4, "Write 504 and 630 as products of prime factors. Hence find their highest common factor and lowest common multiple.", "504 = 2^3 x 3^2 x 7, 630 = 2 x 3^2 x 5 x 7, so HCF = 126 and LCM = 2520.", 5),
        row("Factors Multiples and Primes", 5, "Two positive integers have highest common factor 18 and lowest common multiple 756. One of the integers is 54. Find the other integer.", "252, because 54 x n = 18 x 756, so n = 252.", 4),
        row("Factors Multiples and Primes", 5, "Find the smallest positive integer k such that 360k is a square number. You must justify your answer using prime factors.", "k = 10, because 360 = 2^3 x 3^2 x 5 and multiplying by 2 x 5 gives 2^4 x 3^2 x 5^2.", 4),
        row("Factors Multiples and Primes", 5, "Find the smallest positive integer m such that 756m is a cube number. You must justify your answer using prime factors.", "m = 98, because 756 = 2^2 x 3^3 x 7 and multiplying by 2 x 7^2 gives 2^3 x 3^3 x 7^3.", 5),
        row("Factors Multiples and Primes", 5, "Show algebraically that the sum of any three consecutive integers is always a multiple of 3.", "Let the integers be n, n + 1 and n + 2. Their sum is 3n + 3 = 3(n + 1), so it is always a multiple of 3.", 4),
    ]


def build_algebra():
    return [
        row("Algebra", 4, "Simplify fully: 3(2x - 5) - 2(x + 7).", "4x - 29.", 3),
        row("Algebra", 5, "The sum of three consecutive integers is 93. Find the integers and show your algebra.", "30, 31 and 32.", 4),
        row("Algebra", 5, "A rectangle has width x and length x + 5. Its perimeter is 42. Find x and then the area.", "x = 8 and the area is 104 square units.", 5),
        row("Algebra", 4, "When x = -2 and y = 5, work out 2x^2 - 3y + xy.", "-19.", 3),
        row("Algebra", 5, "Two cinema tickets and three drinks cost GBP 21. One ticket costs twice as much as one drink. Work out the cost of one ticket and one drink.", "Ticket GBP 6 and drink GBP 3.", 4),
    ]


def build_substitution():
    return [
        row("Substitution", 4, "When x = -3 and y = 4, work out 2x^2 - y.", "14.", 3),
        row("Substitution", 5, "When a = 5 and b = -2, work out 3a - 2b^2.", "7.", 3),
        row("Substitution", 4, "Use p = 2l + 2w to find the perimeter when l = 8.5 cm and w = 3.2 cm.", "23.4 cm.", 3),
        row("Substitution", 5, "Use C = (F - 32) x 5/9 to convert 68 F to degrees Celsius.", "20 C.", 4),
        row("Substitution", 5, "If n = 7, work out 3n^2 - 4n + 6.", "125.", 3),
    ]


def build_expanding_brackets():
    return [
        row("Expanding Brackets", 4, "Expand and simplify 3(2x + 5) - 4(x - 1).", "2x + 19.", 3),
        row("Expanding Brackets", 5, "Expand and simplify -2(3x - 7) + 5(x + 4).", "-x + 34.", 3),
        row("Expanding Brackets", 5, "Solve 4(x + 3) + 2(x - 5) = 32.", "x = 5.", 4),
        row("Expanding Brackets", 4, "Expand and simplify 6 - 2(x - 3) + 3(2x + 1).", "4x + 15.", 3),
        row("Expanding Brackets", 5, "The area of a rectangle is 5(x + 2). Write and simplify an expression for the area.", "5x + 10.", 2),
    ]


def build_equations():
    return [
        row("Solving Equations", 4, "Solve 5x - 7 = 3x + 11.", "x = 9.", 3),
        row("Multi-step Equations", 5, "Solve 3(2x - 1) = 4x + 14.", "x = 8.5.", 4),
        row("Solving Equations", 4, "Solve 7 - 2(x - 3) = 13.", "x = 0.", 3),
        row("Multi-step Equations", 5, "A number is multiplied by 4, then 9 is added, and the result is 3 less than twice the original number. Find the number.", "x = -6.", 4),
        row("Solving Equations", 5, "Solve 2(x + 5) + 3(x - 1) = 4x + 17.", "x = 10.", 4),
    ]


def build_factorising():
    return [
        row("Factorising", 4, "Factorise fully: 6x + 15.", "3(2x + 5).", 2),
        row("Factorising", 5, "Factorise x^2 + 9x + 20.", "(x + 4)(x + 5).", 3),
        row("Factorising", 5, "Factorise 2x^2 + 10x.", "2x(x + 5).", 2),
        row("Factorising", 4, "Expand and then factorise back to check: (x + 3)(x + 8).", "Expanded form x^2 + 11x + 24, so the factorised form is (x + 3)(x + 8).", 3),
        row("Factorising", 5, "A rectangle has area x^2 + 7x + 12. If one side is x + 3, find the other side.", "x + 4.", 3),
    ]


def build_sequences():
    return [
        row("Sequences", 4, "Find the nth term of 5, 9, 13, 17, ...", "4n + 1.", 3),
        row("Sequences", 5, "The nth term of a sequence is 3n + 2. Which term is 62?", "The 20th term.", 3),
        row("Sequences", 5, "A pattern has 7 tiles in term 1, 12 in term 2 and 17 in term 3. Find an nth term rule and use it to work out term 25.", "5n + 2 and term 25 is 127.", 4),
        row("Sequences", 4, "Explain why 4n + 3 can never give the value 100 for a term in a sequence.", "Because 100 - 3 = 97, and 97 is not divisible by 4, so there is no whole-number value of n.", 4),
        row("Sequences", 5, "Two sequences have nth terms 2n + 7 and 5n - 8. Find the first term number where they are equal.", "n = 5.", 4),
    ]


def build_graphs():
    return [
        row("Graphs", 4, "Find the equation of the line through (2, 5) and (6, 13).", "y = 2x + 1.", 4),
        row("Graphs", 5, "Two lines have equations y = 3x - 4 and y = -x + 12. Find their point of intersection.", "(4, 8).", 4),
        row("Graphs", 4, "A straight line has gradient -2 and passes through (3, 7). Find its equation.", "y = -2x + 13.", 4),
        row("Graphs", 5, "The line y = 4x + 1 crosses the x-axis at A. Find the coordinates of A and explain your method.", "(-0.25, 0).", 3),
        row("Graphs", 5, "Which has the greater gradient: the line through (1, 3) and (5, 11), or the line through (2, 7) and (6, 12)?", "The first line. Its gradient is 2, while the second line has gradient 1.25.", 4),
    ]


def build_coordinate_geometry():
    return [
        row("Coordinate Geometry", 5, "Find the midpoint of the line joining (-3, 4) and (7, -2).", "(2, 1).", 3),
        row("Coordinate Geometry", 5, "Triangle A(1, 2), B(7, 2), C(4, 8) is drawn on a grid. Find the area of the triangle.", "18 square units.", 4),
        row("Coordinate Geometry", 5, "Find the gradient of the line through (-2, 5) and (4, -1).", "-1.", 3),
        row("Coordinate Geometry", 5, "A line has equation y = x - 3. Find the equation of the line perpendicular to it through (2, 4).", "y = -x + 6.", 5),
        row("Coordinate Geometry", 5, "Point P is (3, -1). It is translated by the vector (-5, 4). Find the image of P.", "(-2, 3).", 2),
    ]


def build_geometry():
    return [
        row("Geometry and Angles", 4, "Angles in a triangle are x, x + 25 and x + 35. Find x.", "x = 40.", 4),
        row("Geometry and Angles", 5, "A regular polygon has interior angle 156 degrees. How many sides does it have?", "15 sides.", 5),
        row("Geometry and Angles", 5, "A transversal crosses parallel lines. One angle is 68 degrees. State three other angles that must appear and justify each.", "Another 68 degrees by corresponding or alternate angles, another 112 degrees by supplementary angle on a straight line, and a further 112 degrees by corresponding/alternate to that obtuse angle.", 5),
        row("Geometry and Angles", 4, "The exterior angle of a triangle is 127 degrees. One opposite interior angle is 54 degrees. Find the other opposite interior angle.", "73 degrees.", 3),
        row("Geometry and Angles", 5, "A right-angled triangle has one acute angle of 37 degrees. Find the other acute angle and explain why.", "53 degrees, because the two acute angles in a right-angled triangle add to 90 degrees.", 3),
    ]


def build_measure():
    return [
        row("Area and Perimeter", 4, "A rectangle has perimeter 46 cm and length 15 cm. Find its width and area.", "Width 8 cm and area 120 cm^2.", 4),
        row("Surface Area and Volume", 5, "A cuboid has length 8 cm, width 5 cm and height 3 cm. Find its total surface area.", "158 cm^2.", 4),
        row("Surface Area and Volume", 5, "A prism has cross-sectional area 24 cm^2 and length 11 cm. Find its volume.", "264 cm^3.", 3),
        row("Area and Perimeter", 5, "A rectangle and a square have the same perimeter of 36 cm. The square has side length 9 cm. If the rectangle has length 12 cm, what is its width and which shape has the greater area?", "Rectangle width 6 cm. Square area 81 cm^2, rectangle area 72 cm^2, so the square has the greater area.", 5),
        row("Surface Area and Volume", 4, "A cube has volume 343 cm^3. Find its side length.", "7 cm.", 3),
    ]


def build_statistics_probability():
    return [
        row("Statistics and Probability", 4, "Find the mean, median and range of 6, 9, 9, 11, 15.", "Mean 10, median 9, range 9.", 4),
        row("Statistics and Probability", 5, "A bag contains 4 red, 3 blue and 5 green counters. One counter is taken at random. What is the probability that it is not blue?", "9/12 = 3/4.", 3),
        row("Statistics and Probability", 5, "In a survey, 18 students choose football, 12 choose basketball and 10 choose tennis. Draw no chart, but state the angle needed for football in a pie chart.", "162 degrees.", 4),
        row("Statistics and Probability", 4, "The scores on a quiz are 7, 8, 8, 10, 12, 15. Find the mean score.", "10.", 3),
        row("Statistics and Probability", 5, "A spinner has equal sections labelled 1, 2, 3, 4, 5, 6. It is spun once. What is the probability of getting a prime number or a multiple of 4?", "4/6 = 2/3.", 4),
    ]


def build_transformations():
    return [
        row("Transformations", 4, "Reflect the point (6, -3) in the y-axis.", "(-6, -3).", 2),
        row("Transformations", 5, "Rotate the point (4, 1) 90 degrees anticlockwise about the origin.", "(-1, 4).", 3),
        row("Transformations", 5, "Enlarge the point (-2, 5) by scale factor 3 about the origin.", "(-6, 15).", 3),
        row("Transformations", 4, "Translate the point (3, -2) by the vector (-5, 7).", "(-2, 5).", 2),
        row("Transformations", 5, "A point is reflected in the x-axis and then translated by the vector (2, -1). What happens to the point (4, 3)?", "(6, -4).", 4),
    ]


def build_questions():
    rows = []
    rows.extend(build_percentages())
    rows.extend(build_number_skills())
    rows.extend(build_negative_numbers())
    rows.extend(build_fractions())
    rows.extend(build_decimals())
    rows.extend(build_ratio())
    rows.extend(build_factors_multiples_primes())
    rows.extend(build_algebra())
    rows.extend(build_substitution())
    rows.extend(build_expanding_brackets())
    rows.extend(build_equations())
    rows.extend(build_factorising())
    rows.extend(build_sequences())
    rows.extend(build_graphs())
    rows.extend(build_coordinate_geometry())
    rows.extend(build_geometry())
    rows.extend(build_measure())
    rows.extend(build_statistics_probability())
    rows.extend(build_transformations())
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} higher-standard maths questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
