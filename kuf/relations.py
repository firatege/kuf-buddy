"""How the goblins feel about each other.

Every pair has a score from -100 (sworn enemies) to 100 (ride or die). Claude tags
each conversation with a vibe and, if one came up, an inside joke; the code turns that
into points, so the numbers stay consistent whatever the model's mood. Relationships
belong to goblin names, so they outlive terminals.
"""

import time

from . import state

VIBES = {"warm": 6, "teasing": 3, "tense": -3, "hostile": -6}
JOINT_BONUS = 8        # sharing one is bonding
REFUSED = -4           # turning Snoop down stings a little
MAX_JOKES = 5
LIMIT = 100

# (lowest score, stage, marker); first match from the top wins
STAGES = [(60, "ride or die", "♥"), (30, "buddies", "♥"), (10, "friendly", ""),
          (-10, "neutral", ""), (-40, "rivals", "⚔"), (-LIMIT - 1, "enemies", "⚔")]


def key(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


def get(s: dict, a: str, b: str) -> dict:
    return s.get("relations", {}).get(key(a, b), {"score": 0, "talks": 0, "joints": 0, "jokes": []})


def stage(rel: dict) -> tuple[str, str]:
    """(stage name, marker) for a relationship."""
    if rel["talks"] < 2 and abs(rel["score"]) < 10:
        return "strangers", ""
    return next((name, mark) for low, name, mark in STAGES if rel["score"] >= low)


def _bump(s: dict, a: str, b: str, delta: int, joke: str, now: float, joint: bool) -> dict:
    rel = get(s, a, b)
    jokes = rel["jokes"] + ([joke] if joke and joke not in rel["jokes"] else [])
    updated = {"score": max(-LIMIT, min(LIMIT, rel["score"] + delta)), "talks": rel["talks"] + 1,
               "joints": rel["joints"] + (1 if joint else 0), "jokes": jokes[-MAX_JOKES:], "last": now}
    return {**s, "relations": {**s.get("relations", {}), key(a, b): updated}}


def record(s: dict, names: list[str], kind: str, vibe: str | None, joke: str | None,
           host: str = "", now: float | None = None) -> dict:
    """Apply one conversation to every pair that took part."""
    now = time.time() if now is None else now
    circle = list(dict.fromkeys(names))
    delta = VIBES.get(vibe or "", 0)
    for i, a in enumerate(circle):
        for b in circle[i + 1:]:
            if kind == "session":
                bonus = JOINT_BONUS
            elif kind == "refused" and host in (a, b):
                bonus = REFUSED
            else:
                bonus = 0
            s = _bump(s, a, b, delta + bonus, (joke or "").strip()[:80], now, kind == "session")
    return s


def save(names: list[str], kind: str, vibe: str | None, joke: str | None, host: str = "") -> None:
    state.update(lambda s: record(s, names, kind, vibe, joke, host))


def describe(s: dict, me: str, them: str) -> str:
    """One line for Claude: how `me` and `them` get along."""
    rel = get(s, me, them)
    name, _ = stage(rel)
    parts = [f"you & {them}: {name} ({rel['score']:+d}"]
    if rel["talks"]:
        parts.append(f", {rel['talks']} hangouts" + (f", {rel['joints']} joints" if rel["joints"] else ""))
    parts.append(")")
    if rel["jokes"]:
        parts.append(" · inside jokes: " + "; ".join(f'"{j}"' for j in rel["jokes"][-3:]))
    return "".join(parts)


def joint_odds(s: dict, host: str, guest: str, base: float) -> float:
    """Friends take it more often, rivals less; ride-or-die can even win over a never."""
    return max(0.0, min(1.0, base + get(s, host, guest)["score"] / 200))


def marker(s: dict, a: str, b: str) -> str:
    return stage(get(s, a, b))[1]
