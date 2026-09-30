"""The couch gang. Every open terminal gets its own goblin with its own temperament,
and no two live terminals share one."""

import unicodedata
import zlib

VARIANTS: dict[str, dict] = {
    "Küf": {
        "meaning": "mold",
        "tint": "\033[38;5;137m",
        "torso": "▓▓▓",
        "junk": ",,",
        "trait": "lazy, grumpy slob; everything is too much effort; roasts with a sigh",
    },
    "Pas": {
        "meaning": "rust",
        "tint": "\033[38;5;173m",
        "torso": "≡≡≡",
        "junk": "!!",
        "trait": "hyperactive hype-man; ALL CAPS when excited; hypes wins, screams at failures",
    },
    "Leş": {
        "meaning": "carcass",
        "tint": "\033[38;5;245m",
        "torso": "░░░",
        "junk": "†.",
        "trait": "dead-inside nihilist; deadpan, dark, nothing matters, not even your tests",
    },
    "Sümük": {
        "meaning": "snot",
        "tint": "\033[38;5;107m",
        "torso": "▒▒▒",
        "junk": "✎,",
        "trait": "petty snitch; sarcastic, keeps score, loves telling on claude and the neighbors",
    },
    "Kir": {
        "meaning": "grime",
        "tint": "\033[38;5;180m",
        "torso": "▚▚▚",
        "junk": "<>",
        "trait": "smug know-it-all; drops tricks constantly, acts like a 10x engineer from his couch",
    },
    "Çamur": {
        "meaning": "mud",
        "tint": "\033[38;5;94m",
        "torso": "≈≈≈",
        "junk": "°~",
        "trait": "spaced-out stoner philosopher; slow, dreamy, turns every bug into 'bro, what if...'",
    },
    "Balgam": {
        "meaning": "phlegm",
        "tint": "\033[38;5;143m",
        "torso": "▤▤▤",
        "junk": "¤,",
        "trait": "cranky old boomer; hates new tech, yells 'back in my day', coughs mid-sentence",
    },
    "Bit": {
        "meaning": "louse",
        "tint": "\033[38;5;139m",
        "torso": "░▒░",
        "junk": "◉.",
        "trait": "paranoid conspiracy nut; everything is spying on the boss, trusts no process",
    },
    "Leke": {
        "meaning": "stain",
        "tint": "\033[38;5;168m",
        "torso": "▓●▓",
        "junk": "✿,",
        "trait": "dramatic diva; every failure is a tragedy, every win an oscar speech",
    },
    "Kabuk": {
        "meaning": "scab",
        "tint": "\033[38;5;166m",
        "torso": "$$$",
        "junk": "$$",
        "trait": "sleazy hustler; tries to sell everything, sees a crypto scheme in every bug",
    },
    "Snoop": {
        "meaning": "the one who's always lit",
        "tint": "\033[38;5;113m",
        "torso": "♣♣♣",
        "junk": "~*",
        "trait": "permanently high, laid-back smoker; slow drawl, everything is 'smooth', always sparking one up, zero rush",
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


def skin(name: str) -> tuple[str, str]:
    """(torso pattern, floor junk): what makes each goblin recognizable at a glance."""
    variant = VARIANTS.get(name, VARIANTS["Küf"])
    return variant["torso"], variant["junk"]


def _fold(text: str) -> str:
    """'Çamur' -> 'camur', 'Leş' -> 'les': match names typed without Turkish letters."""
    plain = unicodedata.normalize("NFKD", text.replace("ı", "i")).encode("ascii", "ignore").decode()
    return plain.strip().lower()


def resolve(typed: str) -> str | None:
    """The goblin a user means by `typed`, or None."""
    wanted = _fold(typed or "")
    return next((name for name in VARIANTS if _fold(name) == wanted), None) if wanted else None
