from collections import defaultdict
from datetime import datetime, timedelta
from app.config import SUBJECTS, STEM_SUBJECTS

GRADE9_TARGET_SCORE = 90
NORMAL_CURVE_MEAN = 65
NORMAL_CURVE_SPREAD = 18


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def _short_subject_label(subject):
    overrides = {
        "English Literature": "Eng Lit",
        "Business Studies": "Business",
        "Computing / 12th Subject": "Computing",
        "Further Maths": "Further Maths",
    }
    if subject in overrides:
        return overrides[subject]
    if len(subject) <= 12:
        return subject
    words = [part for part in subject.replace("/", " ").split() if part]
    if len(words) >= 2:
        return " ".join(words[:2])
    return subject[:12]


def _score_band(score):
    if score is None:
        return "No score yet"
    if score >= GRADE9_TARGET_SCORE:
        return "Grade 9 zone"
    if score >= 80:
        return "Close to target"
    if score >= 65:
        return "Secure but below 9"
    if score >= 50:
        return "Developing"
    return "Needs recovery"


def _trend_text(delta):
    if delta is None:
        return "No prior datapoint"
    if delta > 0:
        return f"Up {delta:.0f} pts"
    if delta < 0:
        return f"Down {abs(delta):.0f} pts"
    return "Flat"


def _gaussian_height(score, mean=NORMAL_CURVE_MEAN, spread=NORMAL_CURVE_SPREAD):
    if score is None:
        return 0.0
    exponent = -0.5 * (((score - mean) / spread) ** 2)
    return 2.718281828 ** exponent


def _build_subject_performance(subjects, subject_logs, stem_subjects):
    by_subject = defaultdict(list)
    for row in subject_logs:
        by_subject[row["subject"]].append(row)

    subject_rows = []
    for subject in subjects:
        rows = sorted(
            by_subject.get(subject, []),
            key=lambda row: (row.get("log_date", ""), row.get("id", 0)),
        )
        score_points = []
        for row in rows:
            if row.get("test_score") is None:
                continue
            score_points.append({
                "date": row["log_date"],
                "score": float(row["test_score"]),
            })

        avg_confidence = (
            sum(float(row.get("confidence", 3) or 3) for row in rows) / len(rows)
            if rows
            else 3.0
        )
        total_minutes = sum(int(row.get("study_minutes", 0) or 0) for row in rows)
        latest_score = round(score_points[-1]["score"]) if score_points else None
        first_score = round(score_points[0]["score"]) if score_points else None
        previous_score = round(score_points[-2]["score"]) if len(score_points) >= 2 else None
        baseline_delta = (
            round(latest_score - first_score)
            if latest_score is not None and first_score is not None and len(score_points) >= 2
            else None
        )
        recent_delta = (
            round(latest_score - previous_score)
            if latest_score is not None and previous_score is not None
            else None
        )
        confidence_component = (avg_confidence / 5) * 18
        minutes_component = min(total_minutes, 120) / 120 * 12
        score_component = latest_score * 0.7 if latest_score is not None else 28
        readiness_score = round(_clamp(score_component + confidence_component + minutes_component, 0, 100))
        display_score = latest_score if latest_score is not None else readiness_score
        gap_to_target = (
            max(0, GRADE9_TARGET_SCORE - latest_score)
            if latest_score is not None
            else None
        )
        curve_height = 16 + (_gaussian_height(display_score) * 56)
        point_labels = [f"{int(point['score'])}% ({point['date'][5:]})" for point in score_points[-4:]]
        history_text = " -> ".join(point_labels) if point_labels else "No recorded paper scores yet"

        subject_rows.append({
            "subject": subject,
            "short_subject": _short_subject_label(subject),
            "is_stem": subject in stem_subjects,
            "score": latest_score,
            "display_score": display_score,
            "score_label": f"{latest_score}%" if latest_score is not None else "No score yet",
            "score_band": _score_band(latest_score),
            "gap_to_target": gap_to_target,
            "gap_label": f"{gap_to_target} pts to Grade 9" if gap_to_target is not None else "Need a scored paper",
            "avg_confidence": round(avg_confidence, 1),
            "total_minutes": total_minutes,
            "readiness_score": readiness_score,
            "recent_delta": recent_delta,
            "baseline_delta": baseline_delta,
            "trend_text": _trend_text(recent_delta if recent_delta is not None else baseline_delta),
            "history_text": history_text,
            "score_points": score_points,
            "curve_position": _clamp(display_score, 0, 100),
            "curve_height": round(curve_height, 1),
            "is_estimate": latest_score is None,
        })

    subject_rows.sort(
        key=lambda row: (
            row["readiness_score"],
            row["score"] if row["score"] is not None else -1,
            row["avg_confidence"],
        ),
        reverse=True,
    )
    return subject_rows


