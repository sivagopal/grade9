from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-physics-topic-pack"
SUBJECT = "Science"


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


def build_forces():
    rows = []
    for i in range(1, 101):
        mass = 2 + (i % 9)
        g = 10
        weight = mass * g
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Physics - Forces",
                difficulty,
                f"Forces {i}: A mass of {mass} kg is on Earth. Calculate its weight using g = {g} N/kg.",
                f"{weight} N. Award 1 mark for using weight = mass x gravity and 1 mark for the correct answer.",
                2,
            )
        )
    return rows


def build_motion_and_speed():
    rows = []
    for i in range(1, 101):
        distance = 30 + i * 3
        time = 2 + (i % 8)
        speed = distance / time
        difficulty = 1 if i <= 30 else 2 if i <= 65 else 4
        rows.append(
            row(
                "Physics - Motion and Speed",
                difficulty,
                f"Motion {i}: A student travels {distance} m in {time} s. Calculate the average speed.",
                f"{speed:g} m/s. Award 1 mark for using speed = distance / time and 1 mark for the correct speed.",
                2,
            )
        )
    return rows


def build_energy():
    rows = []
    for i in range(1, 101):
        power = 20 + i * 2
        time = 5 + (i % 9)
        energy = power * time
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Physics - Energy",
                difficulty,
                f"Energy {i}: A device has a power of {power} W and runs for {time} s. Calculate the energy transferred.",
                f"{energy} J. Award 1 mark for using energy = power x time and 1 mark for the correct answer.",
                2,
            )
        )
    return rows


def build_electricity():
    rows = []
    for i in range(1, 101):
        current = 0.5 + (i % 8) * 0.5
        resistance = 2 + (i % 9)
        voltage = current * resistance
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Physics - Electricity",
                difficulty,
                f"Electricity {i}: A circuit has current {current:g} A and resistance {resistance} ohms. Calculate the voltage.",
                f"{voltage:g} V. Award 1 mark for using V = I x R and 1 mark for the correct voltage.",
                2,
            )
        )
    return rows


def build_waves():
    rows = []
    for i in range(1, 101):
        wavelength = 0.5 + (i % 10) * 0.2
        frequency = 2 + (i % 7)
        speed = wavelength * frequency
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Physics - Waves",
                difficulty,
                f"Waves {i}: A wave has wavelength {wavelength:g} m and frequency {frequency} Hz. Calculate the wave speed.",
                f"{speed:g} m/s. Award 1 mark for using wave speed = frequency x wavelength and 1 mark for the correct speed.",
                2,
            )
        )
    return rows


def build_magnetism():
    rows = []
    prompt_pairs = [
        ("north pole", "south pole", "attract"),
        ("north pole", "north pole", "repel"),
        ("south pole", "south pole", "repel"),
        ("south pole", "north pole", "attract"),
    ]
    rows = []
    for i in range(1, 101):
        pole1, pole2, result = prompt_pairs[(i - 1) % len(prompt_pairs)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Physics - Magnetism",
                difficulty,
                f"Magnetism {i}: Predict what happens when a {pole1} is brought near a {pole2}.",
                f"They {result}. Award 1 mark for recalling that unlike poles attract and like poles repel.",
                1,
            )
        )
    return rows


def build_pressure_and_fluids():
    rows = []
    for i in range(1, 101):
        force = 40 + i * 2
        area = 2 + (i % 8)
        pressure = force / area
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Physics - Pressure and Fluids",
                difficulty,
                f"Pressure {i}: A force of {force} N acts on an area of {area} m^2. Calculate the pressure.",
                f"{pressure:g} Pa. Award 1 mark for using pressure = force / area and 1 mark for the correct pressure.",
                2,
            )
        )
    return rows


def build_space():
    rows = []
    planets = [
        ("Mercury", "smallest orbital period"),
        ("Venus", "thick carbon dioxide atmosphere"),
        ("Earth", "liquid water on the surface"),
        ("Mars", "red appearance due to iron oxide"),
        ("Jupiter", "largest planet"),
        ("Saturn", "prominent rings"),
        ("Uranus", "rotates on its side"),
        ("Neptune", "furthest major planet from the Sun"),
    ]
    for i in range(1, 101):
        planet, fact = planets[(i - 1) % len(planets)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Physics - Space",
                difficulty,
                f"Space {i}: State one fact about {planet}.",
                f"Accept: {fact}. Other correct scientific facts about {planet} also gain the mark.",
                1,
            )
        )
    return rows


def build_heat_transfer():
    rows = []
    materials = [
        ("metal spoon", "conduction"),
        ("water in a pan", "convection"),
        ("the Sun warming Earth", "radiation"),
        ("a radiator warming air", "convection"),
    ]
    for i in range(1, 101):
        item, process = materials[(i - 1) % len(materials)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Physics - Heat Transfer",
                difficulty,
                f"Heat Transfer {i}: Name the main method of heat transfer in {item}.",
                f"{process}. Award 1 mark for the correct heat transfer process.",
                1,
            )
        )
    return rows


def build_light_and_sound():
    rows = []
    for i in range(1, 101):
        distance = 100 + i * 5
        time = 2 + (i % 6)
        speed = distance / time
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Physics - Light and Sound",
                difficulty,
                f"Light and Sound {i}: A sound travels {distance} m in {time} s. Calculate its average speed.",
                f"{speed:g} m/s. Award 1 mark for using speed = distance / time and 1 mark for the correct answer.",
                2,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_forces())
    rows.extend(build_motion_and_speed())
    rows.extend(build_energy())
    rows.extend(build_electricity())
    rows.extend(build_waves())
    rows.extend(build_magnetism())
    rows.extend(build_pressure_and_fluids())
    rows.extend(build_space())
    rows.extend(build_heat_transfer())
    rows.extend(build_light_and_sound())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 physics questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
