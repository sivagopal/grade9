from collections import defaultdict
from datetime import datetime, timedelta
from app.config import SUBJECTS, STEM_SUBJECTS

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

def estimate_grade9_trajectory(daily_logs, subject_logs):
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

    subjects_touched = len([s for s in SUBJECTS if subject_minutes.get(s, 0) > 0])
    stem_minutes = sum(subject_minutes.get(s, 0) for s in STEM_SUBJECTS)
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

def analyse_week(daily_logs, subject_logs):
    trajectory = estimate_grade9_trajectory(daily_logs, subject_logs)

    if not daily_logs:
        return {
            "summary": "No logs yet. Start by recording today honestly.",
            "weak_subjects": ["Maths", "Science", "Biology", "Further Maths"],
            "priority_subjects": ["Maths", "Science", "Biology", "Further Maths"],
            "warnings": ["Log at least 5 days for stronger recommendations."],
            "metrics": {},
            "trajectory": trajectory,
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

    weakness_scores = {}
    for subject in SUBJECTS:
        minutes = subject_minutes.get(subject, 0)
        confs = subject_conf.get(subject, [3])
        avg_conf = sum(confs) / len(confs)
        stem_boost = 1.4 if subject in STEM_SUBJECTS else 1.0
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
        f"Main priorities: {', '.join(weak_subjects[:3])}. "
        f"Grade 9 trajectory: {trajectory['status']} ({trajectory['score']}/100)."
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
        },
        "trajectory": trajectory,
    }

def next_day_name(log_date=None):
    if log_date is None:
        d = datetime.now().date() + timedelta(days=1)
    else:
        d = datetime.fromisoformat(log_date).date() + timedelta(days=1)
    return d.strftime("%A"), d.isoformat()

def generate_next_day_timetable(analysis, day_name):
    priorities = analysis["priority_subjects"]
    stem = [s for s in priorities if s in STEM_SUBJECTS]
    non_stem = [s for s in priorities if s not in STEM_SUBJECTS]
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
