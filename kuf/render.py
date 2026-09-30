"""Draw Küf and his speech bubble for the terminal."""

import re
import textwrap

from .buddies import skin, tint as buddy_tint
from .emotes import EMOTES
from .text import graphemes, width

SPRITE_COLS = 16
BUBBLE_TEXT_COLS = 56
BUBBLE_MAX_LINES = 3   # per paragraph; a stacked exchange has two

RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
GLOW = "\033[1;97m"   # bold bright white: goblins talking to each other
# Color roles used by room masks ('.' = the goblin's own tint, ' ' = plain).
ROLE_COLORS = {"s": 250, "e": 208, "g": 71, "c": 45, "y": 229, "w": 94, "b": 61, "m": 245}
RAINBOW = [196, 208, 226, 46, 51, 33, 201]
MOOD_COLOR = {
    "comfy": "\033[38;5;137m",    # mud brown
    "sleepy": "\033[38;5;102m",   # dusty grey
    "grumpy": "\033[38;5;106m",   # mold green
    "furious": "\033[38;5;167m",  # angry red
}
EMOTE_MOOD = {"rage": "furious", "tableflip": "furious", "middle-finger": "furious",
              "roast": "grumpy", "sus": "grumpy", "facepalm": "grumpy", "puke": "grumpy",
              "dead": "sleepy", "sleep": "sleepy", "cry": "sleepy"}


def pad(text: str, cols: int) -> str:
    return text + " " * max(0, cols - width(text))


MIRROR = dict(zip("()[]{}<>/\\╯╰╭╮┗┛┏┓ᕦᕤ☞☜ﾉ彡ミ▐▌▖▗▘▝▙▟▛▜«»⊲⊳◀▶┐┌\u0300\u0301",
                  ")(][}{><\\/╰╯╮╭┛┗┓┏ᕤᕦ☜☞\\ミ彡▌▐▗▖▝▘▟▙▜▛»«⊳⊲▶◀┌┐\u0301\u0300"))


def mirror(rows: list[str]) -> list[str]:
    """Flip plain rows horizontally (a thin wrapper over mirror_cells)."""
    return ["".join(g for g, _ in row) for row in mirror_cells([cells(r, None) for r in rows])]


TORSO = re.compile("▓+")
DEFAULT_JUNK = ",,"


def dress(rows: list[str], name: str) -> list[str]:
    """Put the goblin's own shirt on and his own junk on the floor (emote-specific
    floor stuff like puke or rage marks stays)."""
    torso, junk = skin(name)
    body = TORSO.sub(lambda m: (torso * len(m.group()))[: len(m.group())], rows[2], count=1)
    if body.endswith(DEFAULT_JUNK):
        body = body[: -len(DEFAULT_JUNK)] + junk
    return [*rows[:2], body, *rows[3:]]


Cell = tuple[str, str]   # (grapheme, color role)


def cells(row: str, mask: str | None) -> list[Cell]:
    """Pair each grapheme with its mask letter by column; no mask = all goblin."""
    out, col = [], 0
    for g in graphemes(row):
        role = "." if mask is None else (mask[col] if col < len(mask) else " ")
        out.append((g, role))
        col += max(1, width(g))
    return out


WORD = re.compile(r"[A-Za-z0-9!?']")


def _unreverse_words(row: list[Cell]) -> list[Cell]:
    """After a flip, put text like LMAO or LET'S GO back in reading order (single spaces
    between words stay part of the phrase)."""
    out: list[Cell] = []
    run: list[Cell] = []
    padded = row + [(" ", " "), (" ", " ")]
    for i, cell in enumerate(padded[:-1]):
        inside = WORD.fullmatch(cell[0]) or (
            cell[0] == " " and run and WORD.fullmatch(padded[i + 1][0]))
        if inside:
            run.append(cell)
            continue
        out.extend(reversed(run))
        run = []
        out.append(cell)
    return out[:-1]


def mirror_cells(rows: list[list[Cell]]) -> list[list[Cell]]:
    cols = max(sum(width(g) for g, _ in r) for r in rows)
    padded = [r + [(" ", " ")] * (cols - sum(width(g) for g, _ in r)) for r in rows]
    flipped = [[("".join(MIRROR.get(c, c) for c in g), role) for g, role in reversed(r)] for r in padded]
    return [_unreverse_words(r) for r in flipped]


