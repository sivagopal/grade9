import re
from html import escape

from markupsafe import Markup


_SUPERSCRIPT_MAP = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "+": "⁺",
    "-": "⁻",
    "=": "⁼",
    "(": "⁽",
    ")": "⁾",
    "n": "ⁿ",
    "i": "ⁱ",
}

_SUBSCRIPT_MAP = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
    "+": "₊",
    "-": "₋",
    "=": "₌",
    "(": "₍",
    ")": "₎",
}

_GREEK_MAP = {
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ε",
    r"\theta": "θ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\pi": "π",
    r"\sigma": "σ",
    r"\phi": "φ",
    r"\omega": "ω",
    r"\Delta": "Δ",
    r"\Sigma": "Σ",
    r"\theta": "θ",
}


def render_math_plain(text):
    return _render_math(str(text or ""), mode="plain")


def render_math_html(text):
    return Markup(_render_math(str(text or ""), mode="html"))


def _render_math(text, mode):
    rendered = str(text or "")
    rendered = rendered.replace("\\(", "").replace("\\)", "")
    rendered = rendered.replace("\\[", "").replace("\\]", "")
    rendered = rendered.replace("\\left", "").replace("\\right", "")
    rendered = _replace_text_blocks(rendered)
    rendered = _replace_common_commands(rendered)
    rendered = _replace_sqrt_blocks(rendered, mode=mode)
    rendered = _replace_frac_blocks(rendered, mode=mode)
    rendered = _replace_power_blocks(rendered, mode=mode)
    rendered = _replace_subscript_blocks(rendered, mode=mode)
    return rendered if mode == "plain" else _preserve_line_breaks(rendered)


def _replace_text_blocks(text):
    return re.sub(r"\\text\{([^{}]*)\}", lambda match: match.group(1), text)


def _replace_common_commands(text):
    replacements = {
        r"\times": "×",
        r"\div": "÷",
        r"\cdot": "·",
        r"\cdots": "⋯",
        r"\pm": "±",
        r"\mp": "∓",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\equiv": "≡",
        r"\propto": "∝",
        r"\leq": "≤",
        r"\geq": "≥",
        r"\lt": "<",
        r"\gt": ">",
        r"\infty": "∞",
        r"\to": "→",
        r"\rightarrow": "→",
        r"\leftarrow": "←",
        r"\therefore": "∴",
        r"\because": "∵",
        r"\angle": "∠",
        r"\triangle": "△",
        r"\parallel": "∥",
        r"\perp": "⟂",
        r"\%": "%",
        r"\degree": "°",
        r"\circ": "°",
    }
    rendered = text
    for source, target in replacements.items():
        rendered = rendered.replace(source, target)
    for source, target in _GREEK_MAP.items():
        rendered = rendered.replace(source, target)
    return rendered


def _replace_sqrt_blocks(text, mode):
    pattern = re.compile(r"\\sqrt\{([^{}]+)\}|\\sqrt([A-Za-z0-9]+)")
    return pattern.sub(lambda match: _format_sqrt(match.group(1) or match.group(2), mode=mode), text)


def _replace_frac_blocks(text, mode):
    pattern = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")
    rendered = text
    while True:
        match = pattern.search(rendered)
        if not match:
            return rendered
        numerator = _render_math(match.group(1), mode=mode)
        denominator = _render_math(match.group(2), mode=mode)
        if mode == "html":
            replacement = (
                '<span class="math-frac">'
                f'<span class="math-num">{numerator}</span>'
                f'<span class="math-den">{denominator}</span>'
                "</span>"
            )
        else:
            replacement = _plain_fraction(numerator, denominator)
        rendered = rendered[: match.start()] + replacement + rendered[match.end() :]


def _replace_power_blocks(text, mode):
    pattern = re.compile(r"\^\{([^{}]+)\}|\^([A-Za-z0-9+\-()=]+)")
    return pattern.sub(lambda match: _format_exponent(match.group(1) or match.group(2), mode=mode), text)


def _replace_subscript_blocks(text, mode):
    pattern = re.compile(r"_\{([^{}]+)\}|_([A-Za-z0-9+\-()=]+)")
    return pattern.sub(lambda match: _format_subscript(match.group(1) or match.group(2), mode=mode), text)


def _format_exponent(content, mode):
    if mode == "html":
        return f"<sup>{escape(content)}</sup>"
    converted = "".join(_SUPERSCRIPT_MAP.get(char, "") for char in content)
    return converted if converted and len(converted) == len(content) else f"^({content})"


def _format_subscript(content, mode):
    if mode == "html":
        return f"<sub>{escape(content)}</sub>"
    converted = "".join(_SUBSCRIPT_MAP.get(char, "") for char in content)
    return converted if converted and len(converted) == len(content) else f"_({content})"


def _preserve_line_breaks(text):
    return text.replace("\n", "<br>")


def _format_sqrt(content, mode):
    inner = _render_math(content, mode=mode)
    if mode == "html":
        return f"√<span class=\"math-root\">{inner}</span>"
    return f"√({inner})"


def _plain_fraction(numerator, denominator):
    numerator_text = str(numerator).strip()
    denominator_text = str(denominator).strip()
    vulgar_key = (numerator_text, denominator_text)
    vulgar_map = {
        ("1", "2"): "½",
        ("1", "3"): "⅓",
        ("2", "3"): "⅔",
        ("1", "4"): "¼",
        ("3", "4"): "¾",
        ("1", "5"): "⅕",
        ("2", "5"): "⅖",
        ("3", "5"): "⅗",
        ("4", "5"): "⅘",
        ("1", "6"): "⅙",
        ("5", "6"): "⅚",
        ("1", "8"): "⅛",
        ("3", "8"): "⅜",
        ("5", "8"): "⅝",
        ("7", "8"): "⅞",
    }
    if vulgar_key in vulgar_map:
        return vulgar_map[vulgar_key]
    if re.fullmatch(r"[0-9+\-()=]+", numerator_text) and re.fullmatch(r"[0-9+\-()=]+", denominator_text):
        num_unicode = "".join(_SUPERSCRIPT_MAP.get(char, char) for char in numerator_text)
        den_unicode = "".join(_SUBSCRIPT_MAP.get(char, char) for char in denominator_text)
        return f"{num_unicode}⁄{den_unicode}"
    return f"({numerator_text})/({denominator_text})"
