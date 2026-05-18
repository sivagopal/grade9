import json
import re
import random
from collections import defaultdict
from datetime import date

from app.math_format import render_math_plain

DEFAULT_DIFFICULTY = 1
MAX_DIFFICULTY = 5

SOURCE_PRIORITY = {
    "year8-biology-grade9-bank": 5,
    "year8-maths-deterministic-algebra": 7,
    "year8-maths-grade9-bank": 5,
    "year8-maths-ks3-bank": 3,
    "manual-web": 5,
    "manual-api": 5,
    "manual": 3,
    "chatgpt-paste": 2,
    "daily-auto": 2,
}

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
    {"subject": "Maths", "topic": "Graphs", "difficulty_level": 2, "question": "The line y = 2x + 3 is shown on a graph. State the gradient and the y-intercept.", "answer": "Gradient 2, y-intercept 3.", "marks": 2},
    {"subject": "Maths", "topic": "Graphs", "difficulty_level": 3, "question": "A graph passes through the points (1, 4), (2, 7), (3, 10) and (4, 13). Find a linear rule linking x and y.", "answer": "y = 3x + 1", "marks": 3},
    {"subject": "Maths", "topic": "Statistics and Probability", "difficulty_level": 2, "question": "A bag contains 3 red counters, 5 blue counters and 2 green counters. Find the probability of selecting a blue counter.", "answer": "5/10 or 1/2", "marks": 2},
    {"subject": "Maths", "topic": "Statistics and Probability", "difficulty_level": 3, "question": "The scores 4, 7, 9, 9 and 11 are shown in a data set. Find the mean score.", "answer": "8", "marks": 2},
    {"subject": "Maths", "topic": "Transformations", "difficulty_level": 3, "question": "Shape A has vertices (1, 1), (4, 1) and (2, 3). It is rotated 90 degrees anticlockwise about the origin. State the coordinates of the image.", "answer": "(-1, 1), (-1, 4) and (-3, 2)", "marks": 3},
    {"subject": "Maths", "topic": "Surface Area and Volume", "difficulty_level": 3, "question": "A cuboid has length 8 cm, width 5 cm and height 3 cm. Work out its volume.", "answer": "120 cm^3", "marks": 2},
    {"subject": "Maths", "topic": "Surface Area and Volume", "difficulty_level": 4, "question": "A cuboid has length 6 cm, width 4 cm and height 3 cm. Work out its total surface area.", "answer": "108 cm^2", "marks": 3},
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
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'puella'.", "answer": "girl", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'puer'.", "answer": "boy", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'aqua'.", "answer": "water", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'canis'.", "answer": "dog", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'equus'.", "answer": "horse", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'amicus'.", "answer": "friend", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'mater'.", "answer": "mother", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'pater'.", "answer": "father", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'rex'.", "answer": "king", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'regina'.", "answer": "queen", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'via'.", "answer": "road or street", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'villa'.", "answer": "house or villa", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'hortus'.", "answer": "garden", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'urbs'.", "answer": "city", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'magnus'.", "answer": "big or great", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'parvus'.", "answer": "small", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'laetus'.", "answer": "happy", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'iratus'.", "answer": "angry", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'portat'.", "answer": "carries", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'currit'.", "answer": "runs", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'videt'.", "answer": "sees", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 1, "question": "Give the meaning of 'audit'.", "answer": "hears", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "What is the Latin for 'water'?", "answer": "aqua", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "What is the Latin for 'friend'?", "answer": "amicus", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "What is the Latin for 'city'?", "answer": "urbs", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "What is the Latin for 'happy'?", "answer": "laetus", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "What is the Latin for 'runs'?", "answer": "currit", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "Which Latin word in 'servus aquam ad villam portat' means 'water'?", "answer": "aquam or aqua", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "Which Latin word in 'parva puella in horto currit' means 'garden'?", "answer": "horto or hortus", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 2, "question": "Which Latin word in 'iratus puer canem videt' means 'angry'?", "answer": "iratus", "marks": 1},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 3, "question": "Translate: servus aquam ad villam portat.", "answer": "The slave carries water to the house.", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 3, "question": "Translate: laeta puella in horto currit.", "answer": "The happy girl runs in the garden.", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 3, "question": "Translate: iratus puer canem parvum videt.", "answer": "The angry boy sees the small dog.", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 3, "question": "Choose the best translation of 'regina ad urbem currit'.", "answer": "The queen runs to the city.", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 3, "question": "A student translates 'parva regina equum audit' as 'The big queen hears the horse.' Which Latin word has been mistranslated, and what should it mean?", "answer": "'parva' has been mistranslated; it means 'small'.", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Write the Latin for 'the happy girl'.", "answer": "laeta puella", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Write the Latin for 'the angry queen'.", "answer": "irata regina", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Write the Latin for 'the small boy'.", "answer": "parvus puer", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Write the Latin for 'the big dog'.", "answer": "magnus canis", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Translate the phrase 'road to the city' into Latin.", "answer": "via ad urbem", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Translate the phrase 'friend in the garden' into Latin.", "answer": "amicus in horto", "marks": 2},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "Sort these three Latin words by word class: portat, regina, iratus.", "answer": "portat = verb, regina = noun, iratus = adjective", "marks": 3},
    {"subject": "Latin", "topic": "Vocabulary", "difficulty_level": 4, "question": "From the list puella, currit, laeta, aqua, choose one noun, one verb, and one adjective.", "answer": "For example: puella = noun, currit = verb, laeta = adjective", "marks": 3},
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