def frame(emote: str, tick: int, facing: str = "right", name: str = "Küf") -> list[list[Cell]]:
    """This tick's sprite as rows of (grapheme, role) cells."""
    spec = EMOTES[emote]
    i = tick % len(spec["frames"])
    masks = spec.get("masks")
    rows = [cells(r, masks[i][n] if masks else None) for n, r in enumerate(dress(spec["frames"][i], name))]
    return mirror_cells(rows) if facing == "left" else rows


def paint(row: list[Cell], tint: str, tick: int, color: bool = True) -> str:
    """One sprite row with each part in its role's color."""
    if not color:
        return "".join(g for g, _ in row)
    out, col, current = [], 0, None
    for g, role in row:
        if role == ".":
            code = tint
        elif role == "r":
            code = f"\033[38;5;{RAINBOW[(col + tick) % len(RAINBOW)]}m"
        elif role in ROLE_COLORS:
            code = f"\033[38;5;{ROLE_COLORS[role]}m"
        else:
            code = RESET
        if code != current:
            out.append(code)
            current = code
        out.append(g)
        col += max(1, width(g))
    return "".join(out) + RESET


def _wrap(paragraph: str) -> list[str]:
    wrapped = textwrap.wrap(paragraph, BUBBLE_TEXT_COLS) or [""]
    if len(wrapped) <= BUBBLE_MAX_LINES:
        return wrapped
    kept = wrapped[:BUBBLE_MAX_LINES]
    return kept[:-1] + [kept[-1][: BUBBLE_TEXT_COLS - 1] + "…"]


def bubble(line: str, name: str = "Küf", marker: str = "") -> list[str]:
    paragraphs = [_wrap(paragraph) for paragraph in line.split("\n")]
    inner = max(width(row) for rows in paragraphs for row in rows)
    label = f"─ {name} {marker} " if marker else f"─ {name} "
    inner = max(inner, width(label) - 2)
    top = f"╭{label}{'─' * (inner + 2 - width(label))}╮"
    divider = f"├{'┄' * (inner + 2)}┤"
    body = [row for i, rows in enumerate(paragraphs)
            for row in ([divider] if i else []) + [f"│ {pad(w, inner)} │" for w in rows]]
    bottom = f"╰{'─' * (inner + 2)}╯"
    return [top, *body, bottom]


def compose(emote: str, line: str, tick: int, mood: str | None = None,
            color: bool = True, name: str = "Küf", facing: str = "right",
            highlight: bool = False, marker: str = "") -> str:
    """Goblin plus speech bubble. Facing right he sits left of the bubble; facing left
    (toward a neighbor on the left) he's mirrored and sits right of it."""
    feeling = mood or EMOTE_MOOD.get(emote, "comfy")
    tint = "" if not color else (MOOD_COLOR["furious"] if feeling == "furious" else buddy_tint(name))
    sprite_cells = frame(emote, tick, facing, name)
    painted = [paint(r, tint, tick, color) + " " * (SPRITE_COLS - sum(width(g) for g, _ in r))
               for r in sprite_cells]
    speech = bubble(line, name, marker)
    rows = max(len(painted), len(speech))
    # Claude Code strips leading spaces from status lines; a leading reset keeps the columns.
    sprite = [" " * SPRITE_COLS] * (rows - len(painted)) + painted     # sit him on the bottom
    speech = speech + [""] * (rows - len(speech))
    face_row = rows - 3
    dim, reset = ((GLOW if highlight else DIM), RESET) if color else ("", "")

    bubble_cols = max(width(b) for b in speech)
    out = []
    for i, (s, b) in enumerate(zip(sprite, speech)):
        if facing == "left":
            if i == face_row and b.endswith(("│", "┤")):
                b = b[:-1] + ">"   # tail points at his mouth, now on his left
            text = f"{dim}{pad(b, bubble_cols)}{reset} " if b else " " * (bubble_cols + 1)
            out.append(f"{text}{s}".rstrip())
        else:
            if i == face_row and b.startswith(("│", "├")):
                b = "<" + b[1:]    # the bubble's tail points at his mouth
            out.append(f"{s} {dim}{b}{reset}" if b else s.rstrip())
    # Claude Code strips leading spaces from status lines; a leading reset keeps the columns.
    keep = RESET if color else ""
    return "\n".join(keep + row for row in out)
