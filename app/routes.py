from datetime import date, datetime
from functools import wraps
import hashlib
import json
import random
import re
import secrets
from uuid import uuid4

from flask import Blueprint, Response, current_app, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from itsdangerous import BadSignature, URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.analyser import analyse_week, generate_next_day_timetable, generate_weekend_plan, next_day_name
from app.config import SUBJECTS
from app.emailer import DEFAULT_REPORT_RECIPIENT, send_daily_report_email
from app.math_format import render_math_html
from app.matplotlib_service import enrich_questions_with_dynamic_assets, load_question_asset_image, question_supports_live_asset, render_asset_png_bytes
from app.openai_helper import (
    extract_questions_from_text,
    generate_ai_mixed_test_payload,
    generate_ai_subject_test_payload,
    mark_scanned_answers,
    openai_available,
)
from app.paths import QUESTION_BANK_IMAGE_DIR, UPLOAD_DIR
from app.question_bank import (
    choose_adaptive_questions,
    format_test_markdown,
    normalize_question_rows,
    parse_question_bank_text,
    question_pattern_key,
    source_priority,
)
from app.pdf_export import build_mark_scheme_pdf, build_test_pdf
from app.reports import build_daily_report
from app.review import build_wrong_answer_review
from app.resources import recommend_resources, recommend_topic_videos
from app.storage import PlannerDB

bp = Blueprint("main", __name__)
db = PlannerDB()

MIN_TEST_QUESTION_COUNT = 10
DEFAULT_PAPER_DIFFICULTY_SEQUENCE = [3, 5, 4, 3, 5, 2, 4, 5, 3, 5]
QUESTION_BANK_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def get_active_subjects():
    return db.get_subject_names()


def get_testing_subjects():
    return db.get_regular_subject_names()


def get_active_stem_subjects():
    return db.get_stem_subjects()


def get_analysis():
    daily = db.get_recent_daily_logs(7)
    subject_logs = db.get_recent_subject_logs(7)
    return analyse_week(
        daily,
        subject_logs,
        subjects=get_active_subjects(),
        stem_subjects=get_active_stem_subjects(),
    )


def _admin_session_key():
    return "admin_user"


def admin_registered():
    return db.has_admin_user()


def admin_logged_in():
    return bool(session.get(_admin_session_key()))


def current_admin_username():
    return str(session.get(_admin_session_key()) or "").strip()


def _set_admin_session(username):
    session[_admin_session_key()] = username
    session.modified = True


def _clear_admin_session():
    session.pop(_admin_session_key(), None)
    session.modified = True


def _admin_redirect_target():
    next_url = request.args.get("next", "").strip()
    if next_url.startswith("/"):
        return next_url
    return url_for("main.question_bank_page")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if admin_logged_in():
            return view(*args, **kwargs)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Admin login required."}), 401
        return redirect(url_for("main.admin_login", next=request.full_path if request.query_string else request.path))

    return wrapped


def _figure_serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="question-figure")


def _question_paper_serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="question-paper")


def _figure_token_payload(question):
    return {
        "id": question.get("id"),
        "subject": question.get("subject"),
        "topic": question.get("topic"),
        "question": question.get("question"),
        "difficulty_level": question.get("difficulty_level"),
        "marks": question.get("marks"),
    }


def _download_urls(config, generated_test_id=None):
    if generated_test_id:
        return {
            "download_md_url": url_for("main.download_saved_generated_test", test_id=generated_test_id, format="md"),
            "download_pdf_url": url_for(
                "main.download_saved_generated_test",
                test_id=generated_test_id,
                format="pdf",
                document="paper",
            ),
            "download_mark_scheme_pdf_url": url_for(
                "main.download_saved_generated_test",
                test_id=generated_test_id,
                format="pdf",
                document="markscheme",
            ),
        }
    return {
        "download_md_url": url_for(
            "main.download_test",
            test_type=config["test_type"],
            subject=config["selected_subject"],
            subtopic=config.get("selected_subtopic", ""),
            source=config["source"],
            selection_mode=config.get("selection_mode", "adaptive"),
            diagram_only="1" if config.get("diagram_only") else "0",
            duration=config["duration"],
            count=config["question_count"],
            format="md",
        ),
        "download_pdf_url": url_for(
            "main.download_test",
            test_type=config["test_type"],
            subject=config["selected_subject"],
            subtopic=config.get("selected_subtopic", ""),
            source=config["source"],
            selection_mode=config.get("selection_mode", "adaptive"),
            diagram_only="1" if config.get("diagram_only") else "0",
            duration=config["duration"],
            count=config["question_count"],
            format="pdf",
            document="paper",
        ),
        "download_mark_scheme_pdf_url": url_for(
            "main.download_test",
            test_type=config["test_type"],
            subject=config["selected_subject"],
            subtopic=config.get("selected_subtopic", ""),
            source=config["source"],
            selection_mode=config.get("selection_mode", "adaptive"),
            diagram_only="1" if config.get("diagram_only") else "0",
            duration=config["duration"],
            count=config["question_count"],
            format="pdf",
            document="markscheme",
        ),
    }


def _paper_title(config, saved_generated_test=None):
    if saved_generated_test:
        return saved_generated_test["title"]
    if config["test_type"] == "daily_all":
        return "GCSE Grade 9 Mixed Test"
    return f"GCSE Grade 9 {config['selected_subject']} Test"


def _question_paper_payload(questions, config, generated_test_id=None, saved_generated_test=None):
    download_urls = _download_urls(config, generated_test_id=generated_test_id)
    return {
        "title": _paper_title(config, saved_generated_test=saved_generated_test),
        "subject": config["selected_subject"],
        "subtopic": config.get("selected_subtopic", ""),
        "source": config["source"],
        "selection_mode": config.get("selection_mode", "adaptive"),
        "duration": config["duration"],
        "test_type": config["test_type"],
        "generated_test_id": generated_test_id,
        "download_urls": download_urls,
        "questions": [
            {
                "id": question.get("id"),
                "subject": question.get("subject"),
                "topic": question.get("topic", "General"),
                "difficulty_level": question.get("difficulty_level", 1),
                "question": question.get("question", ""),
                "marks": question.get("marks", 1),
                "asset_path": question.get("asset_path"),
            }
            for question in questions
        ],
    }


def _serialize_question_paper_token(questions, config, generated_test_id=None, saved_generated_test=None):
    if not questions:
        return None
    payload = _question_paper_payload(
        questions,
        config,
        generated_test_id=generated_test_id,
        saved_generated_test=saved_generated_test,
    )
    return _question_paper_serializer().dumps(payload)


def _paper_answer_gate_key(token):
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"paper_answers:{digest}"


def _paper_answer_gate_state(token):
    return dict(session.get(_paper_answer_gate_key(token), {}))


def _set_paper_answer_gate_state(token, state):
    session[_paper_answer_gate_key(token)] = state
    session.modified = True


def _generate_paper_answer_password():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))


def _display_answer_text(answer_text, answer_asset_path=None):
    text = str(answer_text or "").strip()
    if not text:
        return ""
    if answer_asset_path:
        normalized = " ".join(text.lower().split())
        if normalized in {
            "see the worked mark scheme.",
            "see the worked mark scheme",
            "see worked mark scheme.",
            "see worked mark scheme",
            "see the worked method.",
            "see the worked method",
        }:
            return ""
    return text


def _build_question_answer_map(payload):
    generated_test_id = payload.get("generated_test_id")
    if generated_test_id:
        rows = db.get_generated_test_questions(int(generated_test_id))
    else:
        question_ids = [row.get("id") for row in payload.get("questions", []) if row.get("id") is not None]
        rows = db.get_questions_by_ids(question_ids) if question_ids else []
    return {
        row.get("id"): {
            "answer": _display_answer_text(row.get("answer", ""), row.get("answer_asset_path")),
            "explanation": row.get("explanation", ""),
            "answer_asset_path": row.get("answer_asset_path"),
            "video_url": row.get("video_url"),
        }
        for row in rows
    }


def _attach_answer_reveal_data(questions, payload, answers_unlocked):
    if not answers_unlocked:
        return questions
    answer_map = _build_question_answer_map(payload)
    attached = []
    for question in questions:
        item = dict(question)
        answer_row = answer_map.get(item.get("id"), {})
        item["answer"] = answer_row.get("answer", "")
        item["explanation"] = answer_row.get("explanation", "")
        item["answer_asset_path"] = answer_row.get("answer_asset_path")
        item["answer_asset_url"] = _question_asset_url(item.get("answer_asset_path"))
        item["answer_asset_is_image"] = _is_image_reference(item.get("answer_asset_path"))
        item["video_url"] = answer_row.get("video_url")
        attached.append(item)
    return attached


