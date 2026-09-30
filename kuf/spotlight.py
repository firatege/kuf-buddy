"""Spotlight moments: a command in any terminal calls out the one goblin it suits best
(a push brings out Pas with his megaphone, a force-push gets Sümük on the phone to the
cops). If that goblin isn't open, the goblin of the terminal where it happened reacts."""

import re
import time
from datetime import datetime

from . import state, stats

SPOTLIGHT_S = 10.0
COOLDOWN_S = 60.0      # per kind of event
NIGHT = range(1, 6)

# (kind, pattern); first match wins, so the specific ones go first
EVENTS = [
    ("force-push", re.compile(r"\bgit\s+push\b.*(\s--force\b|\s-f\b|--force-with-lease)")),
    ("push", re.compile(r"\bgit\s+push\b")),
    ("commit", re.compile(r"\bgit\s+commit\b")),
    ("reset", re.compile(r"\bgit\s+reset\s+--hard\b")),
    ("merge", re.compile(r"\bgit\s+(merge|rebase)\b")),
    ("rm", re.compile(r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r")),
    ("install", re.compile(r"\b(npm|pnpm|yarn|bun)\s+(i|install|add)\b|\bpip3?\s+install\b|\bcargo\s+add\b")),
]

# kind -> (goblin, emote, outburst)
STARS = {
    "force-push": ("Sümük", "sumuk-tattle", "force push?! hello police? i'm calling it in."),
    "push": ("Pas", "pas-megaphone", "PUSHED IT!! LET'S GOOOO!!"),
    "night-commit": ("Balgam", "balgam-fist", "committing at this hour? back in my day we SLEPT."),
    "commit": ("Kabuk", "kabuk-cash", "every commit is an NFT, boss. i'm minting this one."),
    "reset": ("Leş", "les-candle", "all gone. finally, peace."),
    "merge": ("Leke", "leke-spotlight", "a WEDDING! two branches, one love. i'm crying."),
    "rm": ("Bit", "bit-blinds", "destroying evidence. smart. they're watching."),
    "install": ("Küf", "kuf-rot", "more dependencies. more weight on my couch."),
}
# when the star isn't around, the local goblin says something about it
STAND_IN = {
    "force-push": ("sus", "force push? bold. somebody's gonna be mad."),
    "push": ("hype", "pushed! it's out there now."),
    "night-commit": ("sleep", "committing at this hour? go to bed."),
    "commit": ("flex", "committed. look at you, responsible."),
    "reset": ("dead", "reset --hard. rip everything."),
    "merge": ("love", "branches merging. beautiful."),
    "rm": ("sus", "rm -rf. hope you meant that."),
    "install": ("burp", "more packages. the node_modules grows."),
}


def classify(command: str, hour: int | None = None) -> str | None:
    kind = next((k for k, pattern in EVENTS if pattern.search(command)), None)
    hour = datetime.now().hour if hour is None else hour
    return "night-commit" if kind == "commit" and hour in NIGHT else kind


def trigger(kind: str, by: str, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    started = []

    def change(s: dict) -> dict:
        last = s.get("spotlight_last", {})
        if now - last.get(kind, 0.0) < COOLDOWN_S:
            return s
        started.append(True)
        star = STARS[kind][0]
        live = {b["name"] for b in s["buddies"].values() if not state.is_ghost(b)}
        credited = star if star in live else s["buddies"].get(by, {}).get("name")
        counted = stats.bump(s, credited, "spotlights") if credited else s
        return {**counted, "spotlight": {"kind": kind, "by": by, "ts": now},
                "spotlight_last": {**last, kind: now}}

    state.update(change)
    return bool(started)


def view(s: dict, owner: str, name: str, now: float) -> tuple[str, str] | None:
    """(emote, outburst) if this terminal's goblin is in the spotlight right now."""
    spot = s.get("spotlight")
    if not spot or not 0 <= now - spot["ts"] < SPOTLIGHT_S:
        return None
    star, emote, line = STARS[spot["kind"]]
    live = {b["name"] for o, b in s["buddies"].items() if not state.is_ghost(b)}
    if name == star:
        return emote, line
    if star not in live and owner == spot["by"]:
        return STAND_IN[spot["kind"]]
    return None
