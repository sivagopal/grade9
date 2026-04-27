import json
import re
import random
from collections import defaultdict
from datetime import date

DEFAULT_DIFFICULTY = 1
MAX_DIFFICULTY = 5

SEED_QUESTIONS = [
    {"subject": "Biology", "topic": "Cell Biology", "difficulty_level": 1, "question": "Explain the function of mitochondria in cells.", "answer": "They release energy by aerobic respiration.", "marks": 2},
    {"subject": "Biology", "topic": "Cell Biology", "difficulty_level": 2, "question": "Name two adaptations of red blood cells.", "answer": "Biconcave shape, no nucleus, haemoglobin, flexible membrane.", "marks": 2},
    {"subject": "Biology", "topic": "Transport in Cells", "difficulty_level": 1, "question": "What is diffusion?", "answer": "Net movement of particles from high to low concentration.", "marks": 2},
    {"subject": "Biology", "topic": "Transport in Cells", "difficulty_level": 3, "question": "Explain why a large surface area speeds up diffusion in the lungs.", "answer": "It provides more space for gas exchange so more particles can diffuse each second.", "marks": 3},
    {"subject": "Maths", "topic": "Algebra", "difficulty_level": 1, "question": "Solve: 3x + 7 = 28.", "answer": "x = 7", "marks": 2},
    {"subject": "Maths", "topic": "Percentages", "difficulty_level": 1, "question": "Find 15% of £80.", "answer": "£12", "marks": 2},
    {"subject": "Maths", "topic": "Algebra", "difficulty_level": 2, "question": "Expand and simplify: 2(x + 5) + 3x.", "answer": "5x + 10", "marks": 2},
    {"subject": "Maths", "topic": "Algebra", "difficulty_level": 3, "question": "Factorise fully: x^2 + 7x + 12.", "answer": "(x + 3)(x + 4)", "marks": 2},
    {"subject": "Maths", "topic": "Ratio", "difficulty_level": 2, "question": "Share £84 in the ratio 3:4.", "answer": "£36 and £48", "marks": 3},
    {"subject": "Maths", "topic": "Geometry", "difficulty_level": 4, "question": "The angles in a triangle are x, 2x and 3x. Find x.", "answer": "30", "marks": 3},
    {"subject": "Science", "topic": "Atomic Structure", "difficulty_level": 1, "question": "State the difference between an element and a compound.", "answer": "An element has one type of atom; a compound has two or more elements chemically joined.", "marks": 2},
    {"subject": "Science", "topic": "Particle Model", "difficulty_level": 1, "question": "What happens to particles when a liquid is heated?", "answer": "They gain energy and move faster.", "marks": 2},
    {"subject": "Science", "topic": "Energy", "difficulty_level": 1, "question": "Define renewable energy source.", "answer": "An energy source that is naturally replenished.", "marks": 2},
    {"subject": "Science", "topic": "Particle Model", "difficulty_level": 3, "question": "Explain why diffusion happens faster in gases than in liquids.", "answer": "Gas particles move faster and are further apart, so they spread out more quickly.", "marks": 3},
    {"subject": "Science", "topic": "Energy", "difficulty_level": 4, "question": "Evaluate one advantage and one disadvantage of wind power.", "answer": "Advantage: renewable and low running emissions. Disadvantage: intermittent and can affect landscapes or wildlife.", "marks": 4},
    {"subject": "Further Maths", "topic": "Algebra", "difficulty_level": 2, "question": "Factorise: x^2 + 5x + 6.", "answer": "(x + 2)(x + 3)", "marks": 2},
    {"subject": "Further Maths", "topic": "Sequences", "difficulty_level": 2, "question": "Find the nth term of 4, 7, 10, 13...", "answer": "3n + 1", "marks": 2},
    {"subject": "Further Maths", "topic": "Indices", "difficulty_level": 1, "question": "Simplify: (x^3)(x^4).", "answer": "x^7", "marks": 1},
    {"subject": "English", "topic": "Punctuation", "difficulty_level": 1, "question": "Write one sentence using a semicolon correctly.", "answer": "Award marks for two closely linked independent clauses joined by a semicolon.", "marks": 2},
    {"subject": "English", "topic": "Grammar", "difficulty_level": 1, "question": "Identify the verb in: 'The tired runner collapsed near the finish line.'", "answer": "collapsed", "marks": 1},
    {"subject": "English", "topic": "Language Analysis", "difficulty_level": 2, "question": "What is the effect of using rhetorical questions?", "answer": "They engage the reader and encourage them to think.", "marks": 2},
    {"subject": "English Literature", "topic": "Methods", "difficulty_level": 1, "question": "What is a metaphor?", "answer": "A comparison saying one thing is another.", "marks": 1},
    {"subject": "English Literature", "topic": "Methods", "difficulty_level": 2, "question": "Explain one effect of pathetic fallacy.", "answer": "It uses weather or nature to reflect mood or atmosphere.", "marks": 2},
    {"subject": "English Literature", "topic": "Essay Writing", "difficulty_level": 2, "question": "What should a strong literature paragraph include?", "answer": "Point, evidence, analysis, and context where relevant.", "marks": 2},
    {"subject": "Latin", "topic": "Translation", "difficulty_level": 1, "question": "Translate: puella aquam portat.", "answer": "The girl carries water.", "marks": 2},
    {"subject": "Latin", "topic": "Grammar", "difficulty_level": 1, "question": "What case is usually used for the subject of a Latin sentence?", "answer": "Nominative", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'servus'.", "answer": "slave or servant", "marks": 1},
    {"subject": "German", "topic": "Translation", "difficulty_level": 1, "question": "Translate: Ich habe einen Hund.", "answer": "I have a dog.", "marks": 2},
    {"subject": "German", "topic": "Grammar", "difficulty_level": 2, "question": "What does 'weil' do to word order in German?", "answer": "It sends the verb to the end of the clause.", "marks": 2},
    {"subject": "German", "topic": "Vocabulary", "difficulty_level": 1, "question": "Translate: meine Schule.", "answer": "my school", "marks": 1},
    {"subject": "French", "topic": "Translation", "difficulty_level": 1, "question": "Translate: Je vais au college.", "answer": "I go or am going to school.", "marks": 2},
    {"subject": "French", "topic": "Vocabulary", "difficulty_level": 1, "question": "What is the French for 'because'?", "answer": "parce que or car", "marks": 1},
    {"subject": "French", "topic": "Translation", "difficulty_level": 1, "question": "Translate: j'aime les maths.", "answer": "I like maths.", "marks": 1},
    {"subject": "Geography", "topic": "Physical Processes", "difficulty_level": 1, "question": "Define erosion.", "answer": "The wearing away and removal of material by water, wind, ice, or waves.", "marks": 2},
    {"subject": "Geography", "topic": "Weather", "difficulty_level": 1, "question": "Name one type of rainfall.", "answer": "Relief, frontal, or convectional rainfall.", "marks": 1},
    {"subject": "Geography", "topic": "Urbanisation", "difficulty_level": 2, "question": "What is urbanisation?", "answer": "An increase in the proportion of people living in urban areas.", "marks": 2},
    {"subject": "Business Studies", "topic": "Finance", "difficulty_level": 1, "question": "Define revenue.", "answer": "Money received from selling goods or services.", "marks": 1},
    {"subject": "Business Studies", "topic": "Finance", "difficulty_level": 1, "question": "What is profit?", "answer": "Revenue minus costs.", "marks": 1},
    {"subject": "Business Studies", "topic": "Market Research", "difficulty_level": 2, "question": "Give one advantage of market research.", "answer": "It helps understand customer needs, reduces risk, or informs decisions.", "marks": 2},
    {"subject": "Computing / 12th Subject", "topic": "Algorithms", "difficulty_level": 1, "question": "What is an algorithm?", "answer": "A step-by-step set of instructions to solve a problem.", "marks": 2},
    {"subject": "Computing / 12th Subject", "topic": "Hardware", "difficulty_level": 1, "question": "Give one example of an input device.", "answer": "Keyboard, mouse, microphone, scanner, or camera.", "marks": 1},
    {"subject": "Computing / 12th Subject", "topic": "Hardware", "difficulty_level": 1, "question": "What does CPU stand for?", "answer": "Central Processing Unit.", "marks": 1},
]

TOPIC_KEYWORDS = {
    "Maths": {
        "Algebra": ["solve", "factorise", "expand", "simplify", "equation", "nth term", "term", "expression"],
        "Geometry": ["angle", "triangle", "circle", "parallel", "perimeter", "area"],
        "Ratio": ["ratio", "share", "proportion"],
        "Percentages": ["percent", "%", "percentage"],
    },
    "Science": {
        "Particle Model": ["particle", "liquid", "gas", "diffusion", "state"],
        "Energy": ["energy", "renewable", "power", "electricity"],
        "Atomic Structure": ["element", "compound", "atom", "molecule"],
    },
    "Biology": {
        "Cell Biology": ["cell", "mitochondria", "nucleus", "red blood", "membrane"],
        "Transport in Cells": ["diffusion", "osmosis", "surface area", "lungs"],
    },
}


def get_seed_questions():
    questions = [dict(row) for row in SEED_QUESTIONS]
    try:
        from app.math_plot_bank import build_plot_question_bank

        questions.extend(build_plot_question_bank())
    except Exception:
        pass
    return questions


def format_test_markdown(questions, title_subject=None):
    today = date.today().isoformat()
    total_marks = sum(q["marks"] for q in questions)
    heading = f"# GCSE Grade 9 {title_subject} Test — {today}" if title_subject else f"# GCSE Grade 9 Mini Test — {today}"
    lines = [
        heading,
        "",
        "Time allowed: 10 minutes",
        f"Total marks: {total_marks}",
        "",
        "## Questions",
        "",
    ]
    for i, q in enumerate(questions, 1):
        topic = q.get("topic", "General")
        difficulty = q.get("difficulty_level", DEFAULT_DIFFICULTY)
        lines.append(
            f"{i}. **{q['subject']}** | Topic: {topic} | Difficulty: {difficulty} | ({q['marks']} marks): {q['question']}"
        )
        if q.get("asset_path"):
            lines.append(f"   Diagram: /static/{q['asset_path']}")
        lines.append("")
        lines.append("   Answer: ________________________________________________")
        lines.append("")
    lines.extend(["---", "", "## Mark Scheme", ""])
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q['answer']} ({q['marks']} marks)")
    return "\n".join(lines)