def _diagram_answer_recommended(question):
    text = str(question.get("question", "")).lower()
    keywords = [
        "draw",
        "sketch",
        "plot",
        "graph",
        "diagram",
        "label",
        "construct",
        "shade",
        "show your working",
    ]
    return bool(question.get("asset_path")) or any(keyword in text for keyword in keywords)


def _attach_question_paper_assets(rows):
    attached = _attach_figure_urls(rows)
    for row in attached:
        row["diagram_answer_recommended"] = _diagram_answer_recommended(row)
    return attached


def _save_uploaded_response(file_storage, prefix):
    original_name = secure_filename(file_storage.filename or "")
    if not original_name:
        return None
    stored_name = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}_{original_name}"
    path = UPLOAD_DIR / stored_name
    file_storage.save(path)
    return {
        "original_name": original_name,
        "stored_name": stored_name,
        "url": url_for("main.view_uploaded_response", filename=stored_name),
    }


def _question_asset_url(asset_path):
    if not asset_path:
        return None
    if isinstance(asset_path, str) and asset_path.startswith(("http://", "https://")):
        return asset_path
    return url_for("static", filename=asset_path)


def _is_image_reference(asset_path):
    if not asset_path:
        return False
    value = str(asset_path).split("?", 1)[0].lower()
    return value.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"))


def _save_question_bank_image(file_storage, prefix):
    original_name = secure_filename(file_storage.filename or "")
    if not original_name:
        return None
    extension = f".{original_name.rsplit('.', 1)[-1].lower()}" if "." in original_name else ""
    if extension not in QUESTION_BANK_IMAGE_EXTENSIONS:
        raise RuntimeError("Use an image file: PNG, JPG, JPEG, WEBP, or GIF.")
    stored_name = f"{prefix}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{extension}"
    file_storage.save(QUESTION_BANK_IMAGE_DIR / stored_name)
    return f"uploads/question_bank/{stored_name}"


def _build_question_paper_submission(payload):
    questions = payload.get("questions", [])
    responses = {}
    answered_count = 0
    uploaded_file_count = 0

    for index, question in enumerate(questions, 1):
        answer_text = request.form.get(f"answer_text_{index}", "").strip()
        response_file = request.files.get(f"answer_file_{index}")
        saved_file = None
        if response_file and response_file.filename:
            saved_file = _save_uploaded_response(response_file, f"paper_q{index}")
            if saved_file:
                uploaded_file_count += 1
        if answer_text:
            answered_count += 1
        if answer_text or saved_file:
            responses[index] = {
                "question": question,
                "answer_text": answer_text,
                "file": saved_file,
            }

    full_scan = None
    scan_file = request.files.get("full_scan")
    if scan_file and scan_file.filename:
        full_scan = _save_uploaded_response(scan_file, "paper_full")
        if full_scan:
            uploaded_file_count += 1

    return {
        "submitted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "answered_count": answered_count,
        "uploaded_file_count": uploaded_file_count,
        "responses": responses,
        "full_scan": full_scan,
    }


def _attach_figure_urls(rows):
    serializer = _figure_serializer()
    attached = []
    for row in rows:
        item = dict(row)
        if item.get("asset_path"):
            item["asset_url"] = _question_asset_url(item["asset_path"])
            item["asset_is_image"] = _is_image_reference(item.get("asset_path"))
        elif question_supports_live_asset(item):
            token = serializer.dumps(_figure_token_payload(item))
            item["asset_url"] = url_for("main.render_question_figure", token=token)
            item["asset_is_image"] = True
        attached.append(item)
    return attached


def _pdf_document_type():
    document = request.args.get("document", "paper").strip().lower()
    return document if document in {"paper", "markscheme"} else "paper"


