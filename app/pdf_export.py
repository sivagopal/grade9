from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.math_format import render_math_plain
from app.matplotlib_service import load_question_asset_image


PAGE_SIZE = (1240, 1754)
MARGIN = 72
LINE_SPACING = 12
SECTION_GAP = 26


def build_test_pdf(questions, title):
    pages = []
    page, draw, cursor_y = _new_page()
    cursor_y = _draw_title(draw, title, cursor_y)

    for index, question in enumerate(questions, 1):
        block_height = _estimate_question_block_height(question, draw)
        if cursor_y + block_height > PAGE_SIZE[1] - MARGIN:
            pages.append(page)
            page, draw, cursor_y = _new_page()
            cursor_y = _draw_title(draw, title, cursor_y)
        cursor_y = _draw_question_block(page, draw, question, index, cursor_y)
    pages.append(page)

    output = BytesIO()
    rgb_pages = [page.convert("RGB") for page in pages]
    rgb_pages[0].save(output, format="PDF", save_all=True, append_images=rgb_pages[1:])
    output.seek(0)
    return output.getvalue()


def build_mark_scheme_pdf(questions, title):
    pages = []
    mark_page, mark_draw, mark_y = _new_page()
    mark_y = _draw_title(mark_draw, f"{title} - Mark Scheme", mark_y)

    for index, question in enumerate(questions, 1):
        question_context = str(question.get("question", "")).strip()
        if len(question_context) > 90:
            question_context = question_context[:87].rstrip() + "..."
        heading_lines = _wrap_text(
            mark_draw,
            f"{index}. {question.get('topic', 'General')}: {render_math_plain(question_context)}",
            PAGE_SIZE[0] - MARGIN * 2,
            _small_font(),
        )
        answer_lines = _wrap_text(
            mark_draw,
            f"Answer: {render_math_plain(question['answer'])} ({question['marks']} marks)",
            PAGE_SIZE[0] - MARGIN * 2,
            _body_font(),
        )
        block_height = _text_height(heading_lines, _small_font()) + _text_height(answer_lines, _body_font()) + 22
        if mark_y + block_height > PAGE_SIZE[1] - MARGIN:
            pages.append(mark_page)
            mark_page, mark_draw, mark_y = _new_page()
            mark_y = _draw_title(mark_draw, f"{title} - Mark Scheme", mark_y)
        for line in heading_lines:
            mark_draw.text((MARGIN, mark_y), line, fill="#2f6b49", font=_small_font())
            mark_y += _line_height(_small_font())
        for line in answer_lines:
            mark_draw.text((MARGIN, mark_y), line, fill="#183022", font=_body_font())
            mark_y += _line_height(_body_font())
        mark_y += 22
    pages.append(mark_page)

    output = BytesIO()
    rgb_pages = [page.convert("RGB") for page in pages]
    rgb_pages[0].save(output, format="PDF", save_all=True, append_images=rgb_pages[1:])
    output.seek(0)
    return output.getvalue()


def _new_page():
    page = Image.new("RGB", PAGE_SIZE, color="#fbfdf9")
    draw = ImageDraw.Draw(page)
    return page, draw, MARGIN


def _draw_title(draw, title, cursor_y):
    draw.rounded_rectangle((MARGIN, cursor_y, PAGE_SIZE[0] - MARGIN, cursor_y + 92), radius=28, fill="#183a25")
    draw.text((MARGIN + 28, cursor_y + 18), title, fill="white", font=_title_font())
    return cursor_y + 120


def _draw_question_block(page, draw, question, index, cursor_y):
    heading = f"{index}. {question['subject']} | {question.get('topic', 'General')} | Difficulty {question.get('difficulty_level', 1)} | {question['marks']} marks"
    heading_lines = _wrap_text(draw, heading, PAGE_SIZE[0] - MARGIN * 2 - 32, _small_font())
    question_lines = _wrap_text(draw, render_math_plain(question["question"]), PAGE_SIZE[0] - MARGIN * 2 - 32, _body_font())
    asset = load_question_asset_image(question)
    block_height = _estimate_question_block_height(question, draw)
    draw.rounded_rectangle(
        (MARGIN, cursor_y, PAGE_SIZE[0] - MARGIN, cursor_y + block_height - 10),
        radius=24,
        fill="white",
        outline="#dcebdd",
        width=2,
    )
    text_y = cursor_y + 22
    for line in heading_lines:
        draw.text((MARGIN + 18, text_y), line, fill="#2f6b49", font=_small_font())
        text_y += _line_height(_small_font())
    text_y += 8
    for line in question_lines:
        draw.text((MARGIN + 18, text_y), line, fill="#183022", font=_body_font())
        text_y += _line_height(_body_font())
    text_y += 8
    if asset:
        image_max_width = PAGE_SIZE[0] - MARGIN * 2 - 36
        image_max_height = 420
        asset.thumbnail((image_max_width, image_max_height))
        page.paste(asset, (MARGIN + 18, text_y))
        text_y += asset.height + 18
    answer_space_top = text_y
    for offset in range(3):
        draw.line((MARGIN + 18, answer_space_top + offset * 42, PAGE_SIZE[0] - MARGIN - 18, answer_space_top + offset * 42), fill="#d7e7d9", width=3)
    return cursor_y + block_height + 14


def _estimate_question_block_height(question, draw):
    heading = f"1. {question['subject']} | {question.get('topic', 'General')} | Difficulty {question.get('difficulty_level', 1)} | {question['marks']} marks"
    heading_lines = _wrap_text(draw, heading, PAGE_SIZE[0] - MARGIN * 2 - 32, _small_font())
    question_lines = _wrap_text(draw, render_math_plain(question["question"]), PAGE_SIZE[0] - MARGIN * 2 - 32, _body_font())
    height = 22 + _text_height(heading_lines, _small_font()) + 8 + _text_height(question_lines, _body_font()) + 18 + 126
    asset = load_question_asset_image(question)
    if asset:
        image_max_width = PAGE_SIZE[0] - MARGIN * 2 - 36
        image_max_height = 420
        asset.thumbnail((image_max_width, image_max_height))
        height += asset.height + 18
    return height + 22


def _wrap_text(draw, text, max_width, font):
    words = str(text).split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _text_height(lines, font):
    return len(lines) * _line_height(font)


def _line_height(font):
    bbox = font.getbbox("Ag")
    return (bbox[3] - bbox[1]) + LINE_SPACING

def _title_font():
    return _font(30)


def _body_font():
    return _font(22)


def _small_font():
    return _font(18)


def _font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()