def _build_subject_pyramid(subject_rows):
    tiers = [
        ("Apex", "Closest subjects to a secure Grade 9 track.", 1),
        ("Strong", "Subjects that are within reach with steady gains.", 2),
        ("Building", "Subjects that need consistent lift over the next cycle.", 3),
        ("Recovery", "Subjects needing the most score movement.", max(0, len(subject_rows) - 6)),
    ]
    pyramid = []
    index = 0
    for label, description, count in tiers:
        if count <= 0:
            continue
        tier_subjects = subject_rows[index:index + count]
        if not tier_subjects:
            continue
        pyramid.append({
            "label": label,
            "description": description,
            "subjects": tier_subjects,
        })
        index += count
    return pyramid


def _build_grade9_curve(subject_rows):
    bands = [
        {"label": "Recovery", "range_label": "0-49%", "minimum": 0, "maximum": 49},
        {"label": "Developing", "range_label": "50-64%", "minimum": 50, "maximum": 64},
        {"label": "Secure", "range_label": "65-79%", "minimum": 65, "maximum": 79},
        {"label": "Grade 8 edge", "range_label": "80-89%", "minimum": 80, "maximum": 89},
        {"label": "Grade 9 target", "range_label": "90-100%", "minimum": 90, "maximum": 100},
    ]
    for band in bands:
        band_subjects = [
            row["short_subject"]
            for row in subject_rows
            if row["score"] is not None and band["minimum"] <= row["score"] <= band["maximum"]
        ]
        band["subjects"] = band_subjects
        band["count"] = len(band_subjects)

    markers = [
        {
            "subject": row["subject"],
            "short_subject": row["short_subject"],
            "score": row["score"],
            "display_score": row["display_score"],
            "position": row["curve_position"],
            "height": row["curve_height"],
            "is_estimate": row["is_estimate"],
            "gap_label": row["gap_label"],
            "trend_text": row["trend_text"],
        }
        for row in subject_rows
    ]
    return {
        "target_score": GRADE9_TARGET_SCORE,
        "mean_score": NORMAL_CURVE_MEAN,
        "bands": bands,
        "markers": markers,
    }


def _build_improvement_snapshot(subject_rows):
    rows = [row for row in subject_rows if row["score_points"]]
    rows.sort(
        key=lambda row: (
            row["baseline_delta"] if row["baseline_delta"] is not None else -999,
            row["recent_delta"] if row["recent_delta"] is not None else -999,
            row["score"] if row["score"] is not None else -1,
        ),
        reverse=True,
    )
    return rows

def default_daily_targets():
    return [
        "Complete homework before extra revision.",
        "Do one focused STEM block.",
        "Complete the 10-minute daily test.",
        "Correct every mistake immediately.",
        "Read for 15–20 minutes.",
        "Pack your bag before bedtime.",
        "Aim for 8–9 hours of sleep.",
    ]

def daily_targets_from_score(score):
    targets = default_daily_targets()
    if score < 70:
        targets.insert(1, "Put your phone away during study blocks.")
        targets.insert(4, "Write one sentence explaining each mistake.")
    if score >= 70:
        targets.append("Try one stretch question beyond class level.")
    if score >= 85:
        targets.append("Teach one concept aloud to prove mastery.")
    return targets

