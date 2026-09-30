"""Spotlight moments: a command in any terminal calls out the one goblin it suits best
(a push brings out Pas with his megaphone, a force-push gets Sümük on the phone to the
cops). If that goblin isn't open, the goblin of the terminal where it happened reacts."""

import re
from datetime import datetime

from . import clock, moments, state, stats, tr
from .config import turkish

SPOTLIGHT_S = 10.0
COOLDOWN_S = 60.0      # per kind of event

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
    return "night-commit" if kind == "commit" and clock.is_night(hour) else kind


def trigger(kind: str, by: str, now: float | None = None) -> bool:
    """Put the event's star in the spotlight (once a minute per kind of event)."""
    def credit(s: dict) -> dict:
        star = STARS[kind][0]
        credited = star if star in state.live_names(s) else s["buddies"].get(by, {}).get("name")
        return stats.bump(s, credited, "spotlights") if credited else s

    return moments.fire("spotlight", {"kind": kind, "by": by}, COOLDOWN_S, per=kind, now=now, also=credit)


def view(s: dict, owner: str, name: str, now: float) -> tuple[str, str] | None:
    """(emote, outburst) if this terminal's goblin is in the spotlight right now."""
    spot = moments.current(s, "spotlight", SPOTLIGHT_S, now)
    if not spot:
        return None
    star, emote, line = STARS[spot["kind"]]
    if name == star:
        return emote, tr.SPOT[spot["kind"]] if turkish() else line
    if star not in state.live_names(s) and owner == spot["by"]:
        stand_emote, stand_line = STAND_IN[spot["kind"]]
        return stand_emote, tr.STAND_IN[spot["kind"]] if turkish() else stand_line
    return None
