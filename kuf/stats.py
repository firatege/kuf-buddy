"""Couch stats: who smoked how much, who talks to whom, who keeps saying no.
`goblin stats` (or `kuf stats`) prints them."""

from . import relations, state
from .buddies import VARIANTS

def _n(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def bump(s: dict, name: str, counter: str, by: int = 1) -> dict:
    mine = s.get("stats", {}).get(name, {})
    return {**s, "stats": {**s.get("stats", {}), name: {**mine, counter: mine.get(counter, 0) + by}}}


def after_session(s: dict, kind: str, order: list[str], host: str) -> dict:
    """Count one written conversation for everyone in it."""
    circle = list(dict.fromkeys(order))
    for name in circle:
        if kind == "session":
            s = bump(s, name, "joints")
        elif kind == "banter":
            s = bump(s, name, "chats")
        elif kind == "refused":
            s = bump(s, name, "turned_down" if name == host else "refused")
    return s


def report(s: dict, me: str = "") -> str:
    counts = s.get("stats", {})
    names = [n for n in VARIANTS if counts.get(n) or n == me]
    lines = ["🌿 couch stats"]
    for name in names:
        c = counts.get(name, {})
        bits = [_n(c.get("joints", 0), "joint"), _n(c.get("chats", 0), "chat")]
        if c.get("refused"):
            bits.append(f"said no {c['refused']}×")
        if c.get("turned_down"):
            bits.append(f"got turned down {c['turned_down']}×")
        if c.get("spotlights"):
            bits.append(_n(c["spotlights"], "spotlight"))
        here = " (this terminal)" if name == me else ""
        lines.append(f"  {name}{here}: " + " · ".join(bits))
    pairs = sorted(s.get("relations", {}).items(), key=lambda kv: -abs(kv[1]["score"]))
    if pairs:
        lines.append("")
        lines.append("relationships")
        for pair, rel in pairs:
            a, b = pair.split("|")
            stage, mark = relations.stage(rel)
            joke = f' · "{rel["jokes"][-1]}"' if rel["jokes"] else ""
            joints = f" · {_n(rel['joints'], 'joint')}" if rel["joints"] else ""
            lines.append(f"  {a} {mark or '·'} {b}: {stage} {rel['score']:+d} · {_n(rel['talks'], 'hangout')}{joints}{joke}")
    podium = []
    for k, label in (("joints", "top smoker"), ("refused", "most likely to say no"), ("chats", "biggest mouth")):
        best = max((counts.get(n, {}).get(k, 0) for n in names), default=0)
        if best:
            leaders = ", ".join(n for n in names if counts.get(n, {}).get(k, 0) == best)
            podium.append(f"{label}: {leaders} ({best})")
    if podium:
        lines.append("")
        lines.append(" · ".join(podium))
    if len(lines) == 1:
        lines.append("  nothing yet. go smoke one: !joint")
    return "\n".join(lines)


def show(me: str = "") -> str:
    return report(state.load(), me)
