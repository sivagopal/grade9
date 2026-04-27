from datetime import date
import json

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.analyser import analyse_week, generate_next_day_timetable, generate_weekend_plan, next_day_name
from app.config import SUBJECTS
from app.emailer import DEFAULT_REPORT_RECIPIENT, send_daily_report_email
from app.openai_helper import (
    extract_questions_from_text,
    generate_ai_subject_test,
    generate_ai_test,
    mark_scanned_answers,
    openai_available,
)
from app.paths import UPLOAD_DIR
from app.question_bank import format_test_markdown, parse_question_bank_text
from app.pdf_export import build_test_pdf
from app.reports import build_daily_report
from app.review import build_wrong_answer_review
from app.resources import recommend_resources
from app.storage import PlannerDB

bp = Blueprint("main", __name__)
db = PlannerDB()


def get_analysis():
    daily = db.get_recent_daily_logs(7)
    subjects = db.get_recent_subject_logs(7)
    return analyse_week(daily, subjects)


def parse_int(value, default, minimum=1, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    parsed = max(minimum, parsed)
    if maximum is not None:
        parsed = min(maximum, parsed)
    return parsed


def build_local_all_subjects_test(subjects, per_subject=1):
    questions = []
    for subject in subjects:
        questions.extend(db.get_adaptive_questions(subject, max_questions=per_subject))
    return questions


def get_test_configuration(values):
    test_type = values.get("test_type", "daily_all")
    selected_subject = values.get("subject", SUBJECTS[0])
    source = values.get("source", "local")
    duration = parse_int(values.get("duration", 10 if test_type == "daily_all" else 30), default=10, minimum=5, maximum=120)
    question_count = parse_int(values.get("count", 5 if test_type == "subject_mini" else len(SUBJECTS)), default=5, minimum=1, maximum=30)
    return {
        "test_type": test_type,
        "selected_subject": selected_subject,
        "source": source,
        "duration": duration,
        "question_count": question_count,
    }


def generate_test_content(config):
    analysis = get_analysis()
    questions = []
    markdown = ""
    title_subject = None
    progress = db.get_subject_progress(config["selected_subject"])

    if config["source"] == "openai":
        if config["test_type"] == "daily_all":
            markdown = generate_ai_test(SUBJECTS, analysis["priority_subjects"], config["duration"])
        else:
            weak_topics = [item["topic"] for item in progress.get("topics", [])[:3]]
            markdown = generate_ai_subject_test(config["selected_subject"], weak_topics=weak_topics, minutes=config["duration"])
            title_subject = config["selected_subject"]
    else:
        if config["test_type"] == "daily_all":
            per_subject = max(1, config["question_count"] // max(1, len(SUBJECTS)))
            questions = build_local_all_subjects_test(SUBJECTS, per_subject=per_subject)
            markdown = format_test_markdown(questions)
        else:
            questions = db.get_adaptive_questions(config["selected_subject"], max_questions=config["question_count"])
            markdown = format_test_markdown(questions, title_subject=config["selected_subject"]) if questions else ""
            title_subject = config["selected_subject"]

    return {
        "analysis": analysis,
        "questions": questions,
        "markdown": markdown,
        "title_subject": title_subject,
        "progress": progress,
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

            for subject in SUBJECTS:
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

    return render_template("log.html", subjects=SUBJECTS, today=date.today().isoformat())


@bp.route("/test", methods=["GET", "POST"])
def test_page():
    config = get_test_configuration(request.values)
    generated = {"questions": [], "markdown": "", "title_subject": None, "progress": db.get_subject_progress(config["selected_subject"])}
    review_items = []

    if request.method == "POST" or request.args.get("generate") == "1":
        try:
            generated = generate_test_content(config)
            if config["source"] == "local" and config["test_type"] == "subject_mini" and not generated["questions"]:
                flash(f"No questions stored for {config['selected_subject']}. Import some first.", "error")
        except Exception as exc:
            flash(f"Test generation failed: {exc}", "error")

    return render_template(
        "test.html",
        subjects=SUBJECTS,
        selected_subject=config["selected_subject"],
        question_count=config["question_count"],
        questions=generated["questions"],
        progress=generated["progress"],
        review_items=review_items,
        test_markdown=generated["markdown"],
        test_type=config["test_type"],
        source=config["source"],
        duration=config["duration"],
        openai_enabled=openai_available(),
    )


@bp.route("/test/submit", methods=["POST"])
def submit_test_results():
    subject = request.form.get("subject", SUBJECTS[0])
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

    recorded = db.record_test_results(subject, results)
    if not recorded:
        flash("No test results were recorded.", "error")
        return redirect(url_for("main.test_page", subject=subject, test_type="subject_mini", source="local", generate="1"))

    flash(f"Recorded {recorded} results for {subject}. The next test will adapt to those marks.", "success")
    questions = db.get_questions_by_ids([row["question_id"] for row in results])
    question_map = {row["id"]: row for row in questions}
    ordered_questions = [question_map[row["question_id"]] for row in results if row["question_id"] in question_map]
    score_map = {row["question_id"]: row for row in results}
    review_items = build_wrong_answer_review(subject, ordered_questions, score_map)
    progress = db.get_subject_progress(subject)
    markdown = format_test_markdown(ordered_questions, title_subject=subject) if ordered_questions else ""
    return render_template(
        "test.html",
        subjects=SUBJECTS,
        selected_subject=subject,
        question_count=len(ordered_questions) or 5,
        questions=ordered_questions,
        progress=progress,
        review_items=review_items,
        test_markdown=markdown,
        test_type="subject_mini",
        source="local",
        duration=30,
        openai_enabled=openai_available(),
    )


@bp.route("/download-test")
def download_test():
    config = get_test_configuration(request.args)
    generated = generate_test_content(config)
    markdown = generated["markdown"]
    export_format = request.args.get("format", "md").lower()
    filename_subject = secure_filename(config["selected_subject"]).lower() or "subject"
    if config["test_type"] == "daily_all":
        filename_root = f"gcse_daily_all_test_{date.today().isoformat()}"
    else:
        filename_root = f"gcse_{filename_subject}_test_{date.today().isoformat()}"

    if export_format == "pdf":
        title = generated["title_subject"] or "GCSE Grade 9 Test"
        questions = generated["questions"]
        if not questions:
            flash("PDF export currently requires the local question bank so diagrams and question layout can be embedded.", "error")
            return redirect(url_for("main.test_page", **config, generate="1"))
        pdf_bytes = build_test_pdf(questions, f"GCSE Grade 9 {title}")
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename_root}.pdf"},
        )

    return Response(
        markdown,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename_root}.md"},
    )