def question_pattern_key(question_text):
    text = str(question_text or "").strip().lower()
    text = re.sub(r"gbp\s*\d+(?:\.\d+)?", "gbp #", text)
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"\b[a-z]\b", "v", text)
    text = re.sub(r"\s+", " ", text)
    return text


def get_seed_questions():
    return [dict(row) for row in SEED_QUESTIONS]


def _markdown_asset_line(asset_path, *, label, fallback_note):
    asset_ref = str(asset_path or "").strip()
    if not asset_ref:
        return ""
    if asset_ref.startswith(("http://", "https://")):
        return f"{label}: {asset_ref}"
    return f"{label}: {fallback_note}"


def format_test_markdown(questions, title_subject=None, duration_minutes=10):
    today = date.today().isoformat()
    total_marks = sum(q["marks"] for q in questions)
    heading = f"# GCSE Grade 9 {title_subject} Test — {today}" if title_subject else f"# GCSE Grade 9 Mini Test — {today}"
    lines = [
        heading,
        "",
        f"Time allowed: {duration_minutes} minutes",
        f"Total marks: {total_marks}",
        "",
        "## Questions",
        "",
    ]
    for i, q in enumerate(questions, 1):
        topic = q.get("topic", "General")
        difficulty = q.get("difficulty_level", DEFAULT_DIFFICULTY)
        lines.append(
            f"{i}. **{q['subject']}** | Topic: {topic} | Difficulty: {difficulty} | ({q['marks']} marks): {render_math_plain(q['question'])}"
        )
        if q.get("asset_path"):
            diagram_line = _markdown_asset_line(
                q.get("asset_path"),
                label="   Diagram",
                fallback_note="available in the web app or PDF paper version",
            )
            if diagram_line:
                lines.append(diagram_line)
        lines.append("")
        lines.append("   Answer: ________________________________________________")
        lines.append("")
    lines.extend(["---", "", "## Mark Scheme", ""])
    for i, q in enumerate(questions, 1):
        question_context = str(q.get("question", "")).strip()
        if len(question_context) > 72:
            question_context = question_context[:69].rstrip() + "..."
        lines.append(f"{i}. {q.get('topic', 'General')}: {render_math_plain(question_context)}")
        lines.append(f"   Answer: {render_math_plain(q['answer'])} ({q['marks']} marks)")
        if q.get("answer_asset_path"):
            mark_scheme_line = _markdown_asset_line(
                q.get("answer_asset_path"),
                label="   Worked mark scheme",
                fallback_note="available in the web app or PDF answer sheet",
            )
            if mark_scheme_line:
                lines.append(mark_scheme_line)
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
    subject_name = " ".join(str(row.get("subject") or subject or "").strip().split())
    question = str(row.get("question") or row.get("question_text") or "").strip()
    answer = str(row.get("answer") or row.get("answer_text") or "").strip()
    asset_path = str(
        row.get("asset_path")
        or row.get("question_asset_path")
        or row.get("question_image_path")
        or row.get("image_url")
        or row.get("question_image_url")
        or row.get("question_url")
        or ""
    ).strip() or None
    answer_asset_path = str(
        row.get("answer_asset_path")
        or row.get("answer_image_path")
        or row.get("answer_image_url")
        or row.get("markscheme_url")
        or row.get("mark_scheme_url")
        or row.get("answer_url")
        or ""
    ).strip() or None
    if not subject_name or (not question and not asset_path) or (not answer and not answer_asset_path):
        return None

    marks = row.get("marks", 1)
    try:
        marks = max(1, int(marks))
    except (TypeError, ValueError):
        marks = 1

    topic = str(row.get("topic") or "").strip() or infer_topic(subject_name, question)
    subtopic = str(row.get("subtopic") or "").strip() or None
    difficulty_level = row.get("difficulty_level", row.get("difficulty"))
    try:
        difficulty_level = int(difficulty_level)
    except (TypeError, ValueError):
        difficulty_level = infer_difficulty(question, marks)

    return {
        "subject": subject_name,
        "topic": topic,
        "subtopic": subtopic,
        "difficulty_level": max(DEFAULT_DIFFICULTY, min(MAX_DIFFICULTY, difficulty_level)),
        "question": question,
        "answer": answer,
        "asset_path": asset_path,
        "answer_asset_path": answer_asset_path,
        "explanation": str(row.get("explanation") or row.get("explanation_text") or "").strip(),
        "video_url": (
            str(
                row.get("video_url")
            or row.get("video_search_url")
            or row.get("video")
            or row.get("video_link")
            or row.get("videoLink")
            or ""
            )
        ).strip() or None,
        "marks": marks,
        "source": source,
    }