def infer_topic(subject, question_text):
    subject_topics = TOPIC_KEYWORDS.get(subject, {})
    text = question_text.lower()
    for topic, keywords in subject_topics.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return "General"


def infer_difficulty(question_text, marks):
    text = question_text.lower()
    complexity = 1
    if marks >= 3:
        complexity += 1
    if marks >= 5:
        complexity += 1
    if any(keyword in text for keyword in ["explain", "compare", "evaluate", "why"]):
        complexity += 1
    if any(keyword in text for keyword in ["prove", "fully", "justify", "simultaneous", "quadratic"]):
        complexity += 1
    return max(DEFAULT_DIFFICULTY, min(MAX_DIFFICULTY, complexity))


def _clean_question_row(subject, row, source):
    question = (row.get("question") or row.get("question_text") or "").strip()
    answer = (row.get("answer") or row.get("answer_text") or "").strip()
    if not question or not answer:
        return None

    marks = row.get("marks", 1)
    try:
        marks = max(1, int(marks))
    except (TypeError, ValueError):
        marks = 1

    topic = (row.get("topic") or "").strip() or infer_topic(subject, question)
    difficulty_level = row.get("difficulty_level", row.get("difficulty"))
    try:
        difficulty_level = int(difficulty_level)
    except (TypeError, ValueError):
        difficulty_level = infer_difficulty(question, marks)

    return {
        "subject": subject,
        "topic": topic,
        "difficulty_level": max(DEFAULT_DIFFICULTY, min(MAX_DIFFICULTY, difficulty_level)),
        "question": question,
        "answer": answer,
        "asset_path": (row.get("asset_path") or "").strip() or None,
        "explanation": (row.get("explanation") or row.get("explanation_text") or "").strip(),
        "marks": marks,
        "source": source,
    }


