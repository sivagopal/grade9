from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-french-topic-pack"
SUBJECT = "French"


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


def build_core_vocabulary():
    rows = []
    prompts = [
        ("la maison", "the house"),
        ("l'ecole", "school"),
        ("le chien", "the dog"),
        ("le livre", "the book"),
        ("la voiture", "the car"),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "French - Core Vocabulary",
                difficulty,
                f"Vocabulary {i}: Translate '{french}' into English.",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_numbers_and_time():
    rows = []
    numbers = {
        11: "onze",
        12: "douze",
        13: "treize",
        14: "quatorze",
        15: "quinze",
        16: "seize",
        17: "dix-sept",
        18: "dix-huit",
        19: "dix-neuf",
        20: "vingt",
    }
    for i in range(1, 101):
        number = 10 + (i % 10) + 1
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "French - Numbers and Time",
                difficulty,
                f"Numbers {i}: Write the number {number} in French.",
                f"{numbers[number]}. Award 1 mark for the correct French number.",
                1,
            )
        )
    return rows


def build_family_and_descriptions():
    rows = []
    prompts = [
        ("mon frere", "my brother"),
        ("ma soeur", "my sister"),
        ("mon pere", "my father"),
        ("ma mere", "my mother"),
        ("ma famille", "my family"),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "French - Family and Descriptions",
                difficulty,
                f"Family {i}: Translate '{french}' into English.",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_school_topic():
    rows = []
    prompts = [
        ("J'aime les maths.", "I like maths."),
        ("Je n'aime pas l'histoire.", "I do not like history."),
        ("Ma matiere preferee est l'art.", "My favourite subject is art."),
        ("L'ecole est interessante.", "School is interesting."),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 4
        rows.append(
            row(
                "French - School",
                difficulty,
                f"School {i}: Translate into English: '{french}'",
                f"{english}. Award 1 mark for each correct idea translated.",
                2,
            )
        )
    return rows


def build_grammar_verbs():
    rows = []
    prompts = [
        ("je", "jouer", "je joue"),
        ("tu", "habiter", "tu habites"),
        ("il", "aimer", "il aime"),
        ("nous", "parler", "nous parlons"),
        ("ils", "regarder", "ils regardent"),
    ]
    for i in range(1, 101):
        pronoun, infinitive, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "French - Grammar Verbs",
                difficulty,
                f"Grammar {i}: Conjugate the verb '{infinitive}' with '{pronoun}' in the present tense.",
                f"{answer}. Award 1 mark for the correct conjugated form.",
                1,
            )
        )
    return rows


def build_negatives_and_opinions():
    rows = []
    prompts = [
        ("Je n'aime pas le sport.", "I do not like sport."),
        ("Je deteste les devoirs.", "I hate homework."),
        ("J'adore la musique.", "I love music."),
        ("Je prefere le francais.", "I prefer French."),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "French - Negatives and Opinions",
                difficulty,
                f"Opinions {i}: Translate into English: '{french}'",
                f"{english}. Award 1 mark for the opinion phrase and 1 mark for the object or subject.",
                2,
            )
        )
    return rows


def build_free_time():
    rows = []
    prompts = [
        ("Je joue au foot.", "I play football."),
        ("J'ecoute de la musique.", "I listen to music."),
        ("Je regarde la tele.", "I watch TV."),
        ("Je lis souvent.", "I often read."),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "French - Free Time",
                difficulty,
                f"Free Time {i}: Translate into English: '{french}'",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_food_and_drink():
    rows = []
    prompts = [
        ("Je mange du pain.", "I eat bread."),
        ("Je bois de l'eau.", "I drink water."),
        ("J'aime la pizza.", "I like pizza."),
        ("Je n'aime pas le cafe.", "I do not like coffee."),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "French - Food and Drink",
                difficulty,
                f"Food {i}: Translate into English: '{french}'",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_daily_routine():
    rows = []
    prompts = [
        ("Je me leve a sept heures.", "I get up at seven o'clock."),
        ("Je prends mon petit-dejeuner a huit heures.", "I have breakfast at eight o'clock."),
        ("Je vais a l'ecole.", "I go to school."),
        ("Je fais mes devoirs.", "I do my homework."),
    ]
    for i in range(1, 101):
        french, english = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "French - Daily Routine",
                difficulty,
                f"Routine {i}: Translate into English: '{french}'",
                f"{english}. Award 1 mark for each correctly translated idea.",
                2,
            )
        )
    return rows


def build_translation_sentences():
    rows = []
    prompts = [
        ("I live in a small town.", "J'habite dans une petite ville."),
        ("My school is quite big.", "Mon ecole est assez grande."),
        ("I play tennis at the weekend.", "Je joue au tennis le week-end."),
        ("Because it is fun, I like French.", "Parce que c'est amusant, j'aime le francais."),
    ]
    for i in range(1, 101):
        english, french = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 30 else 3 if i <= 65 else 5
        rows.append(
            row(
                "French - Translation Sentences",
                difficulty,
                f"Translation {i}: Translate into French: '{english}'",
                f"{french}. Award 1 mark for each correctly conveyed idea and accurate key vocabulary.",
                3,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_core_vocabulary())
    rows.extend(build_numbers_and_time())
    rows.extend(build_family_and_descriptions())
    rows.extend(build_school_topic())
    rows.extend(build_grammar_verbs())
    rows.extend(build_negatives_and_opinions())
    rows.extend(build_free_time())
    rows.extend(build_food_and_drink())
    rows.extend(build_daily_routine())
    rows.extend(build_translation_sentences())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 French questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