def normalize_question_rows(rows, default_subject=None, source="pasted"):
    cleaned = []
    for row in rows:
        normalized = _clean_question_row(default_subject, row, source)
        if normalized:
            cleaned.append(normalized)
    return cleaned


def parse_question_bank_text(raw_text, subject=None, source="pasted"):
    text = raw_text.strip()
    if not text:
        return []

    parsed = _parse_json_question_text(text)
    if parsed is None:
        parsed = _parse_block_question_text(text)
    return normalize_question_rows(parsed, default_subject=subject, source=source)


def _parse_json_question_text(text):
    cleaned_text = str(text or "").strip()
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
    cleaned_text = re.sub(r",(\s*[}\]])", r"\1", cleaned_text)
    try:
        payload = json.loads(cleaned_text)
    except json.JSONDecodeError:
        repaired_text = _repair_json_math_backslashes(cleaned_text)
        try:
            payload = json.loads(repaired_text)
        except json.JSONDecodeError:
            return None

    if isinstance(payload, dict):
        if "questions" in payload and isinstance(payload["questions"], list):
            return payload["questions"]
        return [payload]

    if isinstance(payload, list):
        return payload

    return None


def _repair_json_math_backslashes(text):
    repaired = []
    in_string = False
    i = 0
    while i < len(text):
        char = text[i]
        if char == '"':
            backslash_count = 0
            j = i - 1
            while j >= 0 and text[j] == "\\":
                backslash_count += 1
                j -= 1
            if backslash_count % 2 == 0:
                in_string = not in_string
            repaired.append(char)
            i += 1
            continue
        if in_string and char == "\\":
            next_char = text[i + 1] if i + 1 < len(text) else ""
            if next_char in {'"', "\\", "/"}:
                repaired.append(char)
            elif next_char == "u" and i + 5 < len(text) and re.fullmatch(r"[0-9a-fA-F]{4}", text[i + 2 : i + 6]):
                repaired.append(char)
            else:
                repaired.append("\\\\")
            i += 1
            continue
        repaired.append(char)
        i += 1
    return "".join(repaired)


