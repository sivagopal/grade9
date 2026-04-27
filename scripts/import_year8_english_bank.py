from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage import PlannerDB


SOURCE = "year8-english-topic-pack"
SUBJECT = "English"


def with_note(answer, note):
    cleaned = answer.strip()
    if cleaned.endswith((".", "!", "?")):
        return f"{cleaned} {note}"
    return f"{cleaned}. {note}"


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


def build_punctuation():
    rows = []
    prompts = [
        ("Add a full stop to end this sentence correctly: I went to the park", "I went to the park."),
        ("Rewrite with a comma after the fronted adverbial: In the morning we read quietly", "In the morning, we read quietly."),
        ("Add an apostrophe for possession: the coat of Sarah", "Sarah's coat"),
        ("Rewrite with a question mark: Where are you going", "Where are you going?"),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "English - Punctuation",
                difficulty,
                f"Punctuation {i}: {prompt}",
                with_note(answer, "Award 1 mark for correct punctuation and accurate rewritten sentence."),
                1,
            )
        )
    return rows


def build_grammar():
    rows = []
    prompts = [
        ("Identify the verb in: The tired athlete stumbled home.", "stumbled"),
        ("Identify the adjective in: The bright lantern glowed.", "bright"),
        ("Identify the adverb in: She answered calmly.", "calmly"),
        ("Identify the noun in: Freedom matters deeply.", "Freedom"),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "English - Grammar",
                difficulty,
                f"Grammar {i}: {prompt}",
                with_note(answer, "Award 1 mark for the correct word class identification."),
                1,
            )
        )
    return rows


