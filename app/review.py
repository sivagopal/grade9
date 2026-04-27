from app.resources import recommend_topic_videos, related_areas_for_topic


def build_wrong_answer_review(subject, questions, score_map):
    reviews = []
    for question in questions:
        result = score_map.get(question["id"])
        if not result:
            continue
        score = float(result["score"])
        max_score = float(question["marks"])
        if score >= max_score:
            continue
        reviews.append(
            {
                "question_id": question["id"],
                "topic": question["topic"],
                "question": question["question"],
                "asset_path": question.get("asset_path"),
                "score": score,
                "max_score": max_score,
                "answer": question["answer"],
                "explanation": question.get("explanation") or _fallback_explanation(question),
                "video_script": _build_video_script(question),
                "videos": recommend_topic_videos(subject, question["topic"]),
                "related_areas": related_areas_for_topic(question["topic"]),
            }
        )
    return reviews


def _fallback_explanation(question):
    topic = question["topic"].lower()
    if "coordinate" in topic:
        return (
            "Translate the picture into algebra first. Identify the key coordinates or equations, "
            "use the relevant geometry fact, and then verify that the final coordinate or area is consistent with the graph."
        )
    if "matrice" in topic:
        return (
            "Work entry by entry or track each point systematically. In matrix questions, order matters, "
            "so check whether you are transforming vectors, multiplying matrices, or interpreting a geometric movement."
        )
    if "binomial" in topic:
        return (
            "Use the coefficient pattern carefully, then handle powers and signs one term at a time. "
            "Most errors come from a missed coefficient, an incorrect power, or a sign slip."
        )
    return (
        "Rebuild the method, not just the final answer. Identify the mathematical structure, "
        "carry out each step cleanly, and justify why the method fits this question."
    )


def _build_video_script(question):
    return [
        f"State the goal: solve a {question['topic']} problem without guessing.",
        "Show the key structure from the diagram or algebra and name the theorem, rule, or pattern being used.",
        "Work through the calculation step by step, then finish by checking that the answer is sensible.",
    ]