def _parse_block_question_text(text):
    blocks = re.split(r"\n\s*\n(?=(?:subject:|topic:|question:|q:|[-*]\s*question:))", text, flags=re.IGNORECASE)
    rows = []
    for block in blocks:
        working = block.strip()
        if not working:
            continue

        subject_match = re.search(r"(?:^|\n)\s*subject:\s*(.+)", working, flags=re.IGNORECASE)
        topic_match = re.search(r"(?:^|\n)\s*topic:\s*(.+)", working, flags=re.IGNORECASE)
        subtopic_match = re.search(r"(?:^|\n)\s*subtopic:\s*(.+)", working, flags=re.IGNORECASE)
        difficulty_match = re.search(r"(?:^|\n)\s*(?:difficulty|level):\s*(\d+)", working, flags=re.IGNORECASE)
        marks_match = re.search(r"(?:^|\n)\s*marks:\s*(\d+)", working, flags=re.IGNORECASE)
        question_match = re.search(r"(?:^|\n)\s*(?:question|q):\s*(.+)", working, flags=re.IGNORECASE)
        answer_match = re.search(
            r"(?:^|\n)\s*(?:answer|mark scheme|a):\s*(.+?)(?=\n\s*(?:explanation|video(?:\s*url)?|video\s*search\s*url|image\s*url|question\s*image\s*url|question\s*url|asset\s*url|answer\s*image\s*url|mark\s*scheme\s*url|markscheme\s*url|answer\s*url|marks):|\Z)",
            working,
            flags=re.IGNORECASE | re.DOTALL,
        )
        explanation_match = re.search(
            r"(?:^|\n)\s*explanation:\s*(.+?)(?=\n\s*(?:video(?:\s*url)?|video\s*search\s*url|image\s*url|question\s*image\s*url|question\s*url|asset\s*url|answer\s*image\s*url|mark\s*scheme\s*url|markscheme\s*url|answer\s*url|marks):|\Z)",
            working,
            flags=re.IGNORECASE | re.DOTALL,
        )
        question_asset_match = re.search(
            r"(?:^|\n)\s*(?:image\s*url|question\s*image\s*url|question\s*url|asset\s*url):\s*(.+)",
            working,
            flags=re.IGNORECASE,
        )
        answer_asset_match = re.search(
            r"(?:^|\n)\s*(?:answer\s*image\s*url|mark\s*scheme\s*url|markscheme\s*url|answer\s*url):\s*(.+)",
            working,
            flags=re.IGNORECASE,
        )
        video_match = re.search(
            r"(?:^|\n)\s*(?:video|video\s*url|video\s*search\s*url):\s*(.+)",
            working,
            flags=re.IGNORECASE,
        )

        if question_match and answer_match:
            rows.append(
                {
                    "subject": subject_match.group(1).strip() if subject_match else "",
                    "topic": topic_match.group(1).strip() if topic_match else "",
                    "subtopic": subtopic_match.group(1).strip() if subtopic_match else "",
                    "difficulty_level": difficulty_match.group(1).strip() if difficulty_match else "",
                    "question": question_match.group(1).strip(),
                    "answer": answer_match.group(1).strip(),
                    "asset_path": question_asset_match.group(1).strip() if question_asset_match else "",
                    "answer_asset_path": answer_asset_match.group(1).strip() if answer_asset_match else "",
                    "explanation": explanation_match.group(1).strip() if explanation_match else "",
                    "video_url": video_match.group(1).strip() if video_match else "",
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
            lowered = extra.lower()
            if lowered.startswith("subject:"):
                row["subject"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("topic:"):
                row["topic"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("subtopic:"):
                row["subtopic"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("difficulty:"):
                row["difficulty_level"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("marks:"):
                row["marks"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("explanation:"):
                row["explanation"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("video:") or lowered.startswith("video url:") or lowered.startswith("video search url:"):
                row["video_url"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("asset path:") or lowered.startswith("question image:"):
                row["asset_path"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("image url:") or lowered.startswith("question image url:") or lowered.startswith("question url:") or lowered.startswith("asset url:"):
                row["asset_path"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("answer image:") or lowered.startswith("answer asset path:"):
                row["answer_asset_path"] = extra.split(":", 1)[1].strip()
            elif lowered.startswith("answer image url:") or lowered.startswith("mark scheme url:") or lowered.startswith("markscheme url:") or lowered.startswith("answer url:"):
                row["answer_asset_path"] = extra.split(":", 1)[1].strip()
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
        if attempt["topic"] not in by_topic:
            continue
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


def source_priority(row):
    return SOURCE_PRIORITY.get(row.get("source", ""), 1)


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

    def template_penalty(row, pattern_counts, topic_counts, topic_limit=None):
        pattern_key = question_pattern_key(row.get("question"))
        topic_key = row.get("topic", "General")
        pattern_count = pattern_counts.get(pattern_key, 0)
        topic_count = topic_counts.get(topic_key, 0)
        over_topic_limit = topic_limit is not None and topic_count >= topic_limit
        return (pattern_count, over_topic_limit, topic_count)

    if not attempts:
        by_topic = defaultdict(list)
        for question in questions:
            by_topic[question["topic"]].append(question)

        selected = []
        used_ids = set()
        pattern_counts = {}
        topic_counts = {}
        topic_limit = max(1, round(max_questions / max(1, len(by_topic)))) + 1
        for topic in sorted(
            by_topic,
            key=lambda topic: (
                -max(source_priority(row) for row in by_topic[topic]),
                -max(row.get("difficulty_level", DEFAULT_DIFFICULTY) for row in by_topic[topic]),
                topic,
            ),
        ):
            best_in_topic = sorted(
                by_topic[topic],
                key=lambda row: (
                    *template_penalty(row, pattern_counts, topic_counts, topic_limit),
                    -source_priority(row),
                    -row.get("difficulty_level", DEFAULT_DIFFICULTY),
                    -row.get("marks", 1),
                    0 if row.get("asset_path") else 1,
                    row.get("id", 0),
                ),
            )[0]
            selected.append(best_in_topic)
            used_ids.add(best_in_topic["id"])
            pattern_key = question_pattern_key(best_in_topic.get("question"))
            topic_key = best_in_topic.get("topic", "General")
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1
            if len(selected) >= max_questions:
                return selected

        remaining = sorted(
            [row for row in questions if row["id"] not in used_ids],
            key=lambda row: (
                *template_penalty(row, pattern_counts, topic_counts, topic_limit),
                -source_priority(row),
                -row.get("difficulty_level", DEFAULT_DIFFICULTY),
                -row.get("marks", 1),
                0 if row.get("asset_path") else 1,
                row.get("topic", ""),
                row.get("id", 0),
            ),
        )
        for row in remaining:
            if len(selected) >= max_questions:
                break
            selected.append(row)
            pattern_key = question_pattern_key(row.get("question"))
            topic_key = row.get("topic", "General")
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1
        return selected[:max_questions]

    by_topic = defaultdict(list)
    for question in questions:
        by_topic[question["topic"]].append(question)

    progress = build_subject_progress(questions, attempts)
    attempted_question_ids = {row["question_id"] for row in attempts}
    recent_question_ids = [row["question_id"] for row in sorted(attempts, key=lambda row: row["taken_at"], reverse=True)[:20]]
    selected = []
    used_ids = set()
    pattern_counts = {}
    topic_counts = {}
    topic_limit = max(1, round(max_questions / max(1, len(by_topic)))) + 1

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
            selected.append(
                sorted(
                    chosen_pool,
                    key=lambda row: (
                        *template_penalty(row, pattern_counts, topic_counts, topic_limit),
                        -source_priority(row),
                        -row.get("difficulty_level", DEFAULT_DIFFICULTY),
                        -row.get("marks", 1),
                        0 if row.get("asset_path") else 1,
                        row.get("id", 0),
                    ),
                )[0]
            )
            used_ids.add(selected[-1]["id"])
            pattern_key = question_pattern_key(selected[-1].get("question"))
            topic_key = selected[-1].get("topic", "General")
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1
        if len(selected) >= max_questions:
            break

    if len(selected) < max_questions:
        remaining = [q for q in questions if q["id"] not in used_ids and q["id"] not in attempted_question_ids]
        remaining.sort(
            key=lambda row: (
                *template_penalty(row, pattern_counts, topic_counts, topic_limit),
                -source_priority(row),
                -row["difficulty_level"],
                -row.get("marks", 1),
                row["topic"],
                row["id"],
            )
        )
        for row in remaining:
            if len(selected) >= max_questions:
                break
            selected.append(row)
            pattern_key = question_pattern_key(row.get("question"))
            topic_key = row.get("topic", "General")
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1

    if len(selected) < max_questions and allow_random_repeat:
        repeat_pool = [q for q in questions if q["id"] not in used_ids]
        random.shuffle(repeat_pool)
        repeat_pool.sort(
            key=lambda row: (
                row["id"] in recent_question_ids,
                *template_penalty(row, pattern_counts, topic_counts, topic_limit),
                -source_priority(row),
                -row["difficulty_level"],
                -row.get("marks", 1),
            )
        )
        for row in repeat_pool:
            if len(selected) >= max_questions:
                break
            selected.append(row)
            pattern_key = question_pattern_key(row.get("question"))
            topic_key = row.get("topic", "General")
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1

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
        else "No prior attempts yet, so start from broad topic coverage at a strong UK Year 8 KS3 standard."
    )

    return "\n".join(
        [
            f"Create a {subject} Year {academic_year} end-of-year question bank aligned to high-attaining UK KS3 classroom standards.",
            f"Generate exactly {question_target} questions with mark schemes.",
            "The bank must be topic-wise and adaptive to the student's previous test performance.",
            "The bank should feel like a selective top-set assessment with clear progression and genuine reasoning, not worksheet filler or BBC Bitesize recap.",
            next_focus_text,
            "Use the following topic priorities and target difficulty levels:",
            *topic_instructions,
            "Difficulty scale must be 1 to 5 where 1 is secure foundation and 5 is grade-9 stretch.",
            "Build a clear ramp from secure fluency to discriminating application and genuine stretch.",
            "Prefer multi-step reasoning, method marks, comparison, explanation, interpretation, and non-routine but age-appropriate applications.",
            "Avoid repetitive arithmetic drills, trivia, and one-step retrieval questions except as a small minority for coverage.",
            "Questions should test what the student can actually do, not just whether they remember an isolated fact.",
            "For Maths and Further Maths, include graph-based, algebraic, geometrical, and proportional reasoning where appropriate.",
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
