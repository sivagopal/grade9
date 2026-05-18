from flask import Flask


def create_app():
    from app.env_loader import load_env_file

    loaded_env_file = load_env_file()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-this-local-dev-key"
    app.config["LAST_STARTUP_REFRESH"] = None
    app.config["EXTERNAL_ENV_FILE"] = str(loaded_env_file) if loaded_env_file else None

    from app.storage import PlannerDB

    db = PlannerDB()
    subjects = db.get_subject_names()
    db.run_daily_prompt_poller(subjects, academic_year=8, question_target=100)
    try:
        db.auto_process_queued_prompt_jobs(limit=len(subjects) * 2)
    except Exception:
        pass
    try:
        settings = db.get_settings()
        if settings["startup_refresh_enabled"]:
            app.config["LAST_STARTUP_REFRESH"] = db.refresh_live_question_bank(
                subjects,
                per_subject_target=settings["startup_refresh_target"],
            )
    except Exception as exc:
        app.config["LAST_STARTUP_REFRESH"] = {"generated": 0, "subjects": 0, "skipped": False, "error": str(exc)}

    from app.routes import bp
    app.register_blueprint(bp)

    return app