def estimate_grade9_trajectory(daily_logs, subject_logs, subjects=None, stem_subjects=None):
    subjects = subjects or SUBJECTS
    stem_subjects = set(stem_subjects or STEM_SUBJECTS)
    if not daily_logs:
        return {
            "score": 50,
            "status": "Not enough evidence yet",
            "forecast": "Log at least 5 days so the app can judge your Grade 9 trajectory more fairly.",
            "daily_targets": default_daily_targets(),
        }

    days = len(daily_logs)
    avg_sleep = sum(x["sleep_hours"] for x in daily_logs) / days
    avg_focus = sum(x["focus"] for x in daily_logs) / days
    avg_revision = sum(x["revision_minutes"] for x in daily_logs) / days
    avg_homework = sum(x["homework_minutes"] for x in daily_logs) / days
    avg_reading = sum(x["reading_minutes"] for x in daily_logs) / days
    avg_distractions = sum(x["distractions_minutes"] for x in daily_logs) / days

    subject_minutes = defaultdict(int)
    subject_confidence = defaultdict(list)
    subject_scores = defaultdict(list)

    for row in subject_logs:
        subject_minutes[row["subject"]] += row["study_minutes"]
        subject_confidence[row["subject"]].append(row["confidence"])
        if row.get("test_score") is not None:
            subject_scores[row["subject"]].append(row["test_score"])

    subjects_touched = len([s for s in subjects if subject_minutes.get(s, 0) > 0])
    stem_minutes = sum(subject_minutes.get(s, 0) for s in stem_subjects)
    total_subject_minutes = sum(subject_minutes.values()) or 1
    stem_ratio = stem_minutes / total_subject_minutes

    all_scores = [score for scores in subject_scores.values() for score in scores]
    avg_test_score = sum(all_scores) / len(all_scores) if all_scores else 70

    score = 0
    score += min(20, avg_sleep / 8.5 * 20)
    score += min(15, avg_focus / 5 * 15)
    score += min(20, avg_revision / 45 * 20)
    score += min(10, avg_homework / 45 * 10)
    score += min(10, avg_reading / 20 * 10)
    score += min(10, subjects_touched / 8 * 10)
    score += min(10, stem_ratio / 0.45 * 10)
    score += min(5, avg_test_score / 90 * 5)

    if avg_distractions > avg_revision:
        score -= 10

    score = max(0, min(100, round(score)))

    if score >= 85:
        status = "Strong Grade 9 trajectory"
        forecast = "You are building habits suitable for straight 9s. Keep consistency and gradually increase challenge."
    elif score >= 70:
        status = "Possible, but consistency matters"
        forecast = "Straight 9s are realistic if you keep this up and close weak-topic gaps early."
    elif score >= 55:
        status = "At risk"
        forecast = "Straight 9s are still possible because you are in Year 8, but your daily system needs tightening."
    else:
        status = "Urgent reset needed"
        forecast = "Straight 9s are not ruled out, but your current routine is not yet strong enough."

    return {
        "score": score,
        "status": status,
        "forecast": forecast,
        "daily_targets": daily_targets_from_score(score),
    }

def analyse_week(daily_logs, subject_logs, subjects=None, stem_subjects=None):
    subjects = subjects or SUBJECTS
    stem_subjects = set(stem_subjects or STEM_SUBJECTS)
    trajectory = estimate_grade9_trajectory(daily_logs, subject_logs, subjects=subjects, stem_subjects=stem_subjects)
    subject_performance = _build_subject_performance(subjects, subject_logs, stem_subjects)
    subject_pyramid = _build_subject_pyramid(subject_performance)
    grade9_curve = _build_grade9_curve(subject_performance)
    improvement_rows = _build_improvement_snapshot(subject_performance)

    if not daily_logs:
        fallback_priorities = [subject for subject in ["Maths", "Science", "Biology", "Further Maths"] if subject in subjects]
        return {
            "summary": "No logs yet. Start by recording today honestly.",
            "weak_subjects": fallback_priorities or list(subjects[:4]),
            "priority_subjects": fallback_priorities or list(subjects[:4]),
            "warnings": ["Log at least 5 days for stronger recommendations."],
            "metrics": {},
            "trajectory": trajectory,
            "subjects": list(subjects),
            "stem_subjects": sorted(stem_subjects),
            "subject_performance": subject_performance,
            "subject_pyramid": subject_pyramid,
            "grade9_curve": grade9_curve,
            "improvement_rows": improvement_rows,
        }

    total_revision = sum(x["revision_minutes"] for x in daily_logs)
    avg_sleep = sum(x["sleep_hours"] for x in daily_logs) / len(daily_logs)
    avg_focus = sum(x["focus"] for x in daily_logs) / len(daily_logs)
    total_distractions = sum(x["distractions_minutes"] for x in daily_logs)

    subject_minutes = defaultdict(int)
    subject_conf = defaultdict(list)

    for row in subject_logs:
        subject_minutes[row["subject"]] += row["study_minutes"]
        subject_conf[row["subject"]].append(row["confidence"])

    all_scores = [row["test_score"] for row in subject_logs if row.get("test_score") is not None]
    avg_test_score = sum(all_scores) / len(all_scores) if all_scores else None

    weakness_scores = {}
    for subject in subjects:
        minutes = subject_minutes.get(subject, 0)
        confs = subject_conf.get(subject, [3])
        avg_conf = sum(confs) / len(confs)
        stem_boost = 1.4 if subject in stem_subjects else 1.0
        weakness_scores[subject] = ((6 - avg_conf) * 25 + max(0, 90 - minutes)) * stem_boost

    weak_subjects = sorted(weakness_scores, key=weakness_scores.get, reverse=True)[:5]

    warnings = []
    if avg_sleep < 8:
        warnings.append("Sleep is below the ideal range for learning. Protect bedtime before adding more revision.")
    if avg_focus < 3:
        warnings.append("Focus ratings are low. Use 25-minute blocks with 5-minute breaks.")
    if total_distractions > total_revision:
        warnings.append("Distraction time is higher than revision time. Use phone-away study blocks.")
    if total_revision < 240 and len(daily_logs) >= 5:
        warnings.append("Weekly revision is light for a Grade 9 trajectory. Add small daily blocks.")

    summary = (
        f"Recent average sleep: {avg_sleep:.1f}h. "
        f"Average focus: {avg_focus:.1f}/5. "
        f"Recent revision: {total_revision} minutes. "
        + (
            f"Recent recorded paper average: {avg_test_score:.0f}%. "
            if avg_test_score is not None
            else ""
        )
        + f"Main priorities: {', '.join(weak_subjects[:3])}. "
        + f"Grade 9 trajectory: {trajectory['status']} ({trajectory['score']}/100)."
    )

    return {
        "summary": summary,
        "weak_subjects": weak_subjects,
        "priority_subjects": weak_subjects,
        "warnings": warnings,
        "metrics": {
            "avg_sleep": round(avg_sleep, 1),
            "avg_focus": round(avg_focus, 1),
            "total_revision": total_revision,
            "total_distractions": total_distractions,
            "avg_test_score": round(avg_test_score, 1) if avg_test_score is not None else None,
        },
        "trajectory": trajectory,
        "subjects": list(subjects),
        "stem_subjects": sorted(stem_subjects),
        "subject_performance": subject_performance,
        "subject_pyramid": subject_pyramid,
        "grade9_curve": grade9_curve,
        "improvement_rows": improvement_rows,
    }

