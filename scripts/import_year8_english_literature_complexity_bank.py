from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-english-literature-complexity-pack"
SUBJECT = "English Literature"
TOPIC = "Year 8 Literature Skills"


def row(difficulty, question, answer, marks):
    return {
        "subject": SUBJECT,
        "topic": TOPIC,
        "difficulty_level": difficulty,
        "question": question,
        "answer": answer,
        "marks": marks,
        "source": SOURCE,
    }


def build_level_1():
    rows = []
    devices = [
        ("metaphor", "a comparison saying one thing is another"),
        ("simile", "a comparison using 'like' or 'as'"),
        ("personification", "giving human qualities to non-human things"),
        ("alliteration", "repetition of the same starting sound"),
        ("rhetorical question", "a question asked for effect, not a real answer"),
    ]
    for i in range(1, 101):
        term, meaning = devices[(i - 1) % len(devices)]
        rows.append(
            row(
                1,
                f"Complexity 1 Question {i}: Define the term '{term}'.",
                f"{meaning}. Award 1 mark for a clear correct definition.",
                1,
            )
        )
    return rows


def build_level_2():
    rows = []
    extracts = [
        ("'The wind screamed through the trees.'", "personification", "the wind is described like a human"),
        ("'Her smile was like sunshine.'", "simile", "it compares a smile to sunshine using 'like'"),
        ("'The classroom was a zoo.'", "metaphor", "it says one thing is another"),
        ("'Dark, dangerous, dreadful night.'", "alliteration", "repetition of the 'd' sound"),
    ]
    for i in range(1, 101):
        quote, device, why = extracts[(i - 1) % len(extracts)]
        rows.append(
            row(
                2,
                f"Complexity 2 Question {i}: Identify the language device in {quote}.",
                f"{device}. Award 1 mark for naming the device and 1 mark for explaining that {why}.",
                2,
            )
        )
    return rows


def build_level_3():
    rows = []
    prompts = [
        ("'The door groaned open in the silence.'", "tension", "the verb 'groaned' suggests something eerie or unsettling"),
        ("'His heart was a drum inside his chest.'", "fear or excitement", "the metaphor suggests intense emotion and physical panic"),
        ("'The rain wrapped the town in grey.'", "sadness or gloom", "the verb 'wrapped' suggests the whole place is covered by a dull mood"),
        ("'She stood alone beneath the broken clock.'", "loneliness", "the image of isolation and the broken clock may suggest hopelessness"),
    ]
    for i in range(1, 101):
        quote, effect, evidence = prompts[(i - 1) % len(prompts)]
        rows.append(
            row(
                3,
                f"Complexity 3 Question {i}: Explain one effect of the writer's language in {quote}.",
                f"Accept any relevant explanation. Strong answer: it creates {effect} because {evidence}. Award 1 mark for a valid effect and 1 mark for relevant reference to the quotation.",
                2,
            )
        )
    return rows


def build_level_4():
    rows = []
    prompts = [
        (
            "'The hero stepped forward while the others shrank back into the dark.'",
            "the hero is presented as brave and different from the others",
            "contrast between 'stepped forward' and 'shrank back'",
        ),
        (
            "'She smiled politely, but her hands trembled beneath the table.'",
            "the character appears calm on the outside but anxious underneath",
            "contrast between smiling and trembling",
        ),
        (
            "'The house looked grand from afar, yet inside it was cold and empty.'",
            "appearance is misleading",
            "contrast between grand outside and empty inside",
        ),
        (
            "'He laughed with the crowd although his eyes stayed fixed on the floor.'",
            "the character may be hiding discomfort or sadness",
            "contrast between laughter and lowered eyes",
        ),
    ]
    for i in range(1, 101):
        quote, point, analysis = prompts[(i - 1) % len(prompts)]
        rows.append(
            row(
                4,
                f"Complexity 4 Question {i}: Explain how the writer presents character in {quote}.",
                f"Accept any relevant analytical response. Strong answer: {point}, shown through the {analysis}. Award 1 mark for a clear point, 1 mark for quotation reference, and 1 mark for analysis.",
                3,
            )
        )
    return rows


def build_level_5():
    rows = []
    prompts = [
        (
            "'The candle burned lower as her hope began to fade.'",
            "fragility of hope",
            "the candle acts as a symbol of hope fading away",
        ),
        (
            "'Behind the locked gate stood the garden he had not seen since childhood.'",
            "memory and loss",
            "the locked gate may symbolise distance from the past",
        ),
        (
            "'Every cheerful song in the hall seemed to sharpen her loneliness.'",
            "isolation",
            "the contrast between public joy and private sadness deepens the theme",
        ),
        (
            "'He tore the letter in half, yet kept both pieces in his pocket.'",
            "conflict",
            "his actions suggest he wants to reject the message but cannot let it go",
        ),
    ]
    for i in range(1, 101):
        quote, theme, analysis = prompts[(i - 1) % len(prompts)]
        rows.append(
            row(
                5,
                f"Complexity 5 Question {i}: Explore how the writer develops the theme of {theme} in {quote}.",
                f"Accept thoughtful, well-supported analysis. Strong answer: {analysis}. Award 1 mark for identifying a theme or idea, 1 mark for reference to the quotation, 1 mark for developed analysis, and 1 mark for an insightful interpretation.",
                4,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_level_1())
    rows.extend(build_level_2())
    rows.extend(build_level_3())
    rows.extend(build_level_4())
    rows.extend(build_level_5())
    assert len(rows) == 500, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 English Literature questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