def parse_int(value, default, minimum=1, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    parsed = max(minimum, parsed)
    if maximum is not None:
        parsed = min(maximum, parsed)
    return parsed


def _subject_topics_map(subjects):
    return {subject: db.get_topics_for_subject(subject) for subject in subjects}


def _normalize_topic_label(value):
    return " ".join(str(value or "").strip().lower().split())


def _matches_any_pattern(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def _question_probability_signal(question):
    text = " ".join(
        [
            str(question.get("topic") or ""),
            str(question.get("subtopic") or ""),
            str(question.get("question") or ""),
        ]
    ).lower()
    probability_patterns = [
        r"\bprobability\b",
        r"\bchance\b",
        r"\blikely\b",
        r"\bunlikely\b",
        r"\brandom\b",
        r"\bspinner\b",
        r"\bdice\b",
        r"\bdie\b",
        r"\bcoin\b",
        r"\bbag contains\b",
        r"\bwithout replacement\b",
        r"\breplacement\b",
        r"\bevent\b",
        r"\boutcome\b",
    ]
    return _matches_any_pattern(text, probability_patterns)


def _question_statistics_signal(question):
    text = " ".join(
        [
            str(question.get("topic") or ""),
            str(question.get("subtopic") or ""),
            str(question.get("question") or ""),
        ]
    ).lower()
    statistics_patterns = [
        r"\bmean\b",
        r"\bmedian\b",
        r"\bmode\b",
        r"\brange\b",
        r"\baverage\b",
        r"\bfrequency\b",
        r"\bdata\b",
        r"\bsurvey\b",
        r"\bchart\b",
        r"\bbar chart\b",
        r"\bpie chart\b",
        r"\bhistogram\b",
        r"\bfrequency table\b",
    ]
    return _matches_any_pattern(text, statistics_patterns)


def _question_matches_selected_subtopic(question, selected_subtopic):
    selected = _normalize_topic_label(selected_subtopic)
    if not selected:
        return True

    topic = _normalize_topic_label(question.get("topic"))
    subtopic = _normalize_topic_label(question.get("subtopic"))
    if selected == "probability":
        return _question_probability_signal(question) and not _question_statistics_signal(question)
    if selected == "statistics":
        return _question_statistics_signal(question) and not _question_probability_signal(question)
    if selected == "statistics and probability":
        return _question_probability_signal(question) or _question_statistics_signal(question) or "statistics and probability" in topic

    if selected in {topic, subtopic}:
        return True
    if selected and ((selected in topic) or (selected in subtopic) or (topic and topic in selected) or (subtopic and subtopic in selected)):
        return True

    return False


def _filter_questions_for_selected_subtopic(question_pool, selected_subtopic):
    if not selected_subtopic:
        return list(question_pool)
    return [question for question in question_pool if _question_matches_selected_subtopic(question, selected_subtopic)]


def _manual_question_row_from_request(default_subject=None):
    return {
        "subject": request.form.get("subject", default_subject or ""),
        "topic": request.form.get("topic", ""),
        "subtopic": request.form.get("subtopic", ""),
        "difficulty_level": request.form.get("difficulty_level", ""),
        "marks": request.form.get("marks", 1),
        "question": request.form.get("question_text", ""),
        "answer": request.form.get("answer_text", ""),
        "explanation": request.form.get("explanation_text", ""),
        "video_url": request.form.get("video_url", ""),
        "asset_path": request.form.get("asset_path", ""),
        "answer_asset_path": request.form.get("answer_asset_path", ""),
    }


def _api_question_payload_rows(payload):
    if isinstance(payload, dict) and isinstance(payload.get("questions"), list):
        return payload["questions"], payload.get("subject")
    if isinstance(payload, list):
        return payload, None
    if isinstance(payload, dict):
        return [payload], payload.get("subject")
    raise RuntimeError("JSON body must be a question object, a list of questions, or an object with a 'questions' list.")


@bp.app_context_processor
def inject_admin_auth_state():
    flagged_topic_alerts = []
    try:
        for row in db.get_flagged_topic_counters():
            item = dict(row)
            item["videos"] = recommend_topic_videos(item["subject"], item["focus_label"])
            flagged_topic_alerts.append(item)
    except Exception:
        flagged_topic_alerts = []
    return {
        "admin_registered": admin_registered(),
        "admin_authenticated": admin_logged_in(),
        "admin_username": current_admin_username(),
        "flagged_topic_alerts": flagged_topic_alerts,
    }


@bp.app_template_filter("math_html")
def math_html_filter(value):
    return render_math_html(value)


def _normalize_answer(answer_text):
    return " ".join(str(answer_text or "").strip().lower().split())


def _question_template_key(question):
    return question_pattern_key(question.get("question"))


def _increment_selection_counters(question, pattern_counts, answer_counts):
    pattern_key = _question_template_key(question)
    answer_key = _normalize_answer(question.get("answer"))
    pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
    if answer_key:
        answer_counts[answer_key] = answer_counts.get(answer_key, 0) + 1


def _choose_diverse_questions(primary_questions, fallback_pool, target_count):
    selected = []
    used_ids = set()
    used_answers = set()
    pattern_counts = {}
    topic_counts = {}

    def add_from_pool(pool, prefer_unique_answers, pattern_limit=None, prefer_topic_balance=False):
        topic_limit = None
        if prefer_topic_balance:
            topic_total = max(1, len({q.get('topic', 'General') for q in pool}))
            topic_limit = max(1, round(target_count / topic_total)) + 1
        for question in pool:
            if len(selected) >= target_count:
                break
            question_id = question.get("id")
            answer_key = _normalize_answer(question.get("answer"))
            pattern_key = question_pattern_key(question.get("question"))
            topic_key = question.get("topic", "General")
            if question_id in used_ids:
                continue
            if prefer_unique_answers and answer_key and answer_key in used_answers:
                continue
            if pattern_limit is not None and pattern_counts.get(pattern_key, 0) >= pattern_limit:
                continue
            if topic_limit is not None and topic_counts.get(topic_key, 0) >= topic_limit:
                continue
            selected.append(question)
            if question_id is not None:
                used_ids.add(question_id)
            if answer_key:
                used_answers.add(answer_key)
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1

    add_from_pool(primary_questions, prefer_unique_answers=True, pattern_limit=1, prefer_topic_balance=True)
    add_from_pool(fallback_pool, prefer_unique_answers=True, pattern_limit=1, prefer_topic_balance=True)
    add_from_pool(primary_questions, prefer_unique_answers=True, pattern_limit=2, prefer_topic_balance=True)
    add_from_pool(fallback_pool, prefer_unique_answers=True, pattern_limit=2, prefer_topic_balance=True)
    add_from_pool(primary_questions, prefer_unique_answers=False, pattern_limit=2, prefer_topic_balance=False)
    add_from_pool(fallback_pool, prefer_unique_answers=False, pattern_limit=2, prefer_topic_balance=False)
    add_from_pool(primary_questions, prefer_unique_answers=False, pattern_limit=None, prefer_topic_balance=False)
    add_from_pool(fallback_pool, prefer_unique_answers=False, pattern_limit=None, prefer_topic_balance=False)
    return selected[:target_count]


def build_local_all_subjects_test(subjects, per_subject=1):
    questions = []
    for subject in subjects:
        questions.extend(db.get_adaptive_questions(subject, max_questions=per_subject))
    return questions


def build_local_all_subjects_diagram_test(subjects, per_subject=1):
    questions = []
    for subject in subjects:
        subject_pool = _diagram_only_pool(db.get_questions_for_subject(subject))
        if not subject_pool:
            continue
        attempts = db.get_recent_attempts_for_subject(subject)
        questions.extend(
            choose_adaptive_questions(
                subject_pool,
                attempts,
                max_questions=per_subject,
                allow_random_repeat=db.get_settings()["allow_random_repeat"],
            )
        )
    return questions


def _duration_question_goal(duration):
    return max(MIN_TEST_QUESTION_COUNT, min(24, round(duration / 5)))


def _duration_mark_goal(duration):
    return max(10, min(120, round(duration * 1.8)))


def _question_pick_key(question, attempted_ids, recent_ids, target_difficulty=None):
    difficulty_level = question.get("difficulty_level", 1)
    return (
        question.get("id") in recent_ids,
        question.get("id") in attempted_ids,
        abs(difficulty_level - target_difficulty) if target_difficulty is not None else 0,
        -source_priority(question),
        -question.get("marks", 1),
        difficulty_level,
        question.get("id", 0),
    )


def _score_ratio(attempt_row):
    max_score = float(attempt_row.get("max_score") or 0)
    if max_score <= 0:
        return 0.0
    return float(attempt_row.get("score") or 0) / max_score


def _paper_difficulty_sequence(target_count):
    target_count = max(MIN_TEST_QUESTION_COUNT, target_count)
    sequence = list(DEFAULT_PAPER_DIFFICULTY_SEQUENCE)
    extension = [4, 3, 5, 3, 4, 5, 2, 4, 5, 3]
    while len(sequence) < target_count:
        sequence.append(extension[(len(sequence) - len(DEFAULT_PAPER_DIFFICULTY_SEQUENCE)) % len(extension)])
    return sequence[:target_count]


def _composed_question_key(question, desired_difficulty, attempted_ids, recent_ids, preferred_topic=None):
    difficulty_level = question.get("difficulty_level", 1)
    return (
        abs(difficulty_level - desired_difficulty),
        question.get("topic") != preferred_topic if preferred_topic else False,
        question.get("id") in recent_ids,
        question.get("id") in attempted_ids,
        -source_priority(question),
        -question.get("marks", 1),
        -difficulty_level,
        question.get("topic", ""),
        question.get("id", 0),
    )


def _very_hard_struggle_counts(attempts):
    counts = {}
    for row in attempts:
        if int(row.get("difficulty_level", 1) or 1) < 5:
            continue
        if _score_ratio(row) >= 0.5:
            continue
        question_id = row.get("question_id")
        if question_id is None:
            continue
        counts[question_id] = counts.get(question_id, 0) + 1
    return counts


def _move_struggled_very_hard_questions_earlier(questions, attempts):
    result = list(questions)
    struggle_counts = _very_hard_struggle_counts(attempts)
    if not struggle_counts:
        return result

    for question in list(result):
        question_id = question.get("id")
        if question_id is None:
            continue
        moves = struggle_counts.get(question_id, 0)
        if moves <= 0 or int(question.get("difficulty_level", 1) or 1) < 5:
            continue
        current_index = next((index for index, row in enumerate(result) if row.get("id") == question_id), None)
        if current_index is None:
            continue
        for _ in range(moves):
            if current_index <= 0:
                break
            result[current_index - 1], result[current_index] = result[current_index], result[current_index - 1]
            current_index -= 1
    return result


def _is_displayable_diagram_question(question):
    asset_path = str(question.get("asset_path") or "").strip()
    if asset_path:
        return True
    return question_supports_live_asset(question)


def _diagram_only_pool(question_pool, preferred_topic=None):
    if preferred_topic:
        return [
            row for row in question_pool
            if _question_matches_selected_subtopic(row, preferred_topic) and _is_displayable_diagram_question(row)
        ]
    return [row for row in question_pool if _is_displayable_diagram_question(row)]


def _diagram_band(question):
    if not _is_displayable_diagram_question(question):
        return None
    difficulty_level = int(question.get("difficulty_level", 1) or 1)
    if difficulty_level >= 4:
        return "hard"
    if difficulty_level == 3:
        return "moderate"
    return None


def _diagram_quota_count(target_count, percentage, available_count):
    if available_count <= 0:
        return 0
    quota = round(target_count * percentage)
    if quota <= 0 and target_count >= MIN_TEST_QUESTION_COUNT:
        quota = 1
    return min(available_count, quota)


def _diagram_quota_targets(question_pool, target_count, preferred_topic=None):
    scoped_pool = [
        row for row in question_pool
        if not preferred_topic or _question_matches_selected_subtopic(row, preferred_topic)
    ]
    hard_available = sum(1 for row in scoped_pool if _diagram_band(row) == "hard")
    moderate_available = sum(1 for row in scoped_pool if _diagram_band(row) == "moderate")
    return {
        "hard": _diagram_quota_count(target_count, 0.15, hard_available),
        "moderate": _diagram_quota_count(target_count, 0.10, moderate_available),
    }


def _pick_best_composed_candidate(
    available,
    desired_difficulty,
    attempted_ids,
    recent_ids,
    preferred_topic=None,
    required_diagram_band=None,
    pattern_counts=None,
    answer_counts=None,
):
    candidates = list(available)
    if preferred_topic:
        preferred_candidates = [row for row in candidates if _question_matches_selected_subtopic(row, preferred_topic)]
        if preferred_candidates:
            candidates = preferred_candidates
    if required_diagram_band:
        diagram_candidates = [row for row in candidates if _diagram_band(row) == required_diagram_band]
        if diagram_candidates:
            candidates = diagram_candidates
        else:
            return None
    if not candidates:
        return None
    random.shuffle(candidates)

    def selection_key(row):
        difficulty_level = row.get("difficulty_level", 1)
        return (
            (pattern_counts or {}).get(_question_template_key(row), 0),
            (answer_counts or {}).get(_normalize_answer(row.get("answer")), 0),
            abs(difficulty_level - desired_difficulty),
            row.get("topic") != preferred_topic if preferred_topic else False,
            row.get("id") in recent_ids,
            row.get("id") in attempted_ids,
            -source_priority(row),
            -row.get("marks", 1),
            -difficulty_level,
        )

    ranked = sorted(candidates, key=selection_key)
    best_key = selection_key(ranked[0])
    best_candidates = [row for row in ranked if selection_key(row) == best_key]
    return random.choice(best_candidates)


def build_composed_subject_questions(subject, question_pool, target_count=MIN_TEST_QUESTION_COUNT, preferred_topic=None):
    if not question_pool:
        return []

    target_count = max(MIN_TEST_QUESTION_COUNT, int(target_count or MIN_TEST_QUESTION_COUNT))
    attempts = db.get_recent_attempts_for_subject(subject)
    attempted_ids = {row["question_id"] for row in attempts}
    recent_ids = {row["question_id"] for row in sorted(attempts, key=lambda row: row["taken_at"], reverse=True)[:20]}
    sequence = _paper_difficulty_sequence(target_count)
    required_counts = {difficulty: sequence.count(difficulty) for difficulty in sorted(set(sequence), reverse=True)}
    used_ids = set()
    chosen_by_difficulty = {}
    remaining_diagram_targets = _diagram_quota_targets(question_pool, target_count, preferred_topic=preferred_topic)
    pattern_counts = {}
    answer_counts = {}

    for desired_difficulty, needed_count in required_counts.items():
        chosen = []
        for _ in range(needed_count):
            available = [row for row in question_pool if row.get("id") not in used_ids]
            required_diagram_band = None
            if desired_difficulty >= 4 and remaining_diagram_targets["hard"] > 0:
                required_diagram_band = "hard"
            elif desired_difficulty == 3 and remaining_diagram_targets["moderate"] > 0:
                required_diagram_band = "moderate"

            row = _pick_best_composed_candidate(
                available,
                desired_difficulty,
                attempted_ids,
                recent_ids,
                preferred_topic=preferred_topic,
                required_diagram_band=required_diagram_band,
                pattern_counts=pattern_counts,
                answer_counts=answer_counts,
            )
            if row is None:
                row = _pick_best_composed_candidate(
                    available,
                    desired_difficulty,
                    attempted_ids,
                    recent_ids,
                    preferred_topic=preferred_topic,
                    pattern_counts=pattern_counts,
                    answer_counts=answer_counts,
                )
            if row is None:
                break
            chosen.append(row)
            if required_diagram_band and _diagram_band(row) == required_diagram_band:
                remaining_diagram_targets[required_diagram_band] = max(
                    0,
                    remaining_diagram_targets[required_diagram_band] - 1,
                )
            if row.get("id") is not None:
                used_ids.add(row["id"])
            _increment_selection_counters(row, pattern_counts, answer_counts)
        chosen_by_difficulty[desired_difficulty] = chosen

    final_questions = []
    for desired_difficulty in sequence:
        bucket = chosen_by_difficulty.get(desired_difficulty, [])
        if bucket:
            final_questions.append(bucket.pop(0))
        else:
            final_questions.append(None)

    for index, row in enumerate(final_questions):
        if row is None:
            remaining = [candidate for candidate in question_pool if candidate.get("id") not in used_ids]
            replacement = _pick_best_composed_candidate(
                remaining,
                sequence[index],
                attempted_ids,
                recent_ids,
                preferred_topic=preferred_topic,
                pattern_counts=pattern_counts,
                answer_counts=answer_counts,
            )
            if replacement is not None:
                final_questions[index] = replacement
                if replacement.get("id") is not None:
                    used_ids.add(replacement["id"])
                _increment_selection_counters(replacement, pattern_counts, answer_counts)

    final_questions = [row for row in final_questions if row is not None][:target_count]
    if len(final_questions) < target_count:
        used_final_ids = {item.get("id") for item in final_questions if item.get("id") is not None}
        while len(final_questions) < target_count:
            top_up_pool = [row for row in question_pool if row.get("id") not in used_final_ids]
            row = _pick_best_composed_candidate(
                top_up_pool,
                4,
                attempted_ids,
                recent_ids,
                preferred_topic=preferred_topic,
                pattern_counts=pattern_counts,
                answer_counts=answer_counts,
            )
            if row is None:
                break
            final_questions.append(row)
            if row.get("id") is not None:
                used_final_ids.add(row["id"])
            _increment_selection_counters(row, pattern_counts, answer_counts)

    return _move_struggled_very_hard_questions_earlier(final_questions[:target_count], attempts)


def build_duration_balanced_questions(subject, duration):
    subject_questions = db.get_questions_for_subject(subject)
    if not subject_questions:
        return []

    attempts = db.get_recent_attempts_for_subject(subject)
    progress = db.get_subject_progress(subject)
    target_marks = _duration_mark_goal(duration)
    target_count = _duration_question_goal(duration)
    attempted_ids = {row["question_id"] for row in attempts}
    recent_ids = {row["question_id"] for row in sorted(attempts, key=lambda row: row["taken_at"], reverse=True)[:20]}
    by_topic = {}
    for question in subject_questions:
        by_topic.setdefault(question["topic"], []).append(question)

    topic_rows = progress.get("topics", [])
    topic_order = [row["topic"] for row in topic_rows] or sorted(by_topic)
    random.shuffle(topic_order)
    target_difficulty_by_topic = {row["topic"]: row["target_difficulty"] for row in topic_rows}
    selected = []
    used_ids = set()
    total_marks = 0

    for topic in topic_order:
        topic_questions = [question for question in by_topic.get(topic, []) if question.get("id") not in used_ids]
        if not topic_questions:
            continue
        picked = sorted(
            topic_questions,
            key=lambda row: _question_pick_key(row, attempted_ids, recent_ids, target_difficulty_by_topic.get(topic)),
        )[0]
        selected.append(picked)
        used_ids.add(picked["id"])
        total_marks += picked.get("marks", 1)
        if len(selected) >= target_count and total_marks >= target_marks:
            break

    remaining = [question for question in subject_questions if question.get("id") not in used_ids]
    random.shuffle(remaining)
    remaining.sort(
        key=lambda row: _question_pick_key(
            row,
            attempted_ids,
            recent_ids,
            target_difficulty_by_topic.get(row.get("topic")),
        )
    )
    for question in remaining:
        if len(selected) >= target_count and total_marks >= target_marks:
            break
        selected.append(question)
        used_ids.add(question["id"])
        total_marks += question.get("marks", 1)

    return selected


def get_test_configuration(values, subjects=None):
    active_subjects = subjects or get_active_subjects()
    test_type = values.get("test_type", "subject_mini")
    selected_subject = values.get("subject", active_subjects[0] if active_subjects else SUBJECTS[0])
    if selected_subject not in active_subjects and active_subjects:
        selected_subject = active_subjects[0]
    selected_subtopic = values.get("subtopic", "").strip()
    source = values.get("source", "local")
    selection_mode = values.get("selection_mode", "adaptive")
    if selection_mode not in {"adaptive", "randomize"}:
        selection_mode = "adaptive"
    duration_default = 10 if test_type == "daily_all" else 30
    duration = parse_int(values.get("duration", duration_default), default=duration_default, minimum=5, maximum=120)
    default_question_count = max(MIN_TEST_QUESTION_COUNT, len(active_subjects)) if test_type == "daily_all" else MIN_TEST_QUESTION_COUNT
    question_count = parse_int(
        values.get("count", default_question_count),
        default=default_question_count,
        minimum=MIN_TEST_QUESTION_COUNT,
        maximum=30,
    )
    delivery_action = values.get("delivery_action", "screen").strip().lower()
    if delivery_action not in {"screen", "paper_pdf", "markscheme_pdf", "markdown"}:
        delivery_action = "screen"
    diagram_only = str(values.get("diagram_only", "")).strip().lower() in {"1", "true", "on", "yes"}
    return {
        "test_type": test_type,
        "selected_subject": selected_subject,
        "selected_subtopic": selected_subtopic,
        "source": source,
        "selection_mode": selection_mode,
        "duration": duration,
        "question_count": question_count,
        "delivery_action": delivery_action,
        "diagram_only": diagram_only,
    }


def build_low_score_suggestion_map(subjects):
    suggestion_map = {}
    for subject in subjects:
        suggestion_map[subject] = [
            {
                "id": row["id"],
                "title": row["title"],
                "subtopic": row.get("subtopic") or "",
                "duration_minutes": row["duration_minutes"],
                "score_text": f"{int(float(row['score']))}/{int(float(row['max_score']))}",
                "score_percent": round((float(row["score"]) / float(row["max_score"])) * 100) if float(row["max_score"]) else 0,
                "created_at": row["created_at"],
                "taken_at": row["taken_at"],
                "view_url": url_for("main.view_saved_generated_test", test_id=row["id"]),
                "pdf_url": url_for("main.download_saved_generated_test", test_id=row["id"], format="pdf"),
            }
            for row in db.get_low_score_generated_tests(subject)
        ]
    return suggestion_map


def _empty_progress():
    return {"subject_score": 0, "topics": [], "next_focus": None, "question_total": 0}


def build_test_page_context(
    *,
    subjects,
    config,
    generated,
    review_items=None,
    generated_test_id=None,
    saved_generated_test=None,
):
    selected_subject = config["selected_subject"]
    progress = generated.get("progress") or _empty_progress()
    raw_questions = generated.get("questions", [])
    questions = _attach_figure_urls(raw_questions)
    download_urls = _download_urls(config, generated_test_id=generated_test_id)
    question_paper_token = _serialize_question_paper_token(
        raw_questions,
        config,
        generated_test_id=generated_test_id,
        saved_generated_test=saved_generated_test,
    )
    review_rows = []
    for item in review_items or []:
        review_row = dict(item)
        if review_row.get("asset_path"):
            review_row["asset_url"] = _question_asset_url(review_row["asset_path"])
            review_row["asset_is_image"] = _is_image_reference(review_row.get("asset_path"))
        elif question_supports_live_asset(review_row):
            token = _figure_serializer().dumps(_figure_token_payload(review_row))
            review_row["asset_url"] = url_for("main.render_question_figure", token=token)
            review_row["asset_is_image"] = True
        if review_row.get("answer_asset_path"):
            review_row["answer_asset_url"] = _question_asset_url(review_row["answer_asset_path"])
            review_row["answer_asset_is_image"] = _is_image_reference(review_row.get("answer_asset_path"))
        review_rows.append(review_row)
    return {
        "subjects": subjects,
        "selected_subject": selected_subject,
        "selected_subtopic": config.get("selected_subtopic", ""),
        "subtopics": db.get_topics_for_subject(selected_subject),
        "subject_subtopics_map": {subject: db.get_topics_for_subject(subject) for subject in subjects},
        "question_count": config["question_count"],
        "questions": questions,
        "progress": progress,
        "review_items": review_rows,
        "test_markdown": generated.get("markdown", ""),
        "test_type": config["test_type"],
        "source": config["source"],
        "selection_mode": config.get("selection_mode", "adaptive"),
        "diagram_only": config.get("diagram_only", False),
        "duration": config["duration"],
        "delivery_action": config.get("delivery_action", "screen"),
        "openai_enabled": openai_available(),
        "generated_test_id": generated_test_id,
        "saved_generated_test": saved_generated_test,
        "subject_suggestion_map": build_low_score_suggestion_map(subjects),
        "download_md_url": download_urls["download_md_url"],
        "download_pdf_url": download_urls["download_pdf_url"],
        "download_mark_scheme_pdf_url": download_urls["download_mark_scheme_pdf_url"],
        "question_paper_token": question_paper_token,
    }


def generate_test_content(config, subjects, persist_openai=False):
    analysis = get_analysis()
    questions = []
    markdown = ""
    title_subject = None
    saved_generated_test = None
    progress = db.get_subject_progress(config["selected_subject"]) if config["selected_subject"] else _empty_progress()
    selected_subtopic = config.get("selected_subtopic", "")
    diagram_only = bool(config.get("diagram_only"))

    if config["source"] == "openai":
        if diagram_only:
            raise RuntimeError("Diagram-only papers are available only from the local question bank.")
        if config["test_type"] == "daily_all":
            questions = generate_ai_mixed_test_payload(
                subjects,
                analysis["priority_subjects"],
                minutes=config["duration"],
                question_target=config["question_count"],
            )
            markdown = format_test_markdown(questions, duration_minutes=config["duration"]) if questions else ""
            title_subject = "Mixed"
            paper_subject = "Mixed"
        else:
            weak_topics = [selected_subtopic] if selected_subtopic else [item["topic"] for item in progress.get("topics", [])[:3]]
            questions = generate_ai_subject_test_payload(
                config["selected_subject"],
                weak_topics=weak_topics,
                minutes=config["duration"],
                question_target=config["question_count"],
                available_topics=db.get_topics_for_subject(config["selected_subject"]),
                randomize_topics=config["selection_mode"] == "randomize" and not selected_subtopic,
            )
            markdown = format_test_markdown(
                questions,
                title_subject=config["selected_subject"],
                duration_minutes=config["duration"],
            ) if questions else ""
            title_subject = config["selected_subject"]
            paper_subject = config["selected_subject"]
        if persist_openai and questions:
            saved_generated_test = db.save_generated_test(
                source="openai",
                test_type=config["test_type"],
                subject=paper_subject,
                subtopic=selected_subtopic,
                duration_minutes=config["duration"],
                selection_mode=config["selection_mode"],
                title=f"GCSE Grade 9 {title_subject or 'Mixed'} Test",
                markdown_text=markdown,
                questions=questions,
            )
            questions = db.get_generated_test_questions(saved_generated_test["id"])
    else:
        if config["test_type"] == "daily_all":
            per_subject = max(1, config["question_count"] // max(1, len(subjects)))
            if diagram_only:
                questions = build_local_all_subjects_diagram_test(subjects, per_subject=per_subject)
            else:
                questions = build_local_all_subjects_test(subjects, per_subject=per_subject)
            questions = enrich_questions_with_dynamic_assets(questions)
            markdown = format_test_markdown(questions, duration_minutes=config["duration"])
        else:
            subject_questions = db.get_questions_for_subject(config["selected_subject"])
            target_count = max(config["question_count"], _duration_question_goal(config["duration"]))
            if selected_subtopic:
                paper_pool = _filter_questions_for_selected_subtopic(subject_questions, selected_subtopic)
            else:
                paper_pool = subject_questions
            if diagram_only:
                paper_pool = _diagram_only_pool(paper_pool, preferred_topic=selected_subtopic or None)
            questions = build_composed_subject_questions(
                config["selected_subject"],
                paper_pool,
                target_count=target_count,
                preferred_topic=selected_subtopic or None,
            )
            questions = enrich_questions_with_dynamic_assets(questions)
            markdown = format_test_markdown(
                questions,
                title_subject=config["selected_subject"],
                duration_minutes=config["duration"],
            ) if questions else ""
            title_subject = config["selected_subject"]

    return {
        "analysis": analysis,
        "questions": questions,
        "markdown": markdown,
        "title_subject": title_subject,
        "progress": progress,
        "saved_generated_test": saved_generated_test,
    }


@bp.route("/")
def index():
    analysis = get_analysis()
    day_name, next_iso = next_day_name()
    timetable = generate_next_day_timetable(analysis, day_name)
    weekend = generate_weekend_plan(analysis)
    resources = recommend_resources(analysis["priority_subjects"])
    settings = db.get_settings()
    startup_refresh = current_app.config.get("LAST_STARTUP_REFRESH")
    return render_template(
        "dashboard.html",
        analysis=analysis,
        timetable=timetable,
        weekend=weekend,
        resources=resources,
        day_name=day_name,
        next_iso=next_iso,
        settings=settings,
        startup_refresh=startup_refresh,
    )


@bp.route("/settings/question-delivery", methods=["POST"])
def update_question_delivery_settings():
    allow_random_repeat = "allow_random_repeat" in request.form
    startup_refresh_enabled = "startup_refresh_enabled" in request.form
    refresh_target = parse_int(request.form.get("startup_refresh_target", 8), default=8, minimum=1, maximum=30)

    db.set_setting("allow_random_repeat", "1" if allow_random_repeat else "0")
    db.set_setting("startup_refresh_enabled", "1" if startup_refresh_enabled else "0")
    db.set_setting("startup_refresh_target", str(refresh_target))
    flash("Question delivery settings updated.", "success")
    return redirect(url_for("main.index"))


@bp.route("/log", methods=["GET", "POST"])
def log_day():
    subjects = get_active_subjects()
    if request.method == "POST":
        try:
            data = {
                "log_date": request.form.get("log_date", date.today().isoformat()),
                "sleep_hours": float(request.form.get("sleep_hours", 8)),
                "energy": int(request.form.get("energy", 3)),
                "focus": int(request.form.get("focus", 3)),
                "mood": request.form.get("mood", ""),
                "homework_minutes": int(request.form.get("homework_minutes", 45)),
                "revision_minutes": int(request.form.get("revision_minutes", 30)),
                "reading_minutes": int(request.form.get("reading_minutes", 15)),
                "exercise_minutes": int(request.form.get("exercise_minutes", 20)),
                "distractions_minutes": int(request.form.get("distractions_minutes", 30)),
                "notes": request.form.get("notes", ""),
            }
            db.upsert_daily_log(data)

            for subject in subjects:
                safe = subject.replace(" ", "_").replace("/", "_")
                score_text = request.form.get(f"score_{safe}", "").strip()
                db.upsert_subject_log({
                    "log_date": data["log_date"],
                    "subject": subject,
                    "study_minutes": int(request.form.get(f"mins_{safe}", 0)),
                    "confidence": int(request.form.get(f"conf_{safe}", 3)),
                    "test_score": int(score_text) if score_text else None,
                    "problem_notes": request.form.get(f"notes_{safe}", ""),
                })
            flash("Daily log saved.", "success")
            return redirect(url_for("main.index"))
        except Exception as exc:
            flash(str(exc), "error")

    return render_template("log.html", subjects=subjects, today=date.today().isoformat())


@bp.route("/test", methods=["GET", "POST"])
def test_page():
    subjects = get_testing_subjects()
    config = get_test_configuration(request.values, subjects=subjects)
    generated = {
        "questions": [],
        "markdown": "",
        "title_subject": None,
        "progress": db.get_subject_progress(config["selected_subject"]) if config["selected_subject"] else _empty_progress(),
    }
    review_items = []
    generated_test_id = None
    saved_generated_test = None

    if request.method == "POST":
        if config["delivery_action"] == "paper_pdf":
            return redirect(url_for(
                "main.download_test",
                test_type=config["test_type"],
                subject=config["selected_subject"],
                subtopic=config["selected_subtopic"],
                source=config["source"],
                selection_mode=config["selection_mode"],
                diagram_only="1" if config.get("diagram_only") else "0",
                duration=config["duration"],
                count=config["question_count"],
                format="pdf",
                document="paper",
            ))
        if config["delivery_action"] == "markscheme_pdf":
            return redirect(url_for(
                "main.download_test",
                test_type=config["test_type"],
                subject=config["selected_subject"],
                subtopic=config["selected_subtopic"],
                source=config["source"],
                selection_mode=config["selection_mode"],
                diagram_only="1" if config.get("diagram_only") else "0",
                duration=config["duration"],
                count=config["question_count"],
                format="pdf",
                document="markscheme",
            ))
        if config["delivery_action"] == "markdown":
            return redirect(url_for(
                "main.download_test",
                test_type=config["test_type"],
                subject=config["selected_subject"],
                subtopic=config["selected_subtopic"],
                source=config["source"],
                selection_mode=config["selection_mode"],
                diagram_only="1" if config.get("diagram_only") else "0",
                duration=config["duration"],
                count=config["question_count"],
                format="md",
            ))

    if request.method == "POST" or request.args.get("generate") == "1":
        try:
            generated = generate_test_content(
                config,
                subjects=subjects,
                persist_openai=request.method == "POST" and config["source"] == "openai",
            )
            saved_generated_test = generated.get("saved_generated_test")
            generated_test_id = saved_generated_test["id"] if saved_generated_test else None
            if config["source"] == "local" and config["test_type"] == "subject_mini" and not generated["questions"]:
                if config.get("diagram_only") and config["selected_subtopic"]:
                    flash(
                        f"No displayable diagram questions are stored for {config['selected_subject']} in subtopic {config['selected_subtopic']}.",
                        "error",
                    )
                elif config.get("diagram_only"):
                    flash(
                        f"No displayable diagram questions are stored for {config['selected_subject']}.",
                        "error",
                    )
                elif config["selected_subtopic"]:
                    flash(f"No questions stored for {config['selected_subject']} in subtopic {config['selected_subtopic']}.", "error")
                else:
                    flash(f"No questions stored for {config['selected_subject']}. Import some first.", "error")
            elif config["source"] == "openai" and generated_test_id:
                flash("AI test generated, saved locally, and ready to download as PDF.", "success")
        except Exception as exc:
            flash(f"Test generation failed: {exc}", "error")

    return render_template("test.html", **build_test_page_context(
        subjects=subjects,
        config=config,
        generated=generated,
        review_items=review_items,
        generated_test_id=generated_test_id,
        saved_generated_test=saved_generated_test,
    ))


@bp.route("/test/submit", methods=["POST"])
def submit_test_results():
    subjects = get_testing_subjects()
    subject = request.form.get("subject", subjects[0] if subjects else SUBJECTS[0])
    generated_test_id = request.form.get("generated_test_id", "").strip()
    question_ids = request.form.getlist("question_id")
    scores = request.form.getlist("score")
    results = []
    for question_id, score in zip(question_ids, scores):
        if not question_id:
            continue
        try:
            numeric_score = float(score or 0)
        except ValueError:
            numeric_score = 0
        results.append({"question_id": int(question_id), "score": numeric_score})

    if generated_test_id:
        saved_generated_test = db.get_generated_test(int(generated_test_id))
        attempt = db.record_generated_test_results(int(generated_test_id), results)
        if not attempt or not saved_generated_test:
            flash("No AI test results were recorded.", "error")
            return redirect(url_for("main.test_page", subject=subject, test_type="subject_mini", source="openai", generate="1"))

        flash(
            f"Recorded {int(attempt['score'])}/{int(attempt['max_score'])} for the saved AI paper in {subject}.",
            "success",
        )
        questions = db.get_generated_test_questions(int(generated_test_id))
        question_map = {row["id"]: row for row in questions}
        ordered_questions = [question_map[row["question_id"]] for row in results if row["question_id"] in question_map]
        score_map = {row["question_id"]: row for row in results}
        review_items = build_wrong_answer_review(subject, ordered_questions, score_map)
        generated = {
            "questions": ordered_questions,
            "markdown": saved_generated_test["markdown_text"],
            "title_subject": saved_generated_test["subject"],
            "progress": db.get_subject_progress(subject),
        }
        config = {
            "test_type": saved_generated_test["test_type"],
            "selected_subject": subject,
            "selected_subtopic": saved_generated_test.get("subtopic") or "",
            "source": "openai",
            "selection_mode": saved_generated_test.get("selection_mode", "adaptive"),
            "duration": saved_generated_test["duration_minutes"],
            "question_count": len(ordered_questions) or _duration_question_goal(saved_generated_test["duration_minutes"]),
        }
        return render_template("test.html", **build_test_page_context(
            subjects=subjects,
            config=config,
            generated=generated,
            review_items=review_items,
            generated_test_id=int(generated_test_id),
            saved_generated_test=saved_generated_test,
        ))

    recorded = db.record_test_results(subject, results)
    if not recorded:
        flash("No test results were recorded.", "error")
        return redirect(url_for("main.test_page", subject=subject, test_type="subject_mini", source="local", generate="1"))

    flash(f"Recorded {recorded} results for {subject}. The next test will adapt to those marks.", "success")
    questions = db.get_questions_by_ids([row["question_id"] for row in results])
    questions = enrich_questions_with_dynamic_assets(questions)
    question_map = {row["id"]: row for row in questions}
    ordered_questions = [question_map[row["question_id"]] for row in results if row["question_id"] in question_map]
    score_map = {row["question_id"]: row for row in results}
    review_items = build_wrong_answer_review(subject, ordered_questions, score_map)
    generated = {
        "questions": ordered_questions,
        "markdown": format_test_markdown(ordered_questions, title_subject=subject, duration_minutes=30) if ordered_questions else "",
        "title_subject": subject,
        "progress": db.get_subject_progress(subject),
    }
    config = {
        "test_type": "subject_mini",
        "selected_subject": subject,
        "selected_subtopic": "",
        "source": "local",
        "selection_mode": "adaptive",
        "duration": 30,
        "question_count": len(ordered_questions) or 5,
    }
    return render_template("test.html", **build_test_page_context(
        subjects=subjects,
        config=config,
        generated=generated,
        review_items=review_items,
    ))


@bp.route("/download-test")
def download_test():
    subjects = get_testing_subjects()
    config = get_test_configuration(request.args, subjects=subjects)
    generated = generate_test_content(config, subjects=subjects)
    markdown = generated["markdown"]
    export_format = request.args.get("format", "md").lower()
    document_type = _pdf_document_type()
    filename_subject = secure_filename(config["selected_subject"]).lower() or "subject"
    if config["test_type"] == "daily_all":
        filename_root = f"gcse_daily_all_test_{date.today().isoformat()}"
    else:
        filename_root = f"gcse_{filename_subject}_test_{date.today().isoformat()}"

    if export_format == "pdf":
        title = generated["title_subject"] or "GCSE Grade 9 Test"
        questions = generated["questions"]
        if not questions:
            flash("PDF export needs generated questions. Generate the test again first.", "error")
            return redirect(url_for("main.test_page", **config, generate="1"))
        if document_type == "markscheme":
            flash("Mark scheme download is blocked. Use the question paper's password-gated Show answers flow.", "error")
            return redirect(url_for("main.test_page", **config, generate="1"))
        pdf_bytes = build_test_pdf(questions, f"GCSE Grade 9 {title}")
        filename = f"{filename_root}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    return Response(
        markdown,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename_root}.md"},
    )


@bp.route("/question-figure")
def render_question_figure():
    token = request.args.get("token", "").strip()
    if not token:
        return Response("Missing figure token.", status=400)
    try:
        payload = _figure_serializer().loads(token)
    except BadSignature:
        return Response("Invalid figure token.", status=400)

    image_bytes = render_asset_png_bytes(payload)
    if image_bytes is None:
        return Response("Figure unavailable.", status=404)
    return Response(image_bytes, mimetype="image/png")


@bp.route("/download-saved-test/<int:test_id>")
def download_saved_generated_test(test_id):
    saved_test = db.get_generated_test(test_id)
    if not saved_test:
        flash("Saved AI paper not found.", "error")
        return redirect(url_for("main.test_page"))

    questions = db.get_generated_test_questions(test_id)
    export_format = request.args.get("format", "pdf").lower()
    document_type = _pdf_document_type()
    filename_subject = secure_filename(saved_test["subject"]).lower() or "subject"
    filename_root = f"gcse_{filename_subject}_saved_test_{test_id}"
    if export_format == "pdf":
        if document_type == "markscheme":
            flash("Mark scheme download is blocked. Use the question paper's password-gated Show answers flow.", "error")
            return redirect(url_for("main.view_saved_generated_test", test_id=test_id))
        pdf_bytes = build_test_pdf(questions, saved_test["title"])
        filename = f"{filename_root}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    return Response(
        saved_test["markdown_text"],
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename_root}.md"},
    )


