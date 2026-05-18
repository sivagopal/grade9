import re
import sqlite3
from datetime import date

from app.config import STEM_SUBJECTS, SUBJECTS, SUBJECT_SUBTOPICS
from app.paths import DB_PATH
from app.question_bank import (
    build_question_generation_prompt,
    build_subject_progress,
    choose_adaptive_questions,
    get_seed_questions,
    parse_question_bank_text,
)
from app.resources import infer_focus_area

HOBBY_SUBJECTS = {
    "JMC",
    "JMO",
    "Chess puzzles",
    "Computing",
    "Computing / 12th Subject",
}


def _display_question_text(question_text, source):
    text = str(question_text or "").strip()
    if not text:
        return text
    text = re.sub(r"^Q\d+:\s*", "", text)
    if str(source or "").endswith("-topic-pack"):
        text = re.sub(r"^[A-Za-z][A-Za-z &'/-]*\s+\d+:\s*", "", text)
    if source == "year8-english-literature-complexity-pack":
        text = re.sub(r"^Complexity\s+\d+\s+Question\s+\d+:\s*", "", text)
    return text.strip()

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

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    is_stem INTEGER NOT NULL DEFAULT 0,
    is_hobby INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'General',
    subtopic TEXT,
    difficulty_level INTEGER NOT NULL DEFAULT 1,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    explanation_text TEXT NOT NULL DEFAULT '',
    video_url TEXT,
    asset_path TEXT,
    answer_asset_path TEXT,
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

CREATE TABLE IF NOT EXISTS weak_topic_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'General',
    subtopic TEXT NOT NULL DEFAULT '',
    focus_label TEXT NOT NULL,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    threshold_reached_at TEXT,
    last_wrong_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject, topic, subtopic, focus_label)
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

