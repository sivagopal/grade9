import re

RESOURCE_MAP = {
    "Biology": [
        ("BBC Bitesize GCSE Biology", "https://www.bbc.co.uk/bitesize/subjects/z9ddmp3"),
        ("Oak National Academy KS4 Biology", "https://www.thenational.academy/teachers/key-stages/ks4/subjects/biology"),
        ("Khan Academy Biology", "https://www.khanacademy.org/science/biology"),
        ("FreeScienceLessons YouTube", "https://www.youtube.com/@Freesciencelessons"),
    ],
    "Science": [
        ("BBC Bitesize GCSE Combined Science", "https://www.bbc.co.uk/bitesize/subjects/zrkw2hv"),
        ("Oak National Academy KS4 Combined Science", "https://www.thenational.academy/teachers/key-stages/ks4/subjects/combined-science"),
        ("Khan Academy Science", "https://www.khanacademy.org/science"),
        ("Cognito YouTube", "https://www.youtube.com/@Cognitoedu"),
    ],
    "Maths": [
        ("BBC Bitesize GCSE Maths", "https://www.bbc.co.uk/bitesize/subjects/z38pycw"),
        ("Oak National Academy KS4 Maths Higher", "https://www.thenational.academy/teachers/programmes/maths-secondary-ks4-higher/units"),
        ("Khan Academy Maths", "https://www.khanacademy.org/math"),
        ("The GCSE Maths Tutor YouTube", "https://www.youtube.com/@TheGCSEMathsTutor"),
        ("Corbettmaths", "https://corbettmaths.com/"),
    ],
    "Further Maths": [
        ("1st Class Maths Further Maths", "https://www.1stclassmaths.com/aqa-level-2-further-maths"),
        ("Khan Academy Algebra", "https://www.khanacademy.org/math/algebra"),
        ("Khan Academy Geometry", "https://www.khanacademy.org/math/geometry-home"),
    ],
    "English": [
        ("BBC Bitesize GCSE English Language", "https://www.bbc.co.uk/bitesize/subjects/zr9d7ty"),
        ("Oak National Academy KS4 English", "https://www.thenational.academy/teachers/programmes/english-secondary-ks4-aqa/units"),
        ("Mr Bruff YouTube", "https://www.youtube.com/@mrbruff"),
        ("Mr Salles YouTube", "https://www.youtube.com/@MrSallesTeachesEnglish"),
    ],
    "English Literature": [
        ("BBC Bitesize GCSE English Literature", "https://www.bbc.co.uk/bitesize/subjects/zckw2hv"),
        ("Oak National Academy KS4 English", "https://www.thenational.academy/teachers/programmes/english-secondary-ks4-aqa/units"),
        ("Mr Bruff YouTube", "https://www.youtube.com/@mrbruff"),
    ],
    "Latin": [
        ("Cambridge Latin Course", "https://www.cambridgescp.com/"),
        ("BBC Bitesize Latin", "https://www.bbc.co.uk/bitesize/subjects/z4dqxnb"),
        ("LatinTutorial YouTube", "https://www.youtube.com/@latintutorial"),
    ],
    "German": [
        ("BBC Bitesize GCSE German", "https://www.bbc.co.uk/bitesize/subjects/z8j2tfr"),
        ("Easy German YouTube", "https://www.youtube.com/@EasyGerman"),
    ],
    "French": [
        ("BBC Bitesize GCSE French", "https://www.bbc.co.uk/bitesize/subjects/z9dqxnb"),
        ("Easy French YouTube", "https://www.youtube.com/@EasyFrench"),
    ],
    "Geography": [
        ("BBC Bitesize GCSE Geography", "https://www.bbc.co.uk/bitesize/subjects/zkw76sg"),
        ("Oak National Academy KS4 Geography", "https://www.thenational.academy/teachers/key-stages/ks4/subjects/geography"),
        ("Time for Geography YouTube", "https://www.youtube.com/@TimeforGeography"),
    ],
    "Business Studies": [
        ("BBC Bitesize GCSE Business", "https://www.bbc.co.uk/bitesize/subjects/zpsvr82"),
        ("Two Teachers Business YouTube", "https://www.youtube.com/@TwoTeachers"),
        ("Tutor2u Business", "https://www.tutor2u.net/business"),
    ],
    "Computing / 12th Subject": [
        ("BBC Bitesize GCSE Computer Science", "https://www.bbc.co.uk/bitesize/subjects/z34k7ty"),
        ("Craig'n'Dave YouTube", "https://www.youtube.com/@craigndave"),
        ("Isaac Computer Science", "https://isaaccomputerscience.org/"),
    ],
}