@bp.route("/saved-test/<int:test_id>")
def view_saved_generated_test(test_id):
    subjects = get_testing_subjects()
    saved_test = db.get_generated_test(test_id)
    if not saved_test:
        flash("Saved AI paper not found.", "error")
        return redirect(url_for("main.test_page"))

    selected_subject = saved_test["subject"] if saved_test["subject"] in subjects else (subjects[0] if subjects else SUBJECTS[0])
    questions = db.get_generated_test_questions(test_id)
    generated = {
        "questions": questions,
        "markdown": saved_test["markdown_text"],
        "title_subject": saved_test["subject"],
        "progress": db.get_subject_progress(selected_subject) if selected_subject != "Mixed" else _empty_progress(),
    }
    config = {
        "test_type": saved_test["test_type"],
        "selected_subject": selected_subject,
        "selected_subtopic": saved_test.get("subtopic") or "",
        "source": "openai",
        "selection_mode": saved_test.get("selection_mode", "adaptive"),
        "duration": saved_test["duration_minutes"],
        "question_count": len(questions) or _duration_question_goal(saved_test["duration_minutes"]),
    }
    return render_template("test.html", **build_test_page_context(
        subjects=subjects,
        config=config,
        generated=generated,
        generated_test_id=test_id,
        saved_generated_test=saved_test,
    ))


