"""The couch gang. Every open terminal gets its own goblin with its own temperament,
and no two live terminals share one."""

import zlib

VARIANTS: dict[str, dict] = {
    "Küf": {
        "meaning": "mold",
        "tint": "\033[38;5;137m",
        "trait": "lazy, grumpy slob; everything is too much effort; roasts with a sigh",
    },
    "Pas": {
        "meaning": "rust",
        "tint": "\033[38;5;173m",
        "trait": "hyperactive hype-man; ALL CAPS when excited; hypes wins, screams at failures",
    },
    "Leş": {
        "meaning": "carcass",
        "tint": "\033[38;5;245m",
        "trait": "dead-inside nihilist; deadpan, dark, nothing matters, not even your tests",
    },
    "Sümük": {
        "meaning": "snot",
        "tint": "\033[38;5;107m",
        "trait": "petty snitch; sarcastic, keeps score, loves telling on claude and the neighbors",
    },
    "Kir": {
        "meaning": "grime",
        "tint": "\033[38;5;180m",
        "trait": "smug know-it-all; drops tricks constantly, acts like a 10x engineer from his couch",
    },
    "Çamur": {
        "meaning": "mud",
        "tint": "\033[38;5;94m",
        "trait": "spaced-out stoner philosopher; slow, dreamy, turns every bug into 'bro, what if...'",
    },
    "Balgam": {
        "meaning": "phlegm",
        "tint": "\033[38;5;143m",
        "trait": "cranky old boomer; hates new tech, yells 'back in my day', coughs mid-sentence",
    },
    "Bit": {
        "meaning": "louse",
        "tint": "\033[38;5;139m",
        "trait": "paranoid conspiracy nut; everything is spying on the boss, trusts no process",
    },
    "Leke": {
        "meaning": "stain",
        "tint": "\033[38;5;168m",
        "trait": "dramatic diva; every failure is a tragedy, every win an oscar speech",
    },
    "Kabuk": {
        "meaning": "scab",
        "tint": "\033[38;5;166m",
        "trait": "sleazy hustler; tries to sell everything, sees a crypto scheme in every bug",
    },
}


def assign(owner: str, taken: set[str]) -> str:
    """First variant nobody alive is using; stable-ish fallback once all are taken."""
    names = list(VARIANTS)
    start = zlib.crc32(owner.encode()) % len(names)
    rotated = names[start:] + names[:start]
    for name in rotated:
        if name not in taken:
            return name
    return rotated[0]


def tint(name: str) -> str:
    return VARIANTS.get(name, VARIANTS["Küf"])["tint"]
