"""Helpers for drawing goblin animations.

A scene is 4 frames of 4 rows, at most 16 columns wide. Colors come from a
character -> role map instead of a hand-typed mask, so masks can't drift out of
line with the art. Roles (see render.ROLE_COLORS): '.' the goblin himself,
s smoke, e ember, g weed/leaf, c screen, y light/glow/text, w wood, b bed,
m metal, r rainbow. Row 2 is the body: '▓' there is his shirt and is never
recolored, so every goblin keeps his own pattern.
"""

from ..text import char_width as _width

ROWS, COLS, FRAMES = 4, 16, 4
TORSO_ROW = 2


def mask(row: str, colors: dict[str, str], body: bool = False) -> str:
    out = []
    for ch in row:
        w = _width(ch)
        if w == 0:
            continue
        if ch == " ":
            role = " "
        elif body and ch == "▓":
            role = "."
        else:
            role = colors.get(ch, ".")
        out.append(role * w)
    return "".join(out)


def scene(desc: str, frames: list[list[str]], colors: dict[str, str] | None = None) -> dict:
    """An emote spec: {desc, frames, masks}. `colors` maps characters to roles."""
    colors = colors or {}
    masks = [[mask(r, colors, body=(i == TORSO_ROW)) for i, r in enumerate(fr)] for fr in frames]
    return {"desc": desc, "frames": [list(fr) for fr in frames], "masks": masks}
