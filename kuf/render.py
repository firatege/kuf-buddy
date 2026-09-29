"""Draw Küf and his speech bubble for the terminal."""

import textwrap
import unicodedata

from .emotes import EMOTES

SPRITE_COLS = 13
BUBBLE_TEXT_COLS = 56
BUBBLE_MAX_LINES = 3

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


def frame(emote: str, tick: int) -> list[str]:
    frames = EMOTES[emote]["frames"]
    return frames[tick % len(frames)]


def bubble(line: str) -> list[str]:
    wrapped = textwrap.wrap(line, BUBBLE_TEXT_COLS) or [""]
    if len(wrapped) > BUBBLE_MAX_LINES:
        wrapped = wrapped[:BUBBLE_MAX_LINES]
        wrapped[-1] = wrapped[-1][: BUBBLE_TEXT_COLS - 1] + "…"
    inner = max(width(w) for w in wrapped)
    label = "─ Küf "
    top = f"╭{label}{'─' * max(0, inner + 2 - len(label))}╮"
    body = [f"│ {pad(w, inner)} │" for w in wrapped]
    bottom = f"╰{'─' * (inner + 2)}╯"
    return [top, *body, bottom]


def compose(emote: str, line: str, tick: int, mood: str | None = None, color: bool = True) -> str:
    sprite = frame(emote, tick)
    speech = bubble(line)
    rows = max(len(sprite), len(speech))
    sprite = [""] * (rows - len(sprite)) + sprite     # sit him on the bottom
    speech = speech + [""] * (rows - len(speech))
    face_row = rows - 3
    tint = MOOD_COLOR[mood or EMOTE_MOOD.get(emote, "comfy")] if color else ""
    dim, reset = (DIM, RESET) if color else ("", "")

    out = []
    for i, (s, b) in enumerate(zip(sprite, speech)):
        if i == face_row and b.startswith("│"):
            b = "<" + b[1:]   # the bubble's tail points at his mouth
        left = f"{tint}{pad(s, SPRITE_COLS)}{reset}"
        out.append(f"{left} {dim}{b}{reset}" if b else left)
    return "\n".join(out)
