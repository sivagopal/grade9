from datetime import date
from app.analyser import next_day_name, generate_next_day_timetable, generate_weekend_plan
from app.resources import recommend_resources

def build_daily_report(analysis):
    day_name, next_iso = next_day_name()
    timetable = generate_next_day_timetable(analysis, day_name)
    weekend = generate_weekend_plan(analysis)
    trajectory = analysis["trajectory"]
    resources = recommend_resources(analysis["priority_subjects"], max_per_subject=3)

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