def next_day_name(log_date=None):
    if log_date is None:
        d = datetime.now().date() + timedelta(days=1)
    else:
        d = datetime.fromisoformat(log_date).date() + timedelta(days=1)
    return d.strftime("%A"), d.isoformat()

def generate_next_day_timetable(analysis, day_name):
    priorities = analysis["priority_subjects"]
    stem_subjects = set(analysis.get("stem_subjects", STEM_SUBJECTS))
    stem = [s for s in priorities if s in stem_subjects]
    non_stem = [s for s in priorities if s not in stem_subjects]
    ordered = (stem + non_stem + ["English", "German", "French"])[:5]

    timetable = [
        ("06:15–06:45", "Wake, breakfast, bag check, 5-minute memory recap"),
        ("07:00–16:30", "School day + school run"),
    ]

    if day_name == "Monday":
        timetable.extend([
            ("16:30–17:00", "Snack, reset, no phone scrolling"),
            ("17:00–17:25", f"Focused STEM block: {ordered[0] if ordered else 'Maths'}"),
            ("17:25–17:35", "Break"),
            ("17:35–18:00", f"Mini block: {ordered[1] if len(ordered) > 1 else 'Science'}"),
            ("18:00–18:35", "Dinner + cadets prep"),
            ("19:00–21:30", "Cadets"),
            ("21:30–21:45", "Pack bag, hygiene, quick reflection"),
            ("21:45", "Bedtime target"),
        ])
    else:
        timetable.extend([
            ("16:30–17:00", "Snack, rest, organise books"),
            ("17:00–17:30", f"Priority block 1: {ordered[0] if ordered else 'Maths'}"),
            ("17:30–17:40", "Break"),
            ("17:40–18:10", f"Priority block 2: {ordered[1] if len(ordered) > 1 else 'Science'}"),
            ("18:10–18:40", "Dinner / family time"),
            ("18:40–19:05", f"Homework catch-up: {ordered[2] if len(ordered) > 2 else 'English'}"),
            ("19:05–19:15", "10-minute daily mini test"),
            ("19:15–19:35", "Mark test + note one mistake pattern"),
            ("19:35–20:00", "Reading / English Literature quotation or vocabulary"),
            ("20:00–20:30", "Free time"),
            ("20:30–21:00", "Pack bag + light review cards"),
            ("21:45", "Bedtime target"),
        ])
    return timetable

def generate_weekend_plan(analysis):
    priorities = analysis["priority_subjects"] + ["Maths", "Science", "English"]
    return [
        ("Saturday 09:30–10:10", f"Deep work: {priorities[0]}"),
        ("Saturday 10:20–11:00", f"Deep work: {priorities[1]}"),
        ("Saturday 11:10–11:30", "10-minute test + correction log"),
        ("Saturday 14:00–14:30", "Reading or English Literature quote bank"),
        ("Saturday 16:00–16:30", "Language rotation: Latin/German/French vocabulary"),
        ("Sunday 10:00–10:40", f"STEM mastery: {priorities[2]}"),
        ("Sunday 10:50–11:20", "Homework completion and bag organisation"),
        ("Sunday 16:00–16:30", "Plan the school week: deadlines, weak topics, revision slots"),
        ("Sunday 19:00–19:20", "Light retrieval practice only; no heavy cramming"),
    ]