def parse_question_bank_text(raw_text, subject, source="pasted"):
    text = raw_text.strip()
    if not text:
        return []

    parsed = _parse_json_question_text(text)
    if parsed is None:
        parsed = _parse_block_question_text(text)

    cleaned = []
    for row in parsed:
        normalized = _clean_question_row(subject, row, source)
        if normalized:
            cleaned.append(normalized)
    return cleaned


def _parse_json_question_text(text):
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if isinstance(payload, dict):
        if "questions" in payload and isinstance(payload["questions"], list):
            return payload["questions"]
        return [payload]

    if isinstance(payload, list):
        return payload

    return None


def _parse_block_question_text(text):
    blocks = re.split(r"\n\s*\n(?=(?:topic:|question:|q:|[-*]\s*question:))", text, flags=re.IGNORECASE)
    rows = []
    for block in blocks:
        working = block.strip()
        if not working:
            continue

        topic_match = re.search(r"(?:^|\n)\s*topic:\s*(.+)", working, flags=re.IGNORECASE)
        difficulty_match = re.search(r"(?:^|\n)\s*(?:difficulty|level):\s*(\d+)", working, flags=re.IGNORECASE)
        marks_match = re.search(r"(?:^|\n)\s*marks:\s*(\d+)", working, flags=re.IGNORECASE)
        question_match = re.search(r"(?:^|\n)\s*(?:question|q):\s*(.+)", working, flags=re.IGNORECASE)
        answer_match = re.search(
            r"(?:^|\n)\s*(?:answer|mark scheme|a):\s*(.+?)(?=\n\s*marks:\s*\d+|\Z)",
            working,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if question_match and answer_match:
            rows.append(
                {
                    "topic": topic_match.group(1).strip() if topic_match else "",
                    "difficulty_level": difficulty_match.group(1).strip() if difficulty_match else "",
                    "question": question_match.group(1).strip(),
                    "answer": answer_match.group(1).strip(),
                    "marks": marks_match.group(1).strip() if marks_match else 1,
                }
            )

    if rows:
        return rows

    fallback_rows = []
    for line in [entry.strip("- ").strip() for entry in text.splitlines() if entry.strip()]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 2:
            continue
        row = {"question": parts[0], "answer": parts[1], "marks": 1}
        for extra in parts[2:]:
            if extra.lower().startswith("topic:"):
                row["topic"] = extra.split(":", 1)[1].strip()
            elif extra.lower().startswith("difficulty:"):
                row["difficulty_level"] = extra.split(":", 1)[1].strip()
            elif extra.lower().startswith("marks:"):
                row["marks"] = extra.split(":", 1)[1].strip()
        fallback_rows.append(row)
    return fallback_rows


def build_subject_progress(questions, attempts):
    question_count = len(questions)
    if question_count == 0:
        return {"subject_score": 0, "topics": [], "next_focus": None}

    by_topic = defaultdict(lambda: {"available_difficulties": set(), "attempts": [], "question_count": 0})
    for question in questions:
        topic = question["topic"]
        by_topic[topic]["available_difficulties"].add(question["difficulty_level"])
        by_topic[topic]["question_count"] += 1

    for attempt in attempts:
        by_topic[attempt["topic"]]["attempts"].append(attempt)

    topics = []
    mastery_scores = []
    for topic, data in sorted(by_topic.items()):
        topic_attempts = sorted(data["attempts"], key=lambda row: row["taken_at"])
        ratios = [row["score"] / row["max_score"] for row in topic_attempts if row["max_score"]]
        mastery = round((sum(ratios) / len(ratios)) * 100) if ratios else 0
        target_difficulty = recommend_difficulty(data["available_difficulties"], topic_attempts)
        topics.append(
            {
                "topic": topic,
                "mastery": mastery,
                "attempts": len(topic_attempts),
                "question_count": data["question_count"],
                "target_difficulty": target_difficulty,
                "secure": mastery >= 85 and len(topic_attempts) >= 2 and target_difficulty >= max(data["available_difficulties"]),
            }
        )
        mastery_scores.append(mastery)

    topics.sort(key=lambda row: (row["secure"], row["mastery"], row["attempts"]))
    next_focus = topics[0] if topics else None
    subject_score = round(sum(mastery_scores) / len(mastery_scores)) if mastery_scores else 0
    return {"subject_score": subject_score, "topics": topics, "next_focus": next_focus}


def recommend_difficulty(available_difficulties, topic_attempts):
    available = sorted(available_difficulties)
    if not available:
        return DEFAULT_DIFFICULTY
    if not topic_attempts:
        return available[-1]

    current_level = available[0]
    for level in available:
        level_attempts = [row for row in topic_attempts if row["difficulty_level"] == level]
        if not level_attempts:
            return level
        recent = level_attempts[-2:]
        avg_ratio = sum(row["score"] / row["max_score"] for row in recent if row["max_score"]) / len(recent)
        current_level = level
        if len(recent) >= 2 and avg_ratio >= 0.85:
            continue
        if avg_ratio < 0.6 and level > available[0]:
            return available[max(0, available.index(level) - 1)]
        return level
    return current_level


def choose_adaptive_questions(questions, attempts, max_questions=5, allow_random_repeat=False):
    if not questions:
        return []
    if not attempts:
        ordered = sorted(
            questions,
            key=lambda row: (
                -row.get("difficulty_level", DEFAULT_DIFFICULTY),
                -row.get("marks", 1),
                0 if row.get("asset_path") else 1,
                row.get("topic", ""),
                row.get("id", 0),
            ),
        )
        return ordered[:max_questions]

    by_topic = defaultdict(list)
    for question in questions:
        by_topic[question["topic"]].append(question)

    progress = build_subject_progress(questions, attempts)
    attempted_question_ids = {row["question_id"] for row in attempts}
    recent_question_ids = [row["question_id"] for row in sorted(attempts, key=lambda row: row["taken_at"], reverse=True)[:20]]
    selected = []
    used_ids = set()

    topic_order = [row["topic"] for row in progress["topics"]] or sorted(by_topic)
    for topic in topic_order:
        topic_questions = by_topic[topic]
        topic_attempts = [row for row in attempts if row["topic"] == topic]
        target_level = recommend_difficulty({q["difficulty_level"] for q in topic_questions}, topic_attempts)
        candidates = [q for q in topic_questions if q["difficulty_level"] == target_level and q["id"] not in used_ids]
        unseen_candidates = [q for q in candidates if q["id"] not in attempted_question_ids]
        fresh_candidates = [q for q in unseen_candidates if q["id"] not in recent_question_ids]
        chosen_pool = fresh_candidates or unseen_candidates
        if chosen_pool:
            selected.append(sorted(chosen_pool, key=lambda row: (row["difficulty_level"], row["id"]))[0])
            used_ids.add(selected[-1]["id"])
        if len(selected) >= max_questions:
            break

    if len(selected) < max_questions:
        remaining = [q for q in questions if q["id"] not in used_ids and q["id"] not in attempted_question_ids]
        remaining.sort(key=lambda row: (-row["difficulty_level"], row["topic"], row["id"]))
        selected.extend(remaining[: max_questions - len(selected)])

    if len(selected) < max_questions and allow_random_repeat:
        repeat_pool = [q for q in questions if q["id"] not in used_ids]
        random.shuffle(repeat_pool)
        repeat_pool.sort(key=lambda row: (row["id"] in recent_question_ids, -row["difficulty_level"]))
        selected.extend(repeat_pool[: max_questions - len(selected)])

    return selected[:max_questions]


def build_question_generation_prompt(subject, academic_year, question_target, progress):
    next_focus = progress.get("next_focus")
    topic_rows = progress.get("topics", [])

    if topic_rows:
        ordered_topics = topic_rows[: min(6, len(topic_rows))]
    else:
        ordered_topics = [{"topic": "General", "mastery": 0, "target_difficulty": 1}]

    topic_instructions = []
    for row in ordered_topics:
        topic_instructions.append(
            f"- {row['topic']}: current mastery {row['mastery']}%, target difficulty {row['target_difficulty']}"
        )

    next_focus_text = (
        f"Primary weakness is {next_focus['topic']} with current target difficulty {next_focus['target_difficulty']}."
        if next_focus
        else "No prior attempts yet, so start from broad topic coverage but set the overall standard at elite Year 8 scholarship level."
    )

    return "\n".join(
        [
            f"Create a {subject} Year {academic_year} end-of-year exam question bank for a student performing at roughly the top 1% of Year {academic_year} pupils in the UK.",
            f"Generate exactly {question_target} questions with mark schemes.",
            "The bank must be topic-wise and adaptive to the student's previous test performance.",
            "This is not a mainstream revision sheet. It must feel selective, demanding, and scholarship-style for a nationally exceptional cohort.",
            next_focus_text,
            "Use the following topic priorities and target difficulty levels:",
            *topic_instructions,
            "Difficulty scale must be 1 to 5 where 1 is secure foundation and 5 is grade-9 stretch.",
            "Every topic must include real challenge. Even difficulty 3 should require fluent reasoning, not simple recall.",
            "Bias the bank toward difficulties 4 and 5 unless prior mastery data clearly shows a need to consolidate at a lower level.",
            "Within each topic, include a deliberate ramp from rigorous core knowledge to olympiad-style or scholarship-style extension.",
            "Prefer multi-step reasoning, proof, justification, comparison, interpretation of unfamiliar cases, and non-routine applications.",
            "Avoid repetitive arithmetic drills, simple definitions, and one-step retrieval questions unless they are needed as a small minority for topic coverage.",
            "Where suitable, include richer contexts, traps, and discriminating distractors that separate very strong pupils from merely secure pupils.",
            "Mark schemes must reward method, reasoning precision, and complete explanations rather than answer-only responses.",
            "Return only valid JSON as an array.",
            "Each JSON item must contain these keys:",
            '- "topic"',
            '- "difficulty_level"',
            '- "question"',
            '- "answer"',
            '- "marks"',
            "Ensure the questions are suitable for end-of-year assessment coverage, not random trivia.",
            "If a topic has weak mastery, include more questions at the target difficulty before moving higher.",
        ]
    )
