import argparse
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "grade9_planner.db"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.question_bank import question_pattern_key


TRIVIAL_START_PATTERNS = [
    r"^define\b",
    r"^what is\b",
    r"^name (one|two)\b",
    r"^give one\b",
    r"^state one\b",
    r"^identify the verb\b",
    r"^what does .* stand for\b",
    r"^give the meaning of\b",
    r"^what is the (french|german|latin) for\b",
]

LOW_SIGNAL_FRAGMENT_PATTERNS = [
    r"\bvocabulary \d+\b",
    r"\bpunctuation \d+\b",
    r"\bforces \d+\b",
    r"\bcomplexity 1 question\b",
    r"\btranslate '\w+'\b",
    r"\btranslate \"\w+\"\b",
    r"\bg = 10 n/kg\b",
    r"\bput these steps\b",
]

REASONING_PATTERNS = [
    r"\bexplain\b",
    r"\bwhy\b",
    r"\bjustify\b",
    r"\bcompare\b",
    r"\bevaluate\b",
    r"\bhow far\b",
    r"\bshow your working\b",
    r"\bprove\b",
    r"\binterpret\b",
    r"\banalyse\b",
]

CHALLENGE_PATTERNS = [
    r"\bsimultaneous\b",
    r"\bquadratic\b",
    r"\bfactorise fully\b",
    r"\bwithout replacement\b",
    r"\bprime number or\b",
    r"\bline of best fit\b",
    r"\bmidpoint\b",
    r"\bgradient\b",
    r"\btransform\b",
    r"\brotated?\b",
    r"\breflection\b",
    r"\btrigonometry\b",
    r"\bpythagoras\b",
    r"\bhistogram\b",
    r"\bcumulative frequency\b",
    r"\bohm'?s law\b",
    r"\bpower\b",
    r"\benergy\b",
    r"\bmatrix\b",
    r"\bbinomial\b",
    r"\bword equation\b",
]

SUBJECT_TOPIC_REJECTS = {
    "Maths": {
        "Number Skills",
        "Negative Numbers",
        "Place Value and Ordering",
        "Factors Multiples and Primes",
        "Fractions",
        "Decimals",
    },
    "French": {
        "French - Core Vocabulary",
    },
    "German": {
        "German - Core Vocabulary",
    },
    "English": {
        "English - Punctuation",
    },
}


def normalized_text(value):
    return " ".join(str(value or "").strip().lower().split())


