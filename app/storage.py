import sqlite3
from datetime import date

from app.paths import DB_PATH
from app.question_bank import (
    build_question_generation_prompt,
    build_subject_progress,
    choose_adaptive_questions,
    get_seed_questions,
    parse_question_bank_text,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date TEXT UNIQUE NOT NULL,
    sleep_hours REAL NOT NULL,
    energy INTEGER NOT NULL,
    focus INTEGER NOT NULL,
    mood TEXT,
    homework_minutes INTEGER NOT NULL,
    revision_minutes INTEGER NOT NULL,
    reading_minutes INTEGER NOT NULL,
    exercise_minutes INTEGER NOT NULL,
    distractions_minutes INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS subject_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date TEXT NOT NULL,
    subject TEXT NOT NULL,
    study_minutes INTEGER NOT NULL,
    confidence INTEGER NOT NULL,
    test_score INTEGER,
    problem_notes TEXT,
    UNIQUE(log_date, subject)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'General',
    difficulty_level INTEGER NOT NULL DEFAULT 1,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    explanation_text TEXT NOT NULL DEFAULT '',
    asset_path TEXT,
    marks INTEGER NOT NULL CHECK (marks > 0),
    source TEXT NOT NULL DEFAULT 'seed',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject, question_text)
);

CREATE TABLE IF NOT EXISTS question_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    FOREIGN KEY(question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS prompt_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_on TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subject TEXT NOT NULL,
    academic_year INTEGER NOT NULL DEFAULT 8,
    question_target INTEGER NOT NULL DEFAULT 100,
    based_on_score INTEGER NOT NULL DEFAULT 0,
    focus_topic TEXT,
    prompt_text TEXT NOT NULL,
    trigger_reason TEXT NOT NULL DEFAULT 'manual',
    status TEXT NOT NULL DEFAULT 'queued',
    processed_at TEXT,
    imported_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    UNIQUE(created_on, subject, academic_year, question_target, trigger_reason)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class PlannerDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()
            self._migrate(conn)
        self.seed_default_questions()

    def _migrate(self, conn):
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(questions)").fetchall()}
        migrations = {
            "topic": "ALTER TABLE questions ADD COLUMN topic TEXT NOT NULL DEFAULT 'General'",
            "difficulty_level": "ALTER TABLE questions ADD COLUMN difficulty_level INTEGER NOT NULL DEFAULT 1",
            "source": "ALTER TABLE questions ADD COLUMN source TEXT NOT NULL DEFAULT 'seed'",
            "created_at": "ALTER TABLE questions ADD COLUMN created_at TEXT",
            "explanation_text": "ALTER TABLE questions ADD COLUMN explanation_text TEXT NOT NULL DEFAULT ''",
            "asset_path": "ALTER TABLE questions ADD COLUMN asset_path TEXT",
        }
        for column, sql in migrations.items():
            if column not in columns:
                conn.execute(sql)
        conn.execute(
            """
            UPDATE questions
            SET topic = COALESCE(NULLIF(topic, ''), 'General'),
                difficulty_level = CASE
                    WHEN difficulty_level IS NULL OR difficulty_level < 1 THEN 1
                    ELSE difficulty_level
                END,
                explanation_text = COALESCE(explanation_text, ''),
                asset_path = NULLIF(asset_path, ''),
                source = COALESCE(NULLIF(source, ''), 'seed'),
                created_at = COALESCE(NULLIF(created_at, ''), CURRENT_TIMESTAMP)
            """
        )
        prompt_columns = {row["name"] for row in conn.execute("PRAGMA table_info(prompt_jobs)").fetchall()}
        prompt_migrations = {
            "processed_at": "ALTER TABLE prompt_jobs ADD COLUMN processed_at TEXT",
            "imported_count": "ALTER TABLE prompt_jobs ADD COLUMN imported_count INTEGER NOT NULL DEFAULT 0",
            "last_error": "ALTER TABLE prompt_jobs ADD COLUMN last_error TEXT",
        }
        for column, sql in prompt_migrations.items():
            if column not in prompt_columns:
                conn.execute(sql)
        conn.executemany(
            """
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO NOTHING
            """,
            [
                ("allow_random_repeat", "0"),
                ("startup_refresh_enabled", "1"),
                ("startup_refresh_target", "8"),
            ],
        )
        conn.commit()

    def seed_default_questions(self):
        self.bulk_upsert_questions(get_seed_questions())

    def bulk_upsert_questions(self, rows):
        if not rows:
            return 0

        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO questions (
                    subject, topic, difficulty_level, question_text, answer_text, explanation_text, asset_path, marks, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject, question_text) DO UPDATE SET
                    topic = excluded.topic,
                    difficulty_level = excluded.difficulty_level,
                    answer_text = excluded.answer_text,
                    explanation_text = excluded.explanation_text,
                    asset_path = excluded.asset_path,
                    marks = excluded.marks,
                    source = excluded.source
                """,
                [
                    (
                        row["subject"],
                        row["topic"],
                        row["difficulty_level"],
                        row["question"],
                        row["answer"],
                        row.get("explanation", ""),
                        row.get("asset_path"),
                        row["marks"],
                        row.get("source", "manual"),
                    )
                    for row in rows
                ],
            )
            conn.commit()
        return len(rows)

    def get_questions_for_subject(self, subject):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, subject, topic, difficulty_level, question_text, answer_text, explanation_text, asset_path, marks, source, created_at
                FROM questions
                WHERE subject = ?
                ORDER BY topic, difficulty_level, id
                """,
                (subject,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "difficulty_level": row["difficulty_level"],
                "question": row["question_text"],
                "answer": row["answer_text"],
                "explanation": row["explanation_text"],
                "asset_path": row["asset_path"],
                "marks": row["marks"],
                "source": row["source"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_questions_by_ids(self, question_ids):
        if not question_ids:
            return []
        placeholders = ",".join("?" for _ in question_ids)
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT id, subject, topic, difficulty_level, question_text, answer_text,
                       explanation_text, asset_path, marks, source, created_at
                FROM questions
                WHERE id IN ({placeholders})
                ORDER BY id
                """,
                question_ids,
            ).fetchall()
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "difficulty_level": row["difficulty_level"],
                "question": row["question_text"],
                "answer": row["answer_text"],
                "explanation": row["explanation_text"],
                "asset_path": row["asset_path"],
                "marks": row["marks"],
                "source": row["source"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_recent_attempts_for_subject(self, subject, limit=200):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT taken_at, subject, topic, difficulty_level, question_id, score, max_score
                FROM question_attempts
                WHERE subject = ?
                ORDER BY taken_at DESC, id DESC
                LIMIT ?
                """,
                (subject, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_setting(self, key, default=None):
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, str(value)),
            )
            conn.commit()

    def get_settings(self):
        return {
            "allow_random_repeat": self.get_setting("allow_random_repeat", "0") == "1",
            "startup_refresh_enabled": self.get_setting("startup_refresh_enabled", "1") == "1",
            "startup_refresh_target": int(self.get_setting("startup_refresh_target", "8") or 8),
        }

    def get_adaptive_questions(self, subject, max_questions=5):
        questions = self.get_questions_for_subject(subject)
        attempts = self.get_recent_attempts_for_subject(subject)
        settings = self.get_settings()
        return choose_adaptive_questions(
            questions,
            attempts,
            max_questions=max_questions,
            allow_random_repeat=settings["allow_random_repeat"],
        )

    def get_subject_progress(self, subject):
        questions = self.get_questions_for_subject(subject)
        attempts = self.get_recent_attempts_for_subject(subject)
        progress = build_subject_progress(questions, attempts)
        progress["question_total"] = len(questions)
        return progress

    def create_prompt_job(
        self,
        subject,
        academic_year=8,
        question_target=100,
        trigger_reason="manual",
        created_on=None,
    ):
        created_on = created_on or "manual"
        progress = self.get_subject_progress(subject)
        prompt_text = build_question_generation_prompt(subject, academic_year, question_target, progress)
        based_on_score = progress.get("subject_score", 0)
        focus_topic = progress.get("next_focus", {}).get("topic") if progress.get("next_focus") else None

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO prompt_jobs (
                    created_on, subject, academic_year, question_target,
                    based_on_score, focus_topic, prompt_text, trigger_reason, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'queued')
                ON CONFLICT(created_on, subject, academic_year, question_target, trigger_reason)
                DO UPDATE SET
                    based_on_score = excluded.based_on_score,
                    focus_topic = excluded.focus_topic,
                    prompt_text = excluded.prompt_text,
                    status = 'queued'
                """,
                (
                    created_on,
                    subject,
                    academic_year,
                    question_target,
                    based_on_score,
                    focus_topic,
                    prompt_text,
                    trigger_reason,
                ),
            )
            conn.commit()

        rows = self.get_recent_prompt_jobs(subject=subject, limit=1, trigger_reason=trigger_reason)
        return rows[0] if rows else None

    def get_recent_prompt_jobs(self, subject=None, limit=20, trigger_reason=None):
        clauses = []
        params = []
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if trigger_reason:
            clauses.append("trigger_reason = ?")
            params.append(trigger_reason)

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT id, created_on, created_at, subject, academic_year, question_target,
                       based_on_score, focus_topic, prompt_text, trigger_reason, status,
                       processed_at, imported_count, last_error
                FROM prompt_jobs
                {where_clause}
                ORDER BY created_on DESC, id DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_prompt_job_used(self, prompt_job_id, status="used"):
        with self.connect() as conn:
            conn.execute(
                "UPDATE prompt_jobs SET status = ?, processed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, prompt_job_id),
            )
            conn.commit()

    def get_prompt_job(self, prompt_job_id):
        rows = self.get_recent_prompt_jobs(limit=500)
        for row in rows:
            if row["id"] == prompt_job_id:
                return row
        return None

    def update_prompt_job_result(self, prompt_job_id, status, imported_count=0, last_error=None):
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE prompt_jobs
                SET status = ?,
                    imported_count = ?,
                    last_error = ?,
                    processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, imported_count, last_error, prompt_job_id),
            )
            conn.commit()

    def process_prompt_job(self, prompt_job_id):
        from app.openai_helper import generate_question_bank_from_prompt

        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, subject, prompt_text
                FROM prompt_jobs
                WHERE id = ?
                """,
                (prompt_job_id,),
            ).fetchone()
        if not row:
            raise RuntimeError(f"Prompt job {prompt_job_id} not found.")

        try:
            generated_rows = generate_question_bank_from_prompt(row["prompt_text"])
            normalized = parse_question_bank_text(
                raw_text=__import__("json").dumps(generated_rows),
                subject=row["subject"],
                source="daily-auto",
            )
            if not normalized:
                raise RuntimeError("OpenAI returned no usable questions.")
            imported_count = self.bulk_upsert_questions(normalized)
            self.update_prompt_job_result(prompt_job_id, status="imported", imported_count=imported_count, last_error=None)
            return imported_count
        except Exception as exc:
            self.update_prompt_job_result(prompt_job_id, status="failed", imported_count=0, last_error=str(exc))
            raise

    def auto_process_queued_prompt_jobs(self, limit=20):
        from app.openai_helper import openai_available

        if not openai_available():
            return {"processed": 0, "imported": 0, "failed": 0, "skipped": True}

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id
                FROM prompt_jobs
                WHERE status = 'queued'
                ORDER BY created_on ASC, id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        processed = 0
        imported = 0
        failed = 0
        for row in rows:
            processed += 1
            try:
                imported += self.process_prompt_job(row["id"])
            except Exception:
                failed += 1
        return {"processed": processed, "imported": imported, "failed": failed, "skipped": False}

    def run_daily_prompt_poller(self, subjects, academic_year=8, question_target=100, created_on=None):
        created_on = created_on or date.today().isoformat()
        jobs = []
        for subject in subjects:
            jobs.append(
                self.create_prompt_job(
                    subject=subject,
                    academic_year=academic_year,
                    question_target=question_target,
                    trigger_reason="daily-poller",
                    created_on=created_on,
                )
            )
        return [job for job in jobs if job]

    def record_test_results(self, subject, results):
        if not results:
            return 0

        question_ids = [row["question_id"] for row in results]
        placeholders = ",".join("?" for _ in question_ids)
        with self.connect() as conn:
            question_rows = conn.execute(
                f"""
                SELECT id, subject, topic, difficulty_level, marks
                FROM questions
                WHERE id IN ({placeholders})
                """,
                question_ids,
            ).fetchall()
            question_map = {row["id"]: row for row in question_rows}

            inserts = []
            for result in results:
                question = question_map.get(result["question_id"])
                if not question:
                    continue
                max_score = float(question["marks"])
                score = min(max(float(result["score"]), 0.0), max_score)
                inserts.append(
                    (
                        subject,
                        question["topic"],
                        question["difficulty_level"],
                        question["id"],
                        score,
                        max_score,
                    )
                )

            conn.executemany(
                """
                INSERT INTO question_attempts (
                    subject, topic, difficulty_level, question_id, score, max_score
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                inserts,
            )
            conn.commit()
        return len(inserts)

    def refresh_live_question_bank(self, subjects, per_subject_target=8):
        from app.openai_helper import generate_similar_question_bank, openai_available

        if not openai_available():
            return {"generated": 0, "subjects": 0, "skipped": True}

        total_generated = 0
        processed_subjects = 0
        for subject in subjects:
            progress = self.get_subject_progress(subject)
            next_focus = progress.get("next_focus")
            attempted_ids = {row["question_id"] for row in self.get_recent_attempts_for_subject(subject)}
            questions = self.get_questions_for_subject(subject)
            reference_rows = []
            if next_focus:
                reference_rows = [row for row in questions if row["topic"] == next_focus["topic"]]
            if not reference_rows:
                reference_rows = questions[: min(5, len(questions))]
            if attempted_ids:
                attempted_rows = [row for row in questions if row["id"] in attempted_ids]
                if attempted_rows:
                    reference_rows = attempted_rows[-5:]

            if not reference_rows:
                continue

            topic = next_focus["topic"] if next_focus else reference_rows[0]["topic"]
            generated_rows = generate_similar_question_bank(subject, topic, reference_rows, question_target=per_subject_target)
            normalized = parse_question_bank_text(
                raw_text=__import__("json").dumps(generated_rows),
                subject=subject,
                source="startup-live-refresh",
            )
            if not normalized:
                continue
            total_generated += self.bulk_upsert_questions(normalized)
            processed_subjects += 1
        return {"generated": total_generated, "subjects": processed_subjects, "skipped": False}

    def upsert_daily_log(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_logs (
                    log_date, sleep_hours, energy, focus, mood,
                    homework_minutes, revision_minutes, reading_minutes,
                    exercise_minutes, distractions_minutes, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(log_date) DO UPDATE SET
                    sleep_hours=excluded.sleep_hours,
                    energy=excluded.energy,
                    focus=excluded.focus,
                    mood=excluded.mood,
                    homework_minutes=excluded.homework_minutes,
                    revision_minutes=excluded.revision_minutes,
                    reading_minutes=excluded.reading_minutes,
                    exercise_minutes=excluded.exercise_minutes,
                    distractions_minutes=excluded.distractions_minutes,
                    notes=excluded.notes
                """,
                (
                    data["log_date"], data["sleep_hours"], data["energy"], data["focus"],
                    data.get("mood", ""), data["homework_minutes"], data["revision_minutes"],
                    data["reading_minutes"], data["exercise_minutes"],
                    data["distractions_minutes"], data.get("notes", "")
                )
            )
            conn.commit()

    def upsert_subject_log(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO subject_logs (
                    log_date, subject, study_minutes, confidence, test_score, problem_notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(log_date, subject) DO UPDATE SET
                    study_minutes=excluded.study_minutes,
                    confidence=excluded.confidence,
                    test_score=excluded.test_score,
                    problem_notes=excluded.problem_notes
                """,
                (
                    data["log_date"], data["subject"], data["study_minutes"],
                    data["confidence"], data.get("test_score"), data.get("problem_notes", "")
                )
            )
            conn.commit()

    def get_recent_daily_logs(self, days=7):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM daily_logs ORDER BY log_date DESC LIMIT ?",
                (days,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_subject_logs(self, days=7):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM subject_logs
                WHERE log_date IN (
                    SELECT log_date FROM daily_logs ORDER BY log_date DESC LIMIT ?
                )
                ORDER BY log_date DESC, subject
                """,
                (days,)
            ).fetchall()
        return [dict(r) for r in rows]
