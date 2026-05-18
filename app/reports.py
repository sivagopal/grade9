from datetime import date
from app.analyser import next_day_name, generate_next_day_timetable, generate_weekend_plan
from app.resources import recommend_resources

def build_daily_report(analysis):
    day_name, next_iso = next_day_name()
    timetable = generate_next_day_timetable(analysis, day_name)
    weekend = generate_weekend_plan(analysis)
    trajectory = analysis["trajectory"]
    resources = recommend_resources(analysis["priority_subjects"], max_per_subject=3)
    pyramid = analysis.get("subject_pyramid", [])
    curve = analysis.get("grade9_curve", {})
    improvement_rows = analysis.get("improvement_rows", [])

    lines = [
        f"GCSE Grade 9 Daily Report — {date.today().isoformat()}",
        "",
        "SUMMARY",
        analysis["summary"],
        "",
        "GRADE 9 TRAJECTORY",
        f"Score: {trajectory['score']}/100",
        f"Status: {trajectory['status']}",
        f"Forecast: {trajectory['forecast']}",
        "",
        "DAILY TARGETS",
    ]
    for target in trajectory["daily_targets"]:
        lines.append(f"- {target}")

    lines.extend(["", "PRIORITY SUBJECTS", ", ".join(analysis["priority_subjects"]), "", "WARNINGS"])
    if analysis["warnings"]:
        for warning in analysis["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- No major warnings today.")

    lines.extend(["", "SUBJECT PYRAMID"])
    for tier in pyramid:
        members = ", ".join(
            f"{row['subject']} ({row['score_label']}, {row['gap_label']})"
            for row in tier["subjects"]
        )
        lines.append(f"{tier['label']}: {members}")

    lines.extend(["", "GRADE 9 NORMAL CURVE"])
    lines.append(f"Target Grade 9 marker: {curve.get('target_score', 90)}%")
    for band in curve.get("bands", []):
        subjects = ", ".join(band["subjects"]) if band["subjects"] else "none yet"
        lines.append(f"{band['label']} [{band['range_label']}]: {subjects}")

    lines.extend(["", "IMPROVEMENT DATA POINTS"])
    if improvement_rows:
        for row in improvement_rows:
            latest = row["score_label"]
            trend = row["trend_text"]
            baseline = (
                f"Baseline delta {int(row['baseline_delta'])} pts"
                if row["baseline_delta"] is not None
                else "Single scored datapoint"
            )
            lines.append(
                f"- {row['subject']}: {row['history_text']} | latest {latest} | {trend} | {baseline} | {row['gap_label']}"
            )
    else:
        lines.append("- No recorded paper scores yet.")

    lines.extend(["", f"NEXT DAY PLAN — {day_name} {next_iso}"])
    for time, task in timetable:
        lines.append(f"{time}: {task}")

    lines.extend(["", "FREE RESOURCES FOR WEAK AREAS"])
    for subject, name, url in resources:
        lines.append(f"- {subject}: {name} — {url}")

    lines.extend(["", "WEEKEND PLAN"])
    for time, task in weekend:
        lines.append(f"{time}: {task}")

    return "\n".join(lines)
