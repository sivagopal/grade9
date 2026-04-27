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
Create a UK Year 8 scholarship-level stretch mini test for a student performing at roughly the top 1% nationally.
Time: {minutes} minutes.
Subjects: {', '.join(subjects)}.
Prioritise weak subjects: {', '.join(weak_subjects)}.
Use demanding, discriminating questions with multi-step reasoning. Avoid easy recall items and routine one-step exercises.
For maths-heavy material, include a mix of algebraic modelling, multi-line word problems, and graph-interpretation questions where useful.
Return questions, answer spaces, and a mark scheme.
'''
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text


def generate_ai_subject_test(subject, weak_topics=None, minutes=30):
    client = _client()
    weak_topics = weak_topics or []
    focus_line = (
        f"Prioritise these weak topics: {', '.join(weak_topics)}. Even within weak topics, keep the standard selective and demanding."
        if weak_topics
        else "Cover the subject broadly at elite Year 8 scholarship standard, with a strong bias toward non-routine reasoning."
    )
    prompt = f'''
Create a UK Year 8 {subject} mini test for a student performing at roughly the top 1% nationally.
Time: {minutes} minutes.
Subject: {subject}.
{focus_line}
Use questions that would stretch exceptionally strong Year 8 pupils in the UK. Avoid routine textbook starters unless used sparingly to set up harder parts.
If the subject is Maths or Further Maths, require a blend of:
- multi-step algebra and manipulation
- multi-line word problems that need modelling before solving
- graph-based or diagram-based questions where a visual representation would genuinely test skill
- sparse direct recall, with emphasis on reasoning and method
Return questions, answer spaces, and a mark scheme.
'''
    response = client.responses.create(model="gpt-5.5", input=prompt)
    return response.output_text

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
- Aim for top-1% Year 8 in the UK: selective, demanding, multi-step where appropriate.
- Prefer unseen variants, richer contexts, and stronger reasoning than routine textbook drills.
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