CREATE TABLE IF NOT EXISTS generated_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL DEFAULT 'openai',
    test_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    subtopic TEXT,
    duration_minutes INTEGER NOT NULL,
    selection_mode TEXT NOT NULL DEFAULT 'adaptive',
    title TEXT NOT NULL,
    markdown_text TEXT NOT NULL,
    total_marks INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS generated_test_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'General',
    difficulty_level INTEGER NOT NULL DEFAULT 1,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    explanation_text TEXT NOT NULL DEFAULT '',
    marks INTEGER NOT NULL CHECK (marks > 0),
    FOREIGN KEY(test_id) REFERENCES generated_tests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS generated_test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    taken_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    FOREIGN KEY(test_id) REFERENCES generated_tests(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS generated_test_attempt_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    generated_question_id INTEGER NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    FOREIGN KEY(attempt_id) REFERENCES generated_test_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY(generated_question_id) REFERENCES generated_test_questions(id) ON DELETE CASCADE
);
"""


class PlannerDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init(self):
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()
            self._migrate(conn)
        self.seed_default_questions()
        self.seed_default_subjects()

    def _migrate(self, conn):
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(questions)").fetchall()}
        migrations = {
            "topic": "ALTER TABLE questions ADD COLUMN topic TEXT NOT NULL DEFAULT 'General'",
            "subtopic": "ALTER TABLE questions ADD COLUMN subtopic TEXT",
            "difficulty_level": "ALTER TABLE questions ADD COLUMN difficulty_level INTEGER NOT NULL DEFAULT 1",
            "source": "ALTER TABLE questions ADD COLUMN source TEXT NOT NULL DEFAULT 'seed'",
            "created_at": "ALTER TABLE questions ADD COLUMN created_at TEXT",
            "explanation_text": "ALTER TABLE questions ADD COLUMN explanation_text TEXT NOT NULL DEFAULT ''",
            "video_url": "ALTER TABLE questions ADD COLUMN video_url TEXT",
            "asset_path": "ALTER TABLE questions ADD COLUMN asset_path TEXT",
            "answer_asset_path": "ALTER TABLE questions ADD COLUMN answer_asset_path TEXT",
        }
        for column, sql in migrations.items():
            if column not in columns:
                conn.execute(sql)
        conn.execute(
            """
            UPDATE questions
            SET topic = COALESCE(NULLIF(TRIM(topic), ''), 'General'),
                subtopic = NULLIF(TRIM(subtopic), ''),
                difficulty_level = CASE
                    WHEN difficulty_level IS NULL OR difficulty_level < 1 THEN 1
                    ELSE difficulty_level
                END,
                explanation_text = COALESCE(explanation_text, ''),
                video_url = NULLIF(TRIM(video_url), ''),
                asset_path = NULLIF(asset_path, ''),
                answer_asset_path = NULLIF(answer_asset_path, ''),
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
        subject_columns = {row["name"] for row in conn.execute("PRAGMA table_info(subjects)").fetchall()}
        if "is_hobby" not in subject_columns:
            conn.execute("ALTER TABLE subjects ADD COLUMN is_hobby INTEGER NOT NULL DEFAULT 0")
        conn.executemany(
            """
            INSERT INTO subjects (name, is_stem, is_hobby)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO NOTHING
            """,
            [(subject, 1 if subject in STEM_SUBJECTS else 0, 1 if subject in HOBBY_SUBJECTS else 0) for subject in SUBJECTS],
        )
        conn.executemany(
            "UPDATE subjects SET is_hobby = 1 WHERE name = ?",
            [(subject,) for subject in sorted(HOBBY_SUBJECTS)],
        )
        conn.commit()

    def seed_default_questions(self):
        self.bulk_upsert_questions(get_seed_questions())

    def seed_default_subjects(self):
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO subjects (name, is_stem, is_hobby)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO NOTHING
                """,
                [(subject, 1 if subject in STEM_SUBJECTS else 0, 1 if subject in HOBBY_SUBJECTS else 0) for subject in SUBJECTS],
            )
            conn.commit()

    def has_admin_user(self):
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM admin_users").fetchone()
        return bool(row and int(row["total"]) > 0)

    def get_admin_user(self):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, username, password_hash, created_at
                FROM admin_users
                ORDER BY id ASC
                LIMIT 1
                """
            ).fetchone()
        return dict(row) if row else None

    def create_admin_user(self, username, password_hash):
        username_clean = " ".join(str(username or "").strip().split())
        if not username_clean:
            raise RuntimeError("Enter a username.")
        if not password_hash:
            raise RuntimeError("Password hash is required.")
        with self.connect() as conn:
            existing = conn.execute("SELECT COUNT(*) AS total FROM admin_users").fetchone()
            if existing and int(existing["total"]) > 0:
                raise RuntimeError("Registration is closed. An admin user already exists.")
            conn.execute(
                """
                INSERT INTO admin_users (username, password_hash)
                VALUES (?, ?)
                """,
                (username_clean, password_hash),
            )
            conn.commit()
        return self.get_admin_user()

    def get_admin_user_by_username(self, username):
        username_clean = " ".join(str(username or "").strip().split())
        if not username_clean:
            return None
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, username, password_hash, created_at
                FROM admin_users
                WHERE username = ?
                LIMIT 1
                """,
                (username_clean,),
            ).fetchone()
        return dict(row) if row else None

    def get_subject_rows(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT name, is_stem, is_hobby, created_at
                FROM subjects
                ORDER BY created_at ASC, id ASC
                """
            ).fetchall()
        ordered_rows = [dict(row) for row in rows]
        default_order = {subject: index for index, subject in enumerate(SUBJECTS)}
        ordered_rows.sort(key=lambda row: (default_order.get(row["name"], len(SUBJECTS)), row["name"]))
        return ordered_rows

    def get_subject_names(self, include_hobby=True):
        rows = self.get_subject_rows()
        if not include_hobby:
            rows = [row for row in rows if int(row.get("is_hobby") or 0) == 0]
        names = [row["name"] for row in rows]
        return names or list(SUBJECTS)

    def get_regular_subject_names(self):
        return self.get_subject_names(include_hobby=False)

    def get_hobby_subject_names(self):
        rows = self.get_subject_rows()
        return [row["name"] for row in rows if int(row.get("is_hobby") or 0) == 1]

    def get_stem_subjects(self):
        rows = self.get_subject_rows()
        stem_subjects = [row["name"] for row in rows if int(row["is_stem"] or 0) == 1]
        return stem_subjects or sorted(STEM_SUBJECTS)

    def add_subject(self, name, is_stem=False, is_hobby=False):
        subject_name = " ".join(str(name or "").strip().split())
        if not subject_name:
            raise RuntimeError("Enter a subject name first.")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO subjects (name, is_stem, is_hobby)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    is_stem = subjects.is_stem OR excluded.is_stem,
                    is_hobby = subjects.is_hobby OR excluded.is_hobby
                """,
                (subject_name, 1 if is_stem else 0, 1 if is_hobby else 0),
            )
            conn.commit()
        return subject_name

    def bulk_upsert_questions(self, rows):
        if not rows:
            return 0

        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO questions (
                    subject, topic, subtopic, difficulty_level, question_text, answer_text,
                    explanation_text, video_url, asset_path, answer_asset_path, marks, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject, question_text) DO UPDATE SET
                    topic = excluded.topic,
                    subtopic = excluded.subtopic,
                    difficulty_level = excluded.difficulty_level,
                    answer_text = excluded.answer_text,
                    explanation_text = excluded.explanation_text,
                    video_url = excluded.video_url,
                    asset_path = excluded.asset_path,
                    answer_asset_path = excluded.answer_asset_path,
                    marks = excluded.marks,
                    source = excluded.source
                """,
                [
                    (
                        row["subject"],
                        row["topic"],
                        row.get("subtopic"),
                        row["difficulty_level"],
                        row["question"],
                        row["answer"],
                        row.get("explanation", ""),
                        row.get("video_url"),
                        row.get("asset_path"),
                        row.get("answer_asset_path"),
                        row["marks"],
                        row.get("source", "manual"),
                    )
                    for row in rows
                ],
            )
            conn.commit()
        return len(rows)

    def get_questions_for_subject(self, subject):
        configured_topics = SUBJECT_SUBTOPICS.get(subject, [])
        with self.connect() as conn:
            if configured_topics:
                placeholders = ",".join("?" for _ in configured_topics)
                rows = conn.execute(
                    f"""
                    SELECT id, subject, topic, subtopic, difficulty_level, question_text, answer_text,
                           explanation_text, video_url, asset_path, answer_asset_path, marks, source, created_at
                    FROM questions
                    WHERE subject = ? AND topic IN ({placeholders})
                    ORDER BY topic, difficulty_level, id
                    """,
                    (subject, *configured_topics),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, subject, topic, subtopic, difficulty_level, question_text, answer_text,
                           explanation_text, video_url, asset_path, answer_asset_path, marks, source, created_at
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
                "subtopic": row["subtopic"],
                "difficulty_level": row["difficulty_level"],
                "question": _display_question_text(row["question_text"], row["source"]),
                "answer": row["answer_text"],
                "explanation": row["explanation_text"],
                "video_url": row["video_url"],
                "asset_path": row["asset_path"],
                "answer_asset_path": row["answer_asset_path"],
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
                SELECT id, subject, topic, subtopic, difficulty_level, question_text, answer_text,
                       explanation_text, video_url, asset_path, answer_asset_path, marks, source, created_at
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
                "subtopic": row["subtopic"],
                "difficulty_level": row["difficulty_level"],
                "question": _display_question_text(row["question_text"], row["source"]),
                "answer": row["answer_text"],
                "explanation": row["explanation_text"],
                "video_url": row["video_url"],
                "asset_path": row["asset_path"],
                "answer_asset_path": row["answer_asset_path"],
                "marks": row["marks"],
                "source": row["source"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_generated_test(
        self,
        *,
        source,
        test_type,
        subject,
        subtopic,
        duration_minutes,
        selection_mode,
        title,
        markdown_text,
        questions,
    ):
        total_marks = sum(max(1, int(question.get("marks", 1) or 1)) for question in questions)
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO generated_tests (
                    source, test_type, subject, subtopic, duration_minutes,
                    selection_mode, title, markdown_text, total_marks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source,
                    test_type,
                    subject,
                    subtopic or None,
                    int(duration_minutes),
                    selection_mode,
                    title,
                    markdown_text,
                    total_marks,
                ),
            )
            test_id = cursor.lastrowid
            conn.executemany(
                """
                INSERT INTO generated_test_questions (
                    test_id, sort_order, subject, topic, difficulty_level,
                    question_text, answer_text, explanation_text, marks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        test_id,
                        index,
                        question.get("subject", subject),
                        question.get("topic", "General"),
                        max(1, int(question.get("difficulty_level", 1) or 1)),
                        question.get("question", ""),
                        question.get("answer", ""),
                        question.get("explanation", ""),
                        max(1, int(question.get("marks", 1) or 1)),
                    )
                    for index, question in enumerate(questions, 1)
                ],
            )
            conn.commit()
        return self.get_generated_test(test_id)

    def get_generated_test(self, test_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, created_at, source, test_type, subject, subtopic,
                       duration_minutes, selection_mode, title, markdown_text, total_marks
                FROM generated_tests
                WHERE id = ?
                """,
                (test_id,),
            ).fetchone()
            if not row:
                return None
            latest_attempt = conn.execute(
                """
                SELECT id, taken_at, score, max_score
                FROM generated_test_attempts
                WHERE test_id = ?
                ORDER BY taken_at DESC, id DESC
                LIMIT 1
                """,
                (test_id,),
            ).fetchone()
            attempt_count = conn.execute(
                "SELECT COUNT(*) AS total FROM generated_test_attempts WHERE test_id = ?",
                (test_id,),
            ).fetchone()
        data = dict(row)
        data["latest_attempt"] = dict(latest_attempt) if latest_attempt else None
        data["attempt_count"] = int(attempt_count["total"]) if attempt_count else 0
        return data

    def get_generated_test_questions(self, test_id):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, subject, topic, difficulty_level, question_text,
                       answer_text, explanation_text, marks
                FROM generated_test_questions
                WHERE test_id = ?
                ORDER BY sort_order ASC, id ASC
                """,
                (test_id,),
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
                "marks": row["marks"],
                "source": "openai-generated-test",
            }
            for row in rows
        ]

    def record_generated_test_results(self, test_id, results):
        if not results:
            return None

        question_ids = [row["question_id"] for row in results]
        placeholders = ",".join("?" for _ in question_ids)
        with self.connect() as conn:
            generated_test = conn.execute(
                """
                SELECT subject, COALESCE(subtopic, '') AS subtopic
                FROM generated_tests
                WHERE id = ?
                """,
                (test_id,),
            ).fetchone()
            question_rows = conn.execute(
                f"""
                SELECT id, subject, topic, question_text, marks
                FROM generated_test_questions
                WHERE test_id = ? AND id IN ({placeholders})
                """,
                (test_id, *question_ids),
            ).fetchall()
            question_map = {row["id"]: row for row in question_rows}
            item_rows = []
            total_score = 0.0
            total_max = 0.0
            counter_rows = []
            for result in results:
                question = question_map.get(result["question_id"])
                if not question:
                    continue
                max_score = float(question["marks"])
                score = min(max(float(result["score"]), 0.0), max_score)
                total_score += score
                total_max += max_score
                item_rows.append((result["question_id"], score, max_score))
                counter_rows.append(
                    {
                        "subject": question["subject"] or (generated_test["subject"] if generated_test else ""),
                        "topic": question["topic"],
                        "subtopic": generated_test["subtopic"] if generated_test else "",
                        "question_text": question["question_text"],
                        "score": score,
                        "max_score": max_score,
                    }
                )
            if not item_rows:
                return None
            cursor = conn.execute(
                """
                INSERT INTO generated_test_attempts (test_id, score, max_score)
                VALUES (?, ?, ?)
                """,
                (test_id, total_score, total_max),
            )
            attempt_id = cursor.lastrowid
            conn.executemany(
                """
                INSERT INTO generated_test_attempt_items (attempt_id, generated_question_id, score, max_score)
                VALUES (?, ?, ?, ?)
                """,
                [(attempt_id, question_id, score, max_score) for question_id, score, max_score in item_rows],
            )
            self._apply_topic_counter_deltas(conn, counter_rows)
            conn.commit()
        return self.get_generated_test_attempt(attempt_id)

    def get_generated_test_attempt(self, attempt_id):
        with self.connect() as conn:
            attempt = conn.execute(
                """
                SELECT id, test_id, taken_at, score, max_score
                FROM generated_test_attempts
                WHERE id = ?
                """,
                (attempt_id,),
            ).fetchone()
            if not attempt:
                return None
            items = conn.execute(
                """
                SELECT generated_question_id AS question_id, score, max_score
                FROM generated_test_attempt_items
                WHERE attempt_id = ?
                ORDER BY id ASC
                """,
                (attempt_id,),
            ).fetchall()
        return {
            **dict(attempt),
            "items": [dict(row) for row in items],
        }

    def get_low_score_generated_tests(self, subject, limit=6, threshold=0.7):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT gt.id, gt.created_at, gt.subject, gt.subtopic, gt.duration_minutes,
                       gt.selection_mode, gt.title, gt.total_marks,
                       gta.taken_at, gta.score, gta.max_score
                FROM generated_tests gt
                JOIN generated_test_attempts gta ON gta.test_id = gt.id
                WHERE gt.subject = ? AND gt.source = 'openai' AND gt.test_type = 'subject_mini'
                ORDER BY gta.taken_at DESC, gta.id DESC
                """,
                (subject,),
            ).fetchall()

        latest_by_test = {}
        for row in rows:
            row_dict = dict(row)
            if row_dict["id"] not in latest_by_test:
                latest_by_test[row_dict["id"]] = row_dict

        suggestions = []
        for row in latest_by_test.values():
            max_score = float(row["max_score"] or 0)
            if max_score <= 0:
                continue
            ratio = float(row["score"] or 0) / max_score
            if ratio >= threshold:
                continue
            row["score_ratio"] = ratio
            suggestions.append(row)

        suggestions.sort(key=lambda row: (row["score_ratio"], row["taken_at"]), reverse=False)
        return suggestions[:limit]

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

    def get_topics_for_subject(self, subject):
        configured_topics = SUBJECT_SUBTOPICS.get(subject, [])
        if configured_topics:
            return configured_topics

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT topic
                FROM questions
                WHERE subject = ? AND topic IS NOT NULL AND TRIM(topic) != ''
                ORDER BY topic
                """,
                (subject,),
            ).fetchall()
        return [row["topic"] for row in rows]

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
                SELECT id, subject, topic, COALESCE(subtopic, '') AS subtopic, question_text, difficulty_level, marks
                FROM questions
                WHERE id IN ({placeholders})
                """,
                question_ids,
            ).fetchall()
            question_map = {row["id"]: row for row in question_rows}

            inserts = []
            counter_rows = []
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
                counter_rows.append(
                    {
                        "subject": question["subject"] or subject,
                        "topic": question["topic"],
                        "subtopic": question["subtopic"],
                        "question_text": question["question_text"],
                        "score": score,
                        "max_score": max_score,
                    }
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
            self._apply_topic_counter_deltas(conn, counter_rows)
            conn.commit()
        return len(inserts)

    def _apply_topic_counter_deltas(self, conn, counter_rows):
        if not counter_rows:
            return

        aggregated = {}
        for row in counter_rows:
            subject = str(row.get("subject") or "").strip()
            if not subject:
                continue
            topic = str(row.get("topic") or "General").strip() or "General"
            subtopic = str(row.get("subtopic") or "").strip()
            score = float(row.get("score") or 0.0)
            max_score = float(row.get("max_score") or 0.0)
            focus_label = infer_focus_area(
                subject,
                topic,
                subtopic=subtopic,
                question_text=row.get("question_text", ""),
            )
            key = (subject, topic, subtopic, focus_label)
            state = aggregated.setdefault(key, {"wrong_count": 0, "all_correct": True})
            if score < max_score:
                state["wrong_count"] += 1
                state["all_correct"] = False

        for (subject, topic, subtopic, focus_label), state in aggregated.items():
            delta = -1 if state["all_correct"] else state["wrong_count"]
            if delta == 0:
                continue
            existing = conn.execute(
                """
                SELECT id, wrong_count
                FROM weak_topic_counters
                WHERE subject = ? AND topic = ? AND subtopic = ? AND focus_label = ?
                """,
                (subject, topic, subtopic, focus_label),
            ).fetchone()
            if existing:
                current_count = int(existing["wrong_count"] or 0)
                new_count = max(0, current_count + delta)
                conn.execute(
                    """
                    UPDATE weak_topic_counters
                    SET wrong_count = ?,
                        threshold_reached_at = CASE
                            WHEN ? >= 5 AND ? < 5 THEN CURRENT_TIMESTAMP
                            WHEN ? < 5 THEN NULL
                            ELSE threshold_reached_at
                        END,
                        last_wrong_at = CASE
                            WHEN ? > 0 THEN CURRENT_TIMESTAMP
                            ELSE last_wrong_at
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (new_count, new_count, current_count, new_count, delta, existing["id"]),
                )
            else:
                if delta < 0:
                    continue
                conn.execute(
                    """
                    INSERT INTO weak_topic_counters (
                        subject, topic, subtopic, focus_label, wrong_count,
                        threshold_reached_at, last_wrong_at, updated_at
                    )
                    VALUES (
                        ?, ?, ?, ?, ?,
                        CASE WHEN ? >= 5 THEN CURRENT_TIMESTAMP ELSE NULL END,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    """,
                    (subject, topic, subtopic, focus_label, delta, delta),
                )

    def get_flagged_topic_counters(self, threshold=5, limit=8):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT subject, topic, subtopic, focus_label, wrong_count,
                       threshold_reached_at, last_wrong_at, updated_at
                FROM weak_topic_counters
                WHERE wrong_count >= ?
                ORDER BY wrong_count DESC, datetime(updated_at) DESC, subject ASC, focus_label ASC
                LIMIT ?
                """,
                (threshold, limit),
            ).fetchall()
        return [dict(row) for row in rows]

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

    def _get_recent_activity_dates(self, conn, days):
        rows = conn.execute(
            """
            SELECT activity_date
            FROM (
                SELECT log_date AS activity_date FROM daily_logs
                UNION
                SELECT log_date AS activity_date FROM subject_logs
                UNION
                SELECT DATE(taken_at) AS activity_date FROM question_attempts
                UNION
                SELECT DATE(gta.taken_at) AS activity_date
                FROM generated_test_attempts gta
            )
            WHERE activity_date IS NOT NULL AND activity_date != ''
            ORDER BY activity_date DESC
            LIMIT ?
            """,
            (days,),
        ).fetchall()
        return [row["activity_date"] for row in rows]

    def _get_recorded_test_scores_by_date(self, conn, log_dates):
        if not log_dates:
            return {}

        placeholders = ",".join("?" for _ in log_dates)
        rows = conn.execute(
            f"""
            SELECT activity_date, subject, SUM(score) AS total_score, SUM(max_score) AS total_max
            FROM (
                SELECT DATE(taken_at) AS activity_date, subject, score, max_score
                FROM question_attempts
                WHERE DATE(taken_at) IN ({placeholders})

                UNION ALL

                SELECT DATE(gta.taken_at) AS activity_date, gt.subject AS subject, gta.score, gta.max_score
                FROM generated_test_attempts gta
                JOIN generated_tests gt ON gt.id = gta.test_id
                WHERE DATE(gta.taken_at) IN ({placeholders})
            )
            GROUP BY activity_date, subject
            """,
            (*log_dates, *log_dates),
        ).fetchall()

        score_map = {}
        for row in rows:
            total_max = float(row["total_max"] or 0)
            if total_max <= 0:
                continue
            score_map[(row["activity_date"], row["subject"])] = {
                "test_score": int(round((float(row["total_score"] or 0) / total_max) * 100)),
                "total_score": float(row["total_score"] or 0),
                "total_max": total_max,
            }
        return score_map

    def get_recent_subject_logs(self, days=7):
        with self.connect() as conn:
            log_dates = self._get_recent_activity_dates(conn, days)
            if not log_dates:
                return []

            placeholders = ",".join("?" for _ in log_dates)
            rows = conn.execute(
                f"""
                SELECT * FROM subject_logs
                WHERE log_date IN ({placeholders})
                ORDER BY log_date DESC, subject
                """,
                tuple(log_dates),
            ).fetchall()
            recorded_scores = self._get_recorded_test_scores_by_date(conn, log_dates)

        merged_rows = {}
        for row in rows:
            data = dict(row)
            key = (data["log_date"], data["subject"])
            derived = recorded_scores.get(key)
            if derived:
                data["auto_test_score"] = derived["test_score"]
                data["test_score_source"] = "manual" if data.get("test_score") is not None else "recorded_attempts"
                if data.get("test_score") is None:
                    data["test_score"] = derived["test_score"]
            else:
                data["auto_test_score"] = None
                data["test_score_source"] = "manual" if data.get("test_score") is not None else None
            merged_rows[key] = data

        for (log_date, subject), derived in recorded_scores.items():
            if (log_date, subject) in merged_rows:
                continue
            merged_rows[(log_date, subject)] = {
                "log_date": log_date,
                "subject": subject,
                "study_minutes": 0,
                "confidence": 3,
                "test_score": derived["test_score"],
                "problem_notes": "",
                "auto_test_score": derived["test_score"],
                "test_score_source": "recorded_attempts",
            }

        return sorted(
            merged_rows.values(),
            key=lambda row: (row["log_date"], row["subject"]),
            reverse=True,
        )