@bp.route("/question-paper", methods=["POST"])
def open_question_paper():
    token = request.form.get("paper_token", "").strip()
    if not token:
        flash("Question paper link is missing its payload.", "error")
        return redirect(url_for("main.test_page"))
    try:
        payload = _question_paper_serializer().loads(token)
    except BadSignature:
        flash("Question paper link has expired or is invalid.", "error")
        return redirect(url_for("main.test_page"))

    answer_gate = _paper_answer_gate_state(token)
    action = request.form.get("action", "").strip()
    submission = None
    if action == "submit-responses":
        submission = _build_question_paper_submission(payload)
    elif action == "generate-answer-password":
        password = _generate_paper_answer_password()
        answer_gate = {"password": password, "revealed": False}
        _set_paper_answer_gate_state(token, answer_gate)
        flash("Answer password generated. Send this password to the student before revealing answers.", "success")
    elif action == "unlock-answers":
        expected_password = answer_gate.get("password", "")
        provided_password = request.form.get("answer_password", "").strip().upper()
        if not expected_password:
            flash("Generate an answer password first.", "error")
        elif provided_password != expected_password:
            flash("Incorrect answer password.", "error")
        else:
            answer_gate["revealed"] = True
            _set_paper_answer_gate_state(token, answer_gate)
            flash("Answers are now visible on this paper.", "success")

    answer_gate = _paper_answer_gate_state(token)
    answers_unlocked = bool(answer_gate.get("revealed"))
    questions = _attach_question_paper_assets(payload.get("questions", []))
    questions = _attach_answer_reveal_data(questions, payload, answers_unlocked)

    return render_template(
        "question_paper.html",
        paper=payload,
        questions=questions,
        submission=submission,
        answer_password=answer_gate.get("password"),
        answers_unlocked=answers_unlocked,
    )


