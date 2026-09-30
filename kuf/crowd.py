"""Crowd moments: when tests pass (or blow up) in any terminal, every goblin reacts at
once, each in his own way. Solo outbursts, not a conversation, so they're canned."""

from . import moments

CROWD_S = 12.0         # how long everyone reacts
COOLDOWN_S = 120.0     # at most one crowd moment every two minutes

# goblin -> {kind: (emote, outburst)}
REACTIONS: dict[str, dict[str, tuple[str, str]]] = {
    "Küf":    {"win": ("burp", "eh. nice. can i lie down now"), "fail": ("kuf-remote", "ugh. not getting up for this.")},
    "Pas":    {"win": ("pas-confetti", "LET'S GOOOOOO!!!"), "fail": ("pas-airhorn", "NOOOOOOO!!!")},
    "Leş":    {"win": ("shrug", "it passed. we still die."), "fail": ("les-flatline", "as expected.")},
    "Sümük":  {"win": ("sumuk-tally", "noted. one win. for now."), "fail": ("sumuk-tattle", "i'm telling. this is going in the book.")},
    "Kir":    {"win": ("kir-glasses", "told you. ez."), "fail": ("kir-lecture", "amateurs. read the stack trace.")},
    "Çamur":  {"win": ("camur-float", "bro... green is so beautiful"), "fail": ("camur-galaxy", "bro what if red is just green upside down")},
    "Balgam": {"win": ("balgam-fist", "*hack* back in my day tests never passed"), "fail": ("balgam-cough", "*HACK* told you so")},
    "Bit":    {"win": ("bit-tinfoil", "too green. suspicious."), "fail": ("bit-hide", "they sabotaged it. hide.")},
    "Leke":   {"win": ("leke-oscar", "i'd like to thank the tests"), "fail": ("leke-faint", "a tragedy. i can't go on.")},
    "Kabuk":  {"win": ("kabuk-cash", "green means money, baby"), "fail": ("kabuk-chart", "rug pulled. sell everything.")},
    "Snoop":  {"win": ("snoop-lowrider", "smooth, man... real smooth"), "fail": ("snoop-rings", "it's cool, man... just breathe")},
}
FALLBACK = {"win": ("flex", "ayyy it passed"), "fail": ("facepalm", "welp. it broke.")}


def trigger(kind: str, by: str, now: float | None = None) -> bool:
    """Start a crowd moment unless one happened recently. True if it started."""
    return moments.fire("crowd", {"kind": kind, "by": by}, COOLDOWN_S, now=now)


def view(s: dict, name: str, now: float) -> tuple[str, str] | None:
    """(emote, outburst) while a crowd moment is on."""
    crowd = moments.current(s, "crowd", CROWD_S, now)
    if not crowd:
        return None
    return REACTIONS.get(name, {}).get(crowd["kind"], FALLBACK[crowd["kind"]])
