import os
import base64
import json
import re
from pathlib import Path

def _client():
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Install OpenAI with: pip install openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key, timeout=20.0, max_retries=1)

def openai_available():
    return bool(os.getenv("OPENAI_API_KEY"))

def _extract_json_array(output_text):
    output = output_text.strip()
    match = re.search(r"(\[.*\])", output, flags=re.DOTALL)
    payload = match.group(1) if match else output
    data = json.loads(payload)
    if not isinstance(data, list):
        raise RuntimeError("OpenAI response did not return a JSON array.")
    return data

def generate_ai_test(subjects, weak_subjects, minutes=10):
    client = _client()
    prompt = f'''
Create a demanding UK Year 8 KS3 mini test that actually discriminates between secure, strong, and exceptional performance.
Time: {minutes} minutes.
Subjects: {', '.join(subjects)}.
Prioritise weak subjects: {', '.join(weak_subjects)}.
Keep the standard aligned to high-attaining top-set KS3 and early GCSE transition, without drifting into university-style difficulty.
Use a balanced mix of fluent core knowledge, application under pressure, and short reasoning.
Avoid trivia, one-step recall chains, and worksheet filler.
For maths-heavy material, include graph interpretation, numerical method, algebra, and geometry where useful.
Return questions, answer spaces, and a mark scheme.
'''
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text


def generate_ai_subject_test(subject, weak_topics=None, minutes=30):
    client = _client()
    weak_topics = weak_topics or []
    focus_line = (
        f"Prioritise these weak topics: {', '.join(weak_topics)}."
        if weak_topics
        else "Cover the subject broadly at a high-attaining UK Year 8 KS3 standard."
    )
    prompt = f'''
Create a demanding UK Year 8 {subject} mini test aligned to high-attaining KS3 classroom expectations.
Time: {minutes} minutes.
Subject: {subject}.
{focus_line}
Use questions that feel like a selective top-set assessment, not a recap sheet or BBC Bitesize filler.
Include a clear difficulty ramp: secure fluency, then discriminating application, then a few genuinely stretching questions.
Avoid one-step retrieval except where needed as a small part of coverage.
If the subject is Maths or Further Maths, require a blend of:
- arithmetic and proportional reasoning
- algebra and manipulation
- graph-based or diagram-based questions where useful
- clear method marks and concise reasoning
Return questions, answer spaces, and a mark scheme.
'''
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text


def _normalize_generated_question(row, default_subject):
    question = str(row.get("question") or row.get("question_text") or "").strip()
    answer = str(row.get("answer") or row.get("answer_text") or "").strip()
    if not question or not answer:
        return None

    try:
        difficulty_level = max(1, min(5, int(row.get("difficulty_level", 2) or 2)))
    except (TypeError, ValueError):
        difficulty_level = 2

    try:
        marks = max(1, int(row.get("marks", 1) or 1))
    except (TypeError, ValueError):
        marks = 1

    return {
        "subject": str(row.get("subject") or default_subject or "Mixed").strip() or (default_subject or "Mixed"),
        "topic": str(row.get("topic") or "General").strip() or "General",
        "difficulty_level": difficulty_level,
        "question": question,
        "answer": answer,
        "explanation": str(row.get("explanation") or row.get("explanation_text") or "").strip(),
        "marks": marks,
    }


def generate_ai_subject_test_payload(subject, weak_topics=None, minutes=30, question_target=None, available_topics=None, randomize_topics=False):
    client = _client()
    weak_topics = weak_topics or []
    available_topics = available_topics or []
    question_target = max(10, min(20, int(question_target or round(minutes / 4) or 10)))
    if randomize_topics and available_topics:
        focus_line = (
            "Cover the subject broadly using these topics where appropriate: "
            + ", ".join(available_topics[:18])
            + ". Spread questions across the subject instead of staying on one narrow topic."
        )
    elif weak_topics:
        focus_line = f"Prioritise these weak topics: {', '.join(weak_topics)}."
    else:
        focus_line = "Cover the subject broadly at a high-attaining UK Year 8 KS3 standard."

    topic_guard_lines = []
    normalized_topics = {" ".join(str(topic or "").strip().lower().split()) for topic in weak_topics}
    if "probability" in normalized_topics and "statistics" not in normalized_topics and "statistics and probability" not in normalized_topics:
        topic_guard_lines.append("- If the requested topic is Probability, do not drift into mean, median, mode, range, or survey-data questions.")
    if "statistics" in normalized_topics and "probability" not in normalized_topics and "statistics and probability" not in normalized_topics:
        topic_guard_lines.append("- If the requested topic is Statistics, do not drift into bag, spinner, dice, or event-probability questions.")
    topic_guard_text = "\n".join(topic_guard_lines)

    prompt = f"""
Create a demanding UK Year 8 {subject} test in strict JSON.
Time allowed: {minutes} minutes.
Subject: {subject}.
Aim for about {question_target} questions and a realistic total mark load for the available time.
{focus_line}

Requirements:
- Return only a JSON array.
- Each item must contain: topic, difficulty_level, question, answer, explanation, marks.
- Use a clear difficulty ramp from secure fluency to discriminating application and moderate stretch.
- If you return 10 questions, use this difficulty mix: 4 questions at difficulty 5, 2 at difficulty 4, 3 at difficulty 3, and 1 at difficulty 2.
- Interleave harder questions through the paper instead of grouping all the hardest questions together.
- Marks must be realistic for the time available.
- Avoid trivial recall, repetitive templates, and questions that can be done without thinking.
- If the subject is Maths or Further Maths, include a balanced spread of algebra, proportion, geometry, graphs, and reasoning when relevant.
- If the subject is a language, include vocabulary in context, short translation, and accuracy under pressure rather than isolated word-list prompts only.
- If one topic is specified as weak, make that topic more prominent without making the whole paper repetitive.
{topic_guard_text}
"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    payload = _extract_json_array(response.output_text)
    return [normalized for row in payload if (normalized := _normalize_generated_question(row, subject))]


def generate_ai_mixed_test_payload(subjects, weak_subjects, minutes=10, question_target=None):
    client = _client()
    question_target = max(10, min(20, int(question_target or round(minutes / 3) or 10), len(subjects) * 4))
    prompt = f"""
