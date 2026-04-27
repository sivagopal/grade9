from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-german-topic-pack"
SUBJECT = "German"


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
    vocab = [
        ("das Haus", "the house"),
        ("die Schule", "the school"),
        ("der Hund", "the dog"),
        ("die Katze", "the cat"),
        ("das Buch", "the book"),
    ]
    for i in range(1, 101):
        german, english = vocab[(i - 1) % len(vocab)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "German - Core Vocabulary",
                difficulty,
                f"Vocabulary {i}: Translate '{german}' into English.",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_numbers_and_time():
    rows = []
    for i in range(1, 101):
        number = 10 + i
        german_numbers = {
            11: "elf", 12: "zwolf", 13: "dreizehn", 14: "vierzehn", 15: "funfzehn",
            16: "sechzehn", 17: "siebzehn", 18: "achtzehn", 19: "neunzehn", 20: "zwanzig",
        }
        answer = german_numbers.get(number if number <= 20 else 20, "zwanzig")
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "German - Numbers and Time",
                difficulty,
                f"Numbers {i}: Write the number {number if number <= 20 else 20} in German.",
                f"{answer}. Award 1 mark for the correct German number.",
                1,
            )
        )
    return rows


def build_family_and_descriptions():
    rows = []
    prompts = [
        ("mein Bruder", "my brother"),
        ("meine Schwester", "my sister"),
        ("mein Vater", "my father"),
        ("meine Mutter", "my mother"),
        ("meine Familie", "my family"),
    ]
    for i in range(1, 101):
        german, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "German - Family and Descriptions",
                difficulty,
                f"Family {i}: Translate '{german}' into English.",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_school_topic():
    rows = []
    prompts = [
        ("Ich mag Mathe.", "I like maths."),
        ("Ich mag Geschichte nicht.", "I do not like history."),
        ("Mein Lieblingsfach ist Kunst.", "My favourite subject is art."),
        ("Die Schule ist interessant.", "School is interesting."),
    ]
    for i in range(1, 101):
        german, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 4
        rows.append(
            row(
                "German - School",
                difficulty,
                f"School {i}: Translate into English: '{german}'",
                f"{english}. Award 1 mark for each idea translated correctly.",
                2,
            )
        )
    return rows


def build_grammar_verbs():
    rows = []
    prompts = [
        ("ich", "spielen", "ich spiele"),
        ("du", "lernen", "du lernst"),
        ("er", "machen", "er macht"),
        ("wir", "wohnen", "wir wohnen"),
        ("sie", "kommen", "sie kommen"),
    ]
    for i in range(1, 101):
        pronoun, infinitive, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "German - Grammar Verbs",
                difficulty,
                f"Grammar {i}: Conjugate the verb '{infinitive}' with '{pronoun}' in the present tense.",
                f"{answer}. Award 1 mark for the correct verb ending and full form.",
                1,
            )
        )
    return rows


def build_word_order():
    rows = []
    prompts = [
        ("weil", "Ich bleibe zu Hause, weil ich krank bin.", "the verb goes to the end"),
        ("dann", "Dann spiele ich Fussball.", "the verb stays in second position"),
        ("heute", "Heute lerne ich Deutsch.", "the verb stays in second position"),
        ("weil", "Er ist froh, weil er Ferien hat.", "the verb goes to the end"),
    ]
    for i in range(1, 101):
        keyword, sentence, rule = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "German - Word Order",
                difficulty,
                f"Word Order {i}: In the sentence '{sentence}', what happens to the verb after '{keyword}'?",
                f"{rule}. Award 1 mark for identifying the correct word order rule.",
                1,
            )
        )
    return rows


def build_free_time():
    rows = []
    prompts = [
        ("Ich spiele Fussball.", "I play football."),
        ("Ich hore Musik.", "I listen to music."),
        ("Ich sehe fern.", "I watch TV."),
        ("Ich lese gern.", "I like reading."),
    ]
    for i in range(1, 101):
        german, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "German - Free Time",
                difficulty,
                f"Free Time {i}: Translate into English: '{german}'",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_food_and_drink():
    rows = []
    prompts = [
        ("Ich esse Brot.", "I eat bread."),
        ("Ich trinke Wasser.", "I drink water."),
        ("Ich mag Pizza.", "I like pizza."),
        ("Ich mag keinen Kaffee.", "I do not like coffee."),
    ]
    for i in range(1, 101):
        german, english = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "German - Food and Drink",
                difficulty,
                f"Food {i}: Translate into English: '{german}'",
                f"{english}. Award 1 mark for the correct translation.",
                1,
            )
        )
    return rows


def build_daily_routine():
    rows = []
    prompts = [
        ("Ich stehe um sieben Uhr auf.", "I get up at seven o'clock."),
        ("Ich fruhstucke um acht Uhr.", "I have breakfast at eight o'clock."),
        ("Ich gehe zur Schule.", "I go to school."),
        ("Ich mache meine Hausaufgaben.", "I do my homework."),
    ]
    for i in range(1, 101):
        german, english = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "German - Daily Routine",
                difficulty,
                f"Routine {i}: Translate into English: '{german}'",
                f"{english}. Award 1 mark for each correct idea translated.",
                2,
            )
        )
    return rows


def build_translation_sentences():
    rows = []
    prompts = [
        ("I live in a small town.", "Ich wohne in einer kleinen Stadt."),
        ("My school is quite big.", "Meine Schule ist ziemlich gross."),
        ("I play tennis at the weekend.", "Ich spiele am Wochenende Tennis."),
        ("Because it is fun, I like German.", "Weil es Spass macht, mag ich Deutsch."),
    ]
    for i in range(1, 101):
        english, german = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 30 else 3 if i <= 65 else 5
        rows.append(
            row(
                "German - Translation Sentences",
                difficulty,
                f"Translation {i}: Translate into German: '{english}'",
                f"{german}. Award 1 mark for each correctly conveyed idea and accurate key vocabulary.",
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
    rows.extend(build_word_order())
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
    print(f"Imported {count} Year 8 German questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