@bp.route("/response-upload/<path:filename>")
def view_uploaded_response(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


@bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if admin_registered():
        flash("Registration is already closed. Use the admin login page.", "error")
        return redirect(url_for("main.admin_login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        try:
            if not username:
                raise RuntimeError("Enter a username.")
            if len(password) < 8:
                raise RuntimeError("Use a password with at least 8 characters.")
            if password != password_confirm:
                raise RuntimeError("Passwords do not match.")
            db.create_admin_user(username, generate_password_hash(password))
            _set_admin_session(username)
            flash("Admin account created.", "success")
            return redirect(url_for("main.question_bank_page"))
        except Exception as exc:
            flash(str(exc), "error")

    return render_template("admin_auth.html", mode="register")


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not admin_registered():
        flash("No admin user exists yet. Register the first account now.", "error")
        return redirect(url_for("main.admin_register"))
    if admin_logged_in():
        return redirect(_admin_redirect_target())

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.get_admin_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Incorrect username or password.", "error")
        else:
            _set_admin_session(user["username"])
            flash("Admin login successful.", "success")
            next_url = request.form.get("next", "").strip()
            if not next_url.startswith("/"):
                next_url = url_for("main.question_bank_page")
            return redirect(next_url)

    return render_template("admin_auth.html", mode="login", next_url=request.args.get("next", ""))


@bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    _clear_admin_session()
    flash("Admin logged out.", "success")
    return redirect(url_for("main.index"))


@bp.route("/subjects/add", methods=["POST"])
def add_subject():
    try:
        subject_name = db.add_subject(
            request.form.get("subject_name", ""),
            is_stem="is_stem" in request.form,
            is_hobby="is_hobby" in request.form,
        )
        flash(f"Added subject: {subject_name}.", "success")
        target = request.form.get("next_url") or url_for("main.test_page", subject=subject_name)
    except Exception as exc:
        flash(f"Subject not added: {exc}", "error")
        target = request.form.get("next_url") or url_for("main.test_page")
    return redirect(target)


@bp.route("/api/questions", methods=["POST"])
@admin_required
def add_questions_api():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            raise RuntimeError("Send a JSON request body.")
        raw_rows, default_subject = _api_question_payload_rows(payload)
        rows = normalize_question_rows(raw_rows, default_subject=default_subject, source="manual-api")
        if not rows:
            raise RuntimeError("No valid questions were found. Each item needs at least subject, question, answer, and marks.")
        inserted = db.bulk_upsert_questions(rows)
        return jsonify(
            {
                "inserted": inserted,
                "questions": rows,
            }
        ), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@bp.route("/question-bank", methods=["GET", "POST"])
@admin_required
def question_bank_page():
    subjects = get_active_subjects()
    selected_subject = request.form.get("subject", request.args.get("subject", subjects[0] if subjects else SUBJECTS[0]))
    imported_preview = []
    import_mode = request.form.get("import_mode", "auto")
    academic_year = parse_int(request.form.get("academic_year", request.args.get("academic_year", 8)), default=8, minimum=7, maximum=13)
    question_target = parse_int(request.form.get("question_target", request.args.get("question_target", 100)), default=100, minimum=1, maximum=300)
    latest_prompt = None

    if request.method == "POST":
        action = request.form.get("action", "import")
        try:
            if action == "generate-prompt":
                latest_prompt = db.create_prompt_job(
                    subject=selected_subject,
                    academic_year=academic_year,
                    question_target=question_target,
                    trigger_reason="manual",
                    created_on=date.today().isoformat(),
                )
                flash(f"Generated a prompt for {selected_subject} Year {academic_year}.", "success")
            elif action == "run-poller":
                jobs = db.run_daily_prompt_poller(
                    subjects=subjects,
                    academic_year=academic_year,
                    question_target=question_target,
                    created_on=date.today().isoformat(),
                )
                flash(f"Daily prompt poller queued {len(jobs)} prompt jobs.", "success")
            elif action == "sync-generated":
                result = db.auto_process_queued_prompt_jobs(limit=len(subjects) * 3)
                if result["skipped"]:
                    raise RuntimeError("OPENAI_API_KEY is not set, so automatic generation is unavailable.")
                flash(
                    f"Processed {result['processed']} queued prompt jobs, imported {result['imported']} questions, failed {result['failed']} jobs.",
                    "success",
                )
            elif action == "add-single-question":
                question_asset_path = ""
                answer_asset_path = ""
                if request.form.get("question_image_mode", "no") == "yes":
                    question_image = request.files.get("question_image")
                    if question_image and question_image.filename:
                        question_asset_path = _save_question_bank_image(question_image, "question")
                if request.form.get("answer_image_mode", "no") == "yes":
                    answer_image = request.files.get("answer_image")
                    if answer_image and answer_image.filename:
                        answer_asset_path = _save_question_bank_image(answer_image, "answer")
                row_payload = _manual_question_row_from_request(default_subject=selected_subject)
                row_payload["asset_path"] = question_asset_path
                row_payload["answer_asset_path"] = answer_asset_path
                raw_question_text = str(row_payload.get("question") or "").strip()
                raw_answer_text = str(row_payload.get("answer") or "").strip()
                looks_like_question_set = (
                    raw_question_text.startswith("[")
                    or raw_question_text.startswith("{")
                    or '"question"' in raw_question_text
                    or "Topic:" in raw_question_text
                )
                if raw_question_text and not raw_answer_text and not question_asset_path and not answer_asset_path and looks_like_question_set:
                    bulk_rows = parse_question_bank_text(raw_question_text, selected_subject, source="manual-web")
                    if bulk_rows:
                        db.bulk_upsert_questions(bulk_rows)
                        imported_preview = bulk_rows[:8]
                        flash(
                            f"Detected a pasted question set in the single-question form and imported {len(bulk_rows)} questions into {selected_subject}.",
                            "success",
                        )
                    else:
                        raise RuntimeError("Pasted question set could not be parsed. Use a valid JSON array/object or the Import question set panel.")
                else:
                    has_question_content = bool(str(row_payload.get("question") or "").strip() or question_asset_path)
                    has_answer_content = bool(str(row_payload.get("answer") or "").strip() or answer_asset_path)
                    if not has_question_content and not has_answer_content:
                        raise RuntimeError("This form saves one question only. For JSON arrays, use Import content and click Import question set.")
                    if not has_question_content:
                        raise RuntimeError("Add question text or upload a question image.")
                    if not has_answer_content:
                        raise RuntimeError("Add answer text or upload an answer image.")
                    rows = normalize_question_rows(
                        [row_payload],
                        default_subject=selected_subject,
                        source="manual-web",
                    )
                    if not rows:
                        raise RuntimeError("Question could not be saved. Check the fields and try again.")
                    db.bulk_upsert_questions(rows)
                    imported_preview = rows
                    flash(f"Saved 1 question into {rows[0]['subject']}.", "success")
            else:
                raw_text = request.form.get("raw_text", "")
                if import_mode == "ai":
                    rows = parse_question_bank_text(
                        raw_text=json.dumps(extract_questions_from_text(selected_subject, raw_text)),
                        subject=selected_subject,
                        source="chatgpt-ai",
                    )
                else:
                    rows = parse_question_bank_text(raw_text, selected_subject, source="chatgpt-paste")
                    if not rows and import_mode == "auto":
                        ai_rows = extract_questions_from_text(selected_subject, raw_text)
                        rows = parse_question_bank_text(json.dumps(ai_rows), selected_subject, source="chatgpt-ai")

                if not rows:
                    raise RuntimeError("No valid questions were found. Use JSON or Topic/Question/Answer/Marks blocks.")

                db.bulk_upsert_questions(rows)
                prompt_job_id = request.form.get("prompt_job_id", "").strip()
                if prompt_job_id:
                    db.mark_prompt_job_used(int(prompt_job_id), status="imported")
                imported_preview = rows[:8]
                flash(f"Imported {len(rows)} questions into {selected_subject}.", "success")
        except Exception as exc:
            flash(f"Question bank action failed: {exc}", "error")

    progress = db.get_subject_progress(selected_subject)
    latest_prompt = latest_prompt or (db.get_recent_prompt_jobs(subject=selected_subject, limit=1) or [None])[0]
    recent_prompt_jobs = db.get_recent_prompt_jobs(subject=selected_subject, limit=8)
    return render_template(
        "question_bank.html",
        subjects=subjects,
        selected_subject=selected_subject,
        progress=progress,
        imported_preview=imported_preview,
        import_mode=import_mode,
        academic_year=academic_year,
        question_target=question_target,
        latest_prompt=latest_prompt,
        recent_prompt_jobs=recent_prompt_jobs,
        subject_topics_map=_subject_topics_map(subjects),
        openai_available=openai_available(),
    )


@bp.route("/ai-test")
def ai_test():
    subjects = get_testing_subjects()
    try:
        analysis = get_analysis()
        questions = generate_ai_mixed_test_payload(subjects, analysis["priority_subjects"], 10)
        markdown = format_test_markdown(questions, duration_minutes=10) if questions else ""
    except Exception as exc:
        questions = []
        markdown = f"AI test unavailable: {exc}\n\nUse the offline adaptive subject test instead."
    generated = {
        "questions": questions,
        "markdown": markdown,
        "title_subject": "Mixed",
        "progress": db.get_subject_progress(subjects[0]) if subjects else _empty_progress(),
    }
    config = {
        "test_type": "daily_all",
        "selected_subject": subjects[0] if subjects else SUBJECTS[0],
        "selected_subtopic": "",
        "source": "openai",
        "selection_mode": "adaptive",
        "duration": 10,
        "question_count": len(questions) or 5,
    }
    return render_template("test.html", **build_test_page_context(subjects=subjects, config=config, generated=generated))


@bp.route("/report")
def report():
    analysis = get_analysis()
    text = build_daily_report(analysis)
    return render_template("report.html", report=text, analysis=analysis)


@bp.route("/download-report")
def download_report():
    text = build_daily_report(get_analysis())
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=daily_report_{date.today().isoformat()}.txt"},
    )


@bp.route("/email-report", methods=["POST"])
def email_report():
    try:
        text = build_daily_report(get_analysis())
        send_daily_report_email(
            subject=f"GCSE Grade 9 Daily Report - {date.today().isoformat()}",
            body=text,
            recipient=DEFAULT_REPORT_RECIPIENT,
        )
        flash(f"Daily report emailed to {DEFAULT_REPORT_RECIPIENT}.", "success")
    except Exception as exc:
        flash(f"Email not sent: {exc}", "error")
    return redirect(url_for("main.report"))


@bp.route("/mark", methods=["GET", "POST"])
def mark():
    feedback = None
    if request.method == "POST":
        try:
            file = request.files.get("scan")
            mark_scheme = request.form.get("mark_scheme", "")
            if not file or not file.filename:
                raise RuntimeError("Upload a scan first.")
            filename = secure_filename(file.filename)
            path = UPLOAD_DIR / filename
            file.save(path)
            context = build_daily_report(get_analysis())
            feedback = mark_scanned_answers(path, mark_scheme, context)
        except Exception as exc:
            feedback = f"AI marking unavailable: {exc}"
    return render_template("mark.html", feedback=feedback)