def build_sentence_types():
    rows = []
    prompts = [
        ("Write a simple sentence about school.", "Accept any grammatically correct simple sentence with one main clause."),
        ("Write a compound sentence using 'but'.", "Accept any correct sentence joining two main clauses with 'but'."),
        ("Write a complex sentence starting with 'Although'.", "Accept any correct sentence with a subordinate clause starting with 'Although'."),
        ("Turn this into an exclamation: What a surprising result", "What a surprising result!"),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 30 else 2 if i <= 65 else 4
        rows.append(
            row(
                "English - Sentence Types",
                difficulty,
                f"Sentence Types {i}: {prompt}",
                f"{answer} Award 1 mark for a structurally correct sentence and 1 mark for suitable punctuation where relevant.",
                2,
            )
        )
    return rows


def build_vocabulary():
    rows = []
    prompts = [
        ("Give a synonym for 'happy'.", "Accept: joyful, cheerful, delighted, pleased."),
        ("Give a synonym for 'said'.", "Accept: replied, whispered, shouted, announced."),
        ("Give an antonym for 'ancient'.", "Accept: modern, new, recent."),
        ("Replace 'nice' with a more precise adjective in this phrase: a nice day", "Accept a precise adjective such as pleasant, warm, bright, peaceful."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "English - Vocabulary",
                difficulty,
                f"Vocabulary {i}: {prompt}",
                f"{answer} Award 1 mark for any suitable answer.",
                1,
            )
        )
    return rows


def build_language_devices():
    rows = []
    prompts = [
        ("Identify the device in: The city never sleeps.", "personification"),
        ("Identify the device in: He ran like the wind.", "simile"),
        ("Identify the device in: The classroom was a jungle.", "metaphor"),
        ("Identify the device in: Silent snakes slid slowly.", "alliteration"),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 30 else 2 if i <= 65 else 4
        rows.append(
            row(
                "English - Language Devices",
                difficulty,
                f"Language Devices {i}: {prompt}",
                with_note(answer, "Award 1 mark for correct identification and allow equivalent terminology where appropriate."),
                1,
            )
        )
    return rows


def build_reading_comprehension():
    rows = []
    prompts = [
        ("From the sentence 'Tom slammed the door and refused to speak,' what can you infer about Tom's mood?", "He is likely angry, upset, or frustrated."),
        ("From the sentence 'The garden shimmered after the rain,' what is the setting like?", "It seems fresh, bright, or beautiful after rainfall."),
        ("From the sentence 'Mina checked her watch three times before the exam began,' what can you infer?", "She is nervous, anxious, or eager."),
        ("From the sentence 'The empty street echoed beneath his footsteps,' what atmosphere is created?", "A lonely, eerie, or quiet atmosphere."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "English - Reading Comprehension",
                difficulty,
                f"Reading {i}: {prompt}",
                f"{answer} Award 1 mark for a relevant inference and 1 mark for support from the wording where appropriate.",
                2,
            )
        )
    return rows


def build_creative_writing():
    rows = []
    prompts = [
        ("Write two vivid sentences describing a storm.", "Accept any two well-formed descriptive sentences using specific detail."),
        ("Write one sentence that creates suspense.", "Accept any grammatically correct sentence that builds tension or anticipation."),
        ("Write one sentence describing a character entering a dark room.", "Accept any suitable descriptive sentence with clear imagery."),
        ("Write one sentence that uses personification to describe rain.", "Accept any correct sentence giving rain human qualities."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 30 else 3 if i <= 65 else 5
        rows.append(
            row(
                "English - Creative Writing",
                difficulty,
                f"Creative Writing {i}: {prompt}",
                f"{answer} Award 1 mark for meeting the task, 1 mark for clear sentence control, and 1 mark for effective detail where relevant.",
                3,
            )
        )
    return rows


def build_transactional_writing():
    rows = []
    prompts = [
        ("Write one formal sentence asking for more library books in school.", "Accept any formal sentence using polite, appropriate register."),
        ("Write one persuasive sentence encouraging students to recycle.", "Accept any persuasive sentence using clear argument or persuasive language."),
        ("Write one complaint sentence about a broken classroom window.", "Accept any clear complaint sentence in an appropriate tone."),
        ("Write one sentence for the opening of a speech about homework.", "Accept any suitable opening sentence addressing an audience."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 35 else 3 if i <= 70 else 4
        rows.append(
            row(
                "English - Transactional Writing",
                difficulty,
                f"Transactional Writing {i}: {prompt}",
                f"{answer} Award 1 mark for purpose and audience, and 1 mark for appropriate style.",
                2,
            )
        )
    return rows


def build_spag_editing():
    rows = []
    prompts = [
        ("Correct this sentence: we was going to the shops", "We were going to the shops."),
        ("Correct this sentence: She dont like apples", "She doesn't like apples."),
        ("Correct this sentence: yesterday i visited london", "Yesterday I visited London."),
        ("Correct this sentence: Their going too school", "They're going to school."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 1 if i <= 35 else 2 if i <= 70 else 3
        rows.append(
            row(
                "English - SPaG Editing",
                difficulty,
                f"SPaG {i}: {prompt}",
                f"{answer} Award 1 mark for fully corrected spelling, punctuation, and grammar.",
                1,
            )
        )
    return rows


def build_analysis_and_effect():
    rows = []
    prompts = [
        ("Explain the effect of 'The shadows crawled across the wall.'", "It creates a creepy or threatening atmosphere because shadows are described as moving like living things."),
        ("Explain the effect of 'Her voice was ice.'", "It suggests she sounded cold, harsh, or emotionless through metaphor."),
        ("Explain the effect of 'The playground exploded with noise.'", "It suggests sudden, overwhelming sound and energy."),
        ("Explain the effect of 'He clung to hope like a rope.'", "It shows hope is keeping him going and preventing him from giving up."),
    ]
    for i in range(1, 101):
        prompt, answer = prompts[(i - 1) % len(prompts)]
        difficulty = 2 if i <= 30 else 3 if i <= 65 else 5
        rows.append(
            row(
                "English - Analysis and Effect",
                difficulty,
                f"Analysis {i}: {prompt}",
                f"{answer} Award 1 mark for identifying a clear effect, 1 mark for reference to the words, and 1 mark for developed explanation.",
                3,
            )
        )
    return rows


def build_questions():
    rows = []
    rows.extend(build_punctuation())
    rows.extend(build_grammar())
    rows.extend(build_sentence_types())
    rows.extend(build_vocabulary())
    rows.extend(build_language_devices())
    rows.extend(build_reading_comprehension())
    rows.extend(build_creative_writing())
    rows.extend(build_transactional_writing())
    rows.extend(build_spag_editing())
    rows.extend(build_analysis_and_effect())
    assert len(rows) == 1000, len(rows)
    return rows


def main():
    db = PlannerDB()
    rows = build_questions()
    count = db.bulk_upsert_questions(rows)
    print(f"Imported {count} Year 8 English questions into the SQLite question bank.")


if __name__ == "__main__":
    main()