@bp.route("/question-bank", methods=["GET", "POST"])
def question_bank_page():
    selected_subject = request.form.get("subject", request.args.get("subject", SUBJECTS[0]))
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
                    subjects=SUBJECTS,
                    academic_year=academic_year,
                    question_target=question_target,
                    created_on=date.today().isoformat(),
                )
                flash(f"Daily prompt poller queued {len(jobs)} prompt jobs.", "success")
            elif action == "sync-generated":
                result = db.auto_process_queued_prompt_jobs(limit=len(SUBJECTS) * 3)
                if result["skipped"]:
                    raise RuntimeError("OPENAI_API_KEY is not set, so automatic generation is unavailable.")
                flash(
                    f"Processed {result['processed']} queued prompt jobs, imported {result['imported']} questions, failed {result['failed']} jobs.",
                    "success",
                )
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
        subjects=SUBJECTS,
        selected_subject=selected_subject,
        progress=progress,
        imported_preview=imported_preview,
        import_mode=import_mode,
        academic_year=academic_year,
        question_target=question_target,
        latest_prompt=latest_prompt,
        recent_prompt_jobs=recent_prompt_jobs,
        openai_available=openai_available(),
    )


@bp.route("/ai-test")
def ai_test():
    try:
        analysis = get_analysis()
        markdown = generate_ai_test(SUBJECTS, analysis["priority_subjects"], 10)
    except Exception as exc:
        markdown = f"AI test unavailable: {exc}\n\nUse the offline adaptive subject test instead."
    return render_template(
        "test.html",
        test_markdown=markdown,
        subjects=SUBJECTS,
        selected_subject=SUBJECTS[0],
        question_count=5,
        questions=[],
        progress=db.get_subject_progress(SUBJECTS[0]),
        test_type="daily_all",
        source="openai",
        duration=10,
        openai_enabled=openai_available(),
    )


@bp.route("/report")
def report():
    analysis = get_analysis()
    text = build_daily_report(analysis)
    return render_template("report.html", report=text)


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