TOPIC_VIDEO_MAP = {
    ("Maths", "Probability"): [
        ("The GCSE Maths Tutor: Probability", "https://www.youtube.com/results?search_query=gcse+maths+probability+the+gcse+maths+tutor"),
        ("Corbettmaths: Probability", "https://www.youtube.com/results?search_query=corbettmaths+probability"),
        ("GCSE Maths Probability Practice", "https://www.youtube.com/results?search_query=gcse+maths+probability+tree+diagrams"),
    ],
    ("Maths", "Statistics"): [
        ("The GCSE Maths Tutor: Statistics", "https://www.youtube.com/results?search_query=gcse+maths+statistics+the+gcse+maths+tutor"),
        ("Corbettmaths: Statistics", "https://www.youtube.com/results?search_query=corbettmaths+statistics"),
        ("GCSE Maths Averages and Range", "https://www.youtube.com/results?search_query=gcse+maths+mean+median+mode+range"),
    ],
    ("Maths", "Coordinate Geometry"): [
        ("Corbettmaths: Equation of a Line", "https://corbettmaths.com/2019/09/02/equation-of-a-line-videos/"),
        ("Corbettmaths: Area in Coordinates", "https://corbettmaths.com/2019/09/26/area-in-coordinates-videos/"),
        ("The GCSE Maths Tutor: Straight Line Graphs", "https://www.youtube.com/@TheGCSEMathsTutor"),
    ],
    ("Further Maths", "Matrices"): [
        ("Maths Genie: Matrices", "https://www.mathsgenie.co.uk/further.html"),
        ("Khan Academy: Matrix Transformations", "https://www.khanacademy.org/math/linear-algebra/matrix-transformations"),
        ("TLMaths YouTube", "https://www.youtube.com/@TLMaths"),
    ],
    ("Further Maths", "Binomial Expansion"): [
        ("Khan Academy: Binomial Theorem", "https://www.khanacademy.org/math/algebra2/polynomial-functions/binomial-theorem"),
        ("Maths Genie: Algebra Revision", "https://www.mathsgenie.co.uk/algebra.html"),
        ("TLMaths YouTube", "https://www.youtube.com/@TLMaths"),
    ],
}

RELATED_AREAS_MAP = {
    "Probability": [
        "Single-event probability",
        "Two-step events and tree diagrams",
        "Complements and checking total probability",
    ],
    "Statistics": [
        "Mean, median, mode, and range",
        "Reading tables and charts",
        "Choosing the right average for a data set",
    ],
    "Coordinate Geometry": [
        "Gradient and intercept form",
        "Simultaneous equations from graphs",
        "Area and midpoint arguments on coordinate axes",
    ],
    "Matrices": [
        "Transformations on the plane",
        "Composition of operations",
        "Inverse processes and undoing transformations",
    ],
    "Binomial Expansion": [
        "General term structure",
        "Powers and signs",
        "Coefficient extraction",
    ],
}


def _normalize_topic_label(value):
    return " ".join(str(value or "").strip().lower().split())


def _matches_any_pattern(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def _probability_signal(text):
    return _matches_any_pattern(
        text,
        [
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
        ],
    )


def _statistics_signal(text):
    return _matches_any_pattern(
        text,
        [
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
        ],
    )


def infer_focus_area(subject, topic, subtopic="", question_text=""):
    topic_text = str(topic or "").strip() or "General"
    subtopic_text = str(subtopic or "").strip()
    if subtopic_text:
        return subtopic_text

    normalized_subject = str(subject or "").strip()
    normalized_topic = _normalize_topic_label(topic_text)
    combined_text = " ".join([topic_text, subtopic_text, str(question_text or "")]).lower()

    if normalized_subject == "Maths" and normalized_topic == "statistics and probability":
        if _probability_signal(combined_text) and not _statistics_signal(combined_text):
            return "Probability"
        if _statistics_signal(combined_text) and not _probability_signal(combined_text):
            return "Statistics"

    return topic_text


def recommend_resources(priority_subjects, max_per_subject=3):
    result = []
    for subject in priority_subjects:
        for name, url in RESOURCE_MAP.get(subject, [])[:max_per_subject]:
            result.append((subject, name, url))
    return result


def recommend_topic_videos(subject, topic, max_items=3):
    focus_topic = infer_focus_area(subject, topic)
    direct = TOPIC_VIDEO_MAP.get((subject, focus_topic), [])
    if direct:
        return direct[:max_items]

    normalized = focus_topic.lower()
    for (mapped_subject, mapped_topic), resources in TOPIC_VIDEO_MAP.items():
        if mapped_subject == subject and mapped_topic.lower() in normalized:
            return resources[:max_items]
    return RESOURCE_MAP.get(subject, [])[:max_items]


def related_areas_for_topic(topic):
    direct = RELATED_AREAS_MAP.get(topic)
    if direct:
        return direct
    normalized = topic.lower()
    for mapped_topic, areas in RELATED_AREAS_MAP.items():
        if mapped_topic.lower() in normalized:
            return areas
    return ["Core method fluency", "Reasoned explanation", "Transfer to unfamiliar problems"]