Create a demanding UK Year 8 KS3 mixed mini test in strict JSON.
Time allowed: {minutes} minutes.
Available subjects: {', '.join(subjects)}.
Prioritise weaker subjects: {', '.join(weak_subjects)}.
Aim for about {question_target} short questions with a realistic mark load.

Requirements:
- Return only a JSON array.
- Each item must contain: subject, topic, difficulty_level, question, answer, explanation, marks.
- Spread the paper across multiple subjects.
- Use a balanced mix of fluency, application, and short reasoning.
- Avoid easy filler and one-step trivia.
"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    payload = _extract_json_array(response.output_text)
    return [normalized for row in payload if (normalized := _normalize_generated_question(row, row.get("subject") or "Mixed"))]

def generate_question_bank_from_prompt(prompt_text):
    client = _client()
    response = client.responses.create(model="gpt-5.5", input=prompt_text)
    return _extract_json_array(response.output_text)


def generate_similar_question_bank(subject, topic, reference_rows, question_target=8):
    client = _client()
    examples = json.dumps(
        [
            {
                "topic": row.get("topic", topic),
                "difficulty_level": row.get("difficulty_level", 4),
                "question": row.get("question", ""),
                "answer": row.get("answer", ""),
                "marks": row.get("marks", 2),
            }
            for row in reference_rows[:5]
        ],
        ensure_ascii=False,
    )
    prompt = f"""
Create a fresh JSON question bank of similar but non-duplicate questions.
Subject: {subject}
Primary topic: {topic}
Question target: {question_target}

Requirements:
- Return only a JSON array.
- Each item must contain: topic, difficulty_level, question, answer, marks, explanation.
- The new questions must be similar in underlying skill to the examples but must not copy wording, numbers, or final answers.
- Aim for high-attaining UK Year 8 KS3 standard, with a mix of fluency, discriminating application, and real stretch.
- Prefer unseen variants, realistic classroom wording, and proper progression across the set.
- Avoid one-step retrieval clones and weak paraphrases of the examples.
- If the examples are algebraic or graphical, produce some variants as multi-line word problems and some as graph-interpretation or diagram-led questions.

Reference questions:
{examples}
"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return _extract_json_array(response.output_text)

def extract_questions_from_text(subject, raw_text):
    client = _client()
    prompt = f"""
Convert this pasted GCSE question bank text into strict JSON.
Subject: {subject}

Return only a JSON array. Each item must contain:
- topic
- difficulty_level (1 to 5)
- question
- answer
- marks

Use the pasted content only. Infer topic and difficulty if needed.
Pasted text:
{raw_text}
"""
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return _extract_json_array(response.output_text)

def mark_scanned_answers(file_path, mark_scheme_text, student_context_text=""):
    client = _client()
    path = Path(file_path)
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    mime = "image/png"
    if path.suffix.lower() in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif path.suffix.lower() == ".pdf":
        mime = "application/pdf"

    prompt = f'''
You are marking a UK GCSE-style self-test for a Year 8 student aiming for grade 9.
Be strict but encouraging.

Mark scheme:
{mark_scheme_text}

Student context:
{student_context_text}

Return score by question, total score, misconceptions, and tomorrow's improvement target.
'''
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:{mime};base64,{data}"},
                ],
            }
        ],
    )
    return response.output_text
