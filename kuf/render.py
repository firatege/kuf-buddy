"""Draw Küf and his speech bubble for the terminal."""

import textwrap
import unicodedata

from .buddies import tint as buddy_tint
from .emotes import EMOTES

SPRITE_COLS = 13
BUBBLE_TEXT_COLS = 56
BUBBLE_MAX_LINES = 3   # per paragraph; a stacked exchange has two

RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
MOOD_COLOR = {
    "comfy": "\033[38;5;137m",    # mud brown
    "sleepy": "\033[38;5;102m",   # dusty grey
    "grumpy": "\033[38;5;106m",   # mold green
    "furious": "\033[38;5;167m",  # angry red
}
EMOTE_MOOD = {"rage": "furious", "tableflip": "furious", "middle-finger": "furious",
              "roast": "grumpy", "sus": "grumpy", "facepalm": "grumpy", "puke": "grumpy",
              "dead": "sleepy", "sleep": "sleepy", "cry": "sleepy"}


def width(text: str) -> int:
    total = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total


def pad(text: str, cols: int) -> str:
    return text + " " * max(0, cols - width(text))


MIRROR = dict(zip("()[]{}<>/\\╯╰╭╮┗┛┏┓ᕦᕤ☞☜ﾉヽノ彡ミ▐▌▖▗▘▝▙▟▛▜«»\u0300\u0301",
                  ")(][}{><\\/╰╯╮╭┛┗┓┏ᕤᕦ☜☞ヽﾉヽミ彡▌▐▗▖▝▘▟▙▜▛»«\u0301\u0300"))


def _graphemes(text: str) -> list[str]:
    """Split into base characters with their combining marks attached."""
    clusters: list[str] = []
    for ch in text:
        if clusters and unicodedata.combining(ch):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    return clusters


def mirror(rows: list[str]) -> list[str]:
    """Flip a sprite horizontally so he faces the other way."""
    cols = max(width(r) for r in rows)
    return ["".join("".join(MIRROR.get(c, c) for c in g) for g in reversed(_graphemes(pad(r, cols))))
            for r in rows]


def frame(emote: str, tick: int, facing: str = "right") -> list[str]:
    frames = EMOTES[emote]["frames"]
    rows = frames[tick % len(frames)]
    return mirror(rows) if facing == "left" else rows


def _wrap(paragraph: str) -> list[str]:
    wrapped = textwrap.wrap(paragraph, BUBBLE_TEXT_COLS) or [""]
    if len(wrapped) <= BUBBLE_MAX_LINES:
        return wrapped
    kept = wrapped[:BUBBLE_MAX_LINES]
    return kept[:-1] + [kept[-1][: BUBBLE_TEXT_COLS - 1] + "…"]


def bubble(line: str, name: str = "Küf") -> list[str]:
    paragraphs = [_wrap(paragraph) for paragraph in line.split("\n")]
    inner = max(width(row) for rows in paragraphs for row in rows)
    label = f"─ {name} "
    inner = max(inner, width(label) - 2)
    top = f"╭{label}{'─' * (inner + 2 - width(label))}╮"
    divider = f"├{'┄' * (inner + 2)}┤"
    body = [row for i, rows in enumerate(paragraphs)
            for row in ([divider] if i else []) + [f"│ {pad(w, inner)} │" for w in rows]]
    bottom = f"╰{'─' * (inner + 2)}╯"
    return [top, *body, bottom]


def compose(emote: str, line: str, tick: int, mood: str | None = None,
            color: bool = True, name: str = "Küf", facing: str = "right") -> str:
    """Goblin plus speech bubble. Facing right he sits left of the bubble; facing left
    (toward a neighbor on the left) he's mirrored and sits right of it."""
    sprite = frame(emote, tick, facing)
    speech = bubble(line, name)
    rows = max(len(sprite), len(speech))
    sprite = [""] * (rows - len(sprite)) + sprite     # sit him on the bottom
    speech = speech + [""] * (rows - len(speech))
    face_row = rows - 3
    feeling = mood or EMOTE_MOOD.get(emote, "comfy")
    tint = "" if not color else (MOOD_COLOR["furious"] if feeling == "furious" else buddy_tint(name))
    dim, reset = (DIM, RESET) if color else ("", "")

    bubble_cols = max(width(b) for b in speech)
    out = []
    for i, (s, b) in enumerate(zip(sprite, speech)):
        if facing == "left":
            if i == face_row and b.endswith(("│", "┤")):
                b = b[:-1] + ">"   # tail points at his mouth, now on his left
            text = f"{dim}{pad(b, bubble_cols)}{reset} " if b else " " * (bubble_cols + 1)
            out.append(f"{text}{tint}{s}{reset}".rstrip() if color else f"{text}{s}".rstrip())
        else:
            if i == face_row and b.startswith(("│", "├")):
                b = "<" + b[1:]    # the bubble's tail points at his mouth
            left = f"{tint}{pad(s, SPRITE_COLS)}{reset}"
            out.append(f"{left} {dim}{b}{reset}" if b else left)
    return "\n".join(out)
