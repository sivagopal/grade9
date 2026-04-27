from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-chemistry-topic-pack"
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


def build_particles_and_states():
    rows = []
    states = [("solid", "closely packed and vibrate in fixed positions"),
              ("liquid", "close together and move past each other"),
              ("gas", "far apart and move rapidly in all directions")]
    for i in range(1, 101):
        state, desc = states[(i - 1) % 3]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Particles and States",
                difficulty,
                f"Particles {i}: Describe how particles are arranged and move in a {state}.",
                f"In a {state}, particles are {desc}. Award 1 mark for arrangement and 1 mark for movement.",
                2,
            )
        )
    return rows


def build_elements_compounds_mixtures():
    rows = []
    prompts = [
        ("oxygen", "element"),
        ("water", "compound"),
        ("air", "mixture"),
        ("iron", "element"),
        ("carbon dioxide", "compound"),
    ]
    for i in range(1, 101):
        name, kind = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Elements Compounds and Mixtures",
                difficulty,
                f"Classification {i}: Classify {name} as an element, compound, or mixture.",
                f"{kind}. Award 1 mark for the correct classification.",
                1,
            )
        )
    return rows


def build_atoms_and_periodic_table():
    rows = []
    elements = [
        ("hydrogen", 1),
        ("carbon", 6),
        ("oxygen", 8),
        ("sodium", 11),
        ("magnesium", 12),
    ]
    for i in range(1, 101):
        element, atomic_number = elements[(i - 1) % len(elements)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Chemistry - Atoms and the Periodic Table",
                difficulty,
                f"Periodic Table {i}: State the atomic number of {element}.",
                f"{atomic_number}. Award 1 mark for the correct atomic number.",
                1,
            )
        )
    return rows


def build_separation_techniques():
    rows = []
    methods = [
        ("sand from water", "filtration"),
        ("salt from salt water", "evaporation or crystallisation"),
        ("different dyes in ink", "chromatography"),
        ("pure water from seawater", "distillation"),
    ]
    for i in range(1, 101):
        mixture, method = methods[(i - 1) % len(methods)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Separation Techniques",
                difficulty,
                f"Separation {i}: Name a suitable method to separate {mixture}.",
                f"{method}. Award 1 mark for a correct separation method.",
                1,
            )
        )
    return rows


def build_acids_alkalis_indicators():
    rows = []
    substances = [
        ("lemon juice", "acid"),
        ("soap solution", "alkali"),
        ("vinegar", "acid"),
        ("baking soda solution", "alkali"),
    ]
    for i in range(1, 101):
        substance, kind = substances[(i - 1) % len(substances)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Acids Alkalis and Indicators",
                difficulty,
                f"Acids and Alkalis {i}: State whether {substance} is an acid or an alkali.",
                f"{kind}. Award 1 mark for the correct identification.",
                1,
            )
        )
    return rows


def build_reactions_and_energy():
    rows = []
    reaction_types = [
        ("combustion", "exothermic"),
        ("neutralisation", "exothermic"),
        ("thermal decomposition", "endothermic"),
        ("photosynthesis", "endothermic"),
    ]
    for i in range(1, 101):
        reaction, energy = reaction_types[(i - 1) % len(reaction_types)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Chemistry - Reactions and Energy",
                difficulty,
                f"Energy Changes {i}: State whether {reaction} is usually exothermic or endothermic.",
                f"{energy}. Award 1 mark for the correct energy change.",
                1,
            )
        )
    return rows


def build_metals_and_non_metals():
    rows = []
    comparisons = [
        ("metal", "good conductor of electricity"),
        ("non-metal", "poor conductor of electricity"),
        ("metal", "malleable"),
        ("non-metal", "often brittle when solid"),
    ]
    for i in range(1, 101):
        kind, property_text = comparisons[(i - 1) % len(comparisons)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Metals and Non-metals",
                difficulty,
                f"Materials {i}: Which type of substance is usually {property_text}: a metal or a non-metal?",
                f"{kind}. Award 1 mark for the correct classification.",
                1,
            )
        )
    return rows


def build_chemical_formulae():
    rows = []
    formulae = [
        ("water", "H2O"),
        ("carbon dioxide", "CO2"),
        ("oxygen", "O2"),
        ("sodium chloride", "NaCl"),
        ("magnesium oxide", "MgO"),
    ]
    for i in range(1, 101):
        name, formula = formulae[(i - 1) % len(formulae)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Chemistry - Chemical Formulae",
                difficulty,
                f"Formulae {i}: Write the chemical formula for {name}.",
                f"{formula}. Award 1 mark for the correct chemical formula.",
                1,
            )
        )
    return rows


def build_environmental_chemistry():
    rows = []
    facts = [
        ("carbon dioxide", "greenhouse gas"),
        ("sulfur dioxide", "acid rain"),
        ("methane", "greenhouse gas"),
        ("carbon monoxide", "poisonous gas"),
    ]
    for i in range(1, 101):
        substance, effect = facts[(i - 1) % len(facts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "Chemistry - Environmental Chemistry",
                difficulty,
                f"Environment {i}: State one environmental issue linked to {substance}.",
                f"Accept: {effect}. Award 1 mark for a correct linked issue or effect.",
                1,
            )
        )
    return rows


def build_practical_skills():
    rows = []
    apparatus = [
        ("measuring liquid volume accurately", "measuring cylinder"),
        ("heating a substance strongly", "Bunsen burner"),
        ("holding chemicals during a reaction", "test tube or beaker"),
        ("measuring mass", "balance"),
    ]
    for i in range(1, 101):
        task, equipment = apparatus[(i - 1) % len(apparatus)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "Chemistry - Practical Skills",
                difficulty,
                f"Practical Skills {i}: Name a piece of laboratory equipment used for {task}.",
                f"{equipment}. Award 1 mark for a suitable piece of equipment.",
                1,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_particles_and_states())
    rows.extend(build_elements_compounds_mixtures())
    rows.extend(build_atoms_and_periodic_table())
    rows.extend(build_separation_techniques())
    rows.extend(build_acids_alkalis_indicators())
    rows.extend(build_reactions_and_energy())
    rows.extend(build_metals_and_non_metals())
    rows.extend(build_chemical_formulae())
    rows.extend(build_environmental_chemistry())
    rows.extend(build_practical_skills())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 chemistry questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