def matches_any(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9']+", text))


def is_single_word_translation(text):
    lowered = normalized_text(text)
    if not lowered.startswith("translate"):
        return False
    body = lowered.split(":", 1)[1].strip() if ":" in lowered else lowered.replace("translate", "", 1).strip()
    tokens = re.findall(r"[A-Za-zÀ-ÿ']+", body)
    return len(tokens) <= 3


def is_rubbish(row):
    subject = str(row["subject"] or "").strip()
    topic = str(row["topic"] or "").strip()
    text = normalized_text(row["question_text"])
    marks = int(row["marks"] or 0)
    source = str(row["source"] or "").strip().lower()

    if topic in SUBJECT_TOPIC_REJECTS.get(subject, set()):
        return True
    if matches_any(text, TRIVIAL_START_PATTERNS):
        return True
    if matches_any(text, LOW_SIGNAL_FRAGMENT_PATTERNS):
        return True
    if is_single_word_translation(text):
        return True
    if source.endswith("-topic-pack") and matches_any(text, [r"\bvocabulary\b", r"\bpunctuation\b"]):
        return True
    if marks <= 2 and word_count(text) <= 8 and not matches_any(text, REASONING_PATTERNS):
        return True
    if subject in {"Latin", "French", "German"} and marks <= 2 and not matches_any(text, REASONING_PATTERNS):
        return True
    if subject in {"Biology", "Science", "Geography", "Technology", "Computing / 12th Subject"} and matches_any(
        text,
        [
            r"^state the\b",
            r"^state one\b",
            r"^name the\b",
            r"^give one example\b",
            r"^what case is\b",
            r"^what is a\b",
        ],
    ):
        return True
    if subject == "Maths" and matches_any(
        text,
        [
            r"^solve x \+ \d+ = \d+",
            r"^find 15% of",
            r"\braises gbp\b",
            r"\btemperature is -?\d+",
        ],
    ):
        return True
    if subject == "Physics" and marks <= 2 and not matches_any(text, REASONING_PATTERNS):
        return True
    if subject == "English Literature" and matches_any(text, [r"^what is a metaphor", r"^define the term"]):
        return True
    if subject == "English" and matches_any(text, [r"full stop", r"question mark", r"apostrophe for possession"]):
        return True
    return False


def assess_difficulty(row):
    text = normalized_text(row["question_text"])
    marks = int(row["marks"] or 0)
    score = 2

    if marks >= 3:
        score += 1
    if marks >= 5:
        score += 1
    if matches_any(text, REASONING_PATTERNS):
        score += 1
    if matches_any(text, CHALLENGE_PATTERNS):
        score += 1
    if word_count(text) >= 20:
        score += 1
    if matches_any(text, TRIVIAL_START_PATTERNS):
        score -= 1
    if is_single_word_translation(text):
        score -= 2
    return max(2, min(5, score))


def clone_keep_limit(row, difficulty):
    subject = str(row["subject"] or "").strip()
    if subject in {"French", "German", "Latin", "English", "English Literature"}:
        return 1
    return 1 if difficulty <= 3 else 2


def curate_rows(rows):
    deleted = []
    kept = []

    for row in rows:
        if is_rubbish(row):
            deleted.append((row, "rubbish"))
            continue
        updated = dict(row)
        updated["new_difficulty"] = assess_difficulty(row)
        if updated["new_difficulty"] <= 2:
            deleted.append((row, "too_easy"))
            continue
        kept.append(updated)

    kept.sort(
        key=lambda row: (
            row["subject"],
            row["topic"],
            question_pattern_key(row["question_text"]),
            -row["new_difficulty"],
            -int(row["marks"] or 0),
            row["id"],
        )
    )

    pattern_counts = Counter()
    final_rows = []
    for row in kept:
        pattern = (row["subject"], row["topic"], question_pattern_key(row["question_text"]))
        limit = clone_keep_limit(row, row["new_difficulty"])
        if pattern_counts[pattern] >= limit:
            deleted.append((row, "clone"))
            continue
        pattern_counts[pattern] += 1
        final_rows.append(row)

    return final_rows, deleted


def backup_database(db_path):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.stem}.backup_{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def summarize(final_rows, deleted):
    kept_by_subject = Counter(row["subject"] for row in final_rows)
    deleted_by_subject = Counter(row["subject"] for row, _ in deleted)
    deleted_by_reason = Counter(reason for _, reason in deleted)
    difficulty_counts = Counter(row["new_difficulty"] for row in final_rows)
    return kept_by_subject, deleted_by_subject, deleted_by_reason, difficulty_counts


def apply_changes(conn, final_rows, deleted):
    deleted_ids = [row["id"] for row, _ in deleted]
    if deleted_ids:
        placeholders = ",".join("?" for _ in deleted_ids)
        conn.execute(f"DELETE FROM questions WHERE id IN ({placeholders})", deleted_ids)

    conn.executemany(
        """
        UPDATE questions
        SET difficulty_level = ?
        WHERE id = ?
        """,
        [(row["new_difficulty"], row["id"]) for row in final_rows],
    )
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute(
        """
        SELECT id, subject, topic, COALESCE(subtopic, '') AS subtopic, question_text, answer_text, marks, difficulty_level, source
        FROM questions
        ORDER BY id ASC
        """
    ).fetchall()]

    final_rows, deleted = curate_rows(rows)
    kept_by_subject, deleted_by_subject, deleted_by_reason, difficulty_counts = summarize(final_rows, deleted)

    print(f"Original questions: {len(rows)}")
    print(f"Kept questions: {len(final_rows)}")
    print(f"Deleted questions: {len(deleted)}")
    print("\nDeleted by reason:")
    for reason, count in sorted(deleted_by_reason.items()):
        print(f"  {reason}: {count}")

    print("\nKept by subject:")
    for subject, count in kept_by_subject.most_common():
        print(f"  {subject}: {count}")

    print("\nDeleted by subject:")
    for subject, count in deleted_by_subject.most_common():
        print(f"  {subject}: {count}")

    print("\nDifficulty distribution after curation:")
    for level in sorted(difficulty_counts):
        print(f"  {level}: {difficulty_counts[level]}")

    sample_deletes = defaultdict(list)
    for row, reason in deleted:
        if len(sample_deletes[reason]) < 5:
            sample_deletes[reason].append(f"{row['subject']} | {row['topic']} | {row['question_text']}")

    print("\nSample deletions:")
    for reason, samples in sorted(sample_deletes.items()):
        print(f"  {reason}:")
        for sample in samples:
            print(f"    - {sample}")

    if not args.apply:
        return

    backup_path = backup_database(DB_PATH)
    apply_changes(conn, final_rows, deleted)
    print(f"\nBackup created: {backup_path}")
    print("Database updated.")


if __name__ == "__main__":
    main()
