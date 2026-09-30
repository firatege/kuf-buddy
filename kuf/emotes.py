"""Küf's emote sheet: a filthy couch goblin, 4 rows tall, 2 animation frames each.

Row order is always: effects/flies, face, body, couch.
"""

import zlib

COUCH = "▐█▄▄▄▄▄▄▄█▌"      # seat; the armrests are added around the body row
BODY = "/|▓▓▓|\\ ,,"
SLOUCH = " |▓▓▓|~ ,,"
ARM_L, ARM_R = "▐▌", "▐▌"
BODY_CORE = 7                # body chars that sit between the armrests; the rest is floor junk


def _on_couch(frame: tuple) -> list[str]:
    """Sit a frame written as (effects, face, body+junk, seat) between the armrests."""
    fx, face, body, seat = frame
    core, junk = body[:BODY_CORE], body[BODY_CORE:].strip()[:2]
    return ["  " + fx, "  " + face, f"{ARM_L}{core}{ARM_R}{junk}", seat]


def _emote(desc: str, *frames: tuple) -> dict:
    return {"desc": desc, "frames": [_on_couch(f) for f in frames]}


EMOTES: dict[str, dict] = {
    "chill": _emote(
        "default couch slouch, nothing is on fire",
        (" °   ·", " (-‿-)旦", BODY, COUCH),
        ("  · °", " (-‿-)旦~", BODY, COUCH),
    ),
    "sleep": _emote(
        "passed out, snoring",
        (" °    zZ", " (=_=)", SLOUCH, COUCH),
        ("  ° zZz", " (-_-)", SLOUCH, COUCH),
    ),
    "eat": _emote(
        "stuffing his face with something off the floor",
        (" ° nom", " (ˆ○ˆ)ノ◎", BODY, COUCH),
        ("  ·nom!", " (ˆ~ˆ)ノ◎", BODY, COUCH),
    ),
    "burp": _emote(
        "gross, loud burp",
        (" ° BUUURP", " (ˇ0ˇ)", BODY, COUCH),
        ("  ·  burp", " (ˇoˇ)", BODY, COUCH),
    ),
    "scratch": _emote(
        "scratching his belly, unbothered",
        (" °  ·", " (¬‿¬)", "/|▓▓▓|ﾉ ,,", COUCH),
        ("  · °", " (¬‿¬)", "/|▓▓▓ﾉ| ,,", COUCH),
    ),
    "laugh": _emote(
        "dying laughing",
        (" HAHAHA", " (≧▽≦)", BODY, COUCH),
        (" HEHEHE", " (≧∇≦)ﾉ", BODY, COUCH),
    ),
    "roast": _emote(
        "pointing and laughing at your code",
        (" ° LMAO", " (☞ﾟ∀ﾟ)☞", BODY, COUCH),
        ("  ·lmao", " (☞ﾟヮﾟ)☞", BODY, COUCH),
    ),
    "rage": _emote(
        "absolutely furious",
        (" °#·#°", " (╬ಠ益ಠ)", "/|▓▓▓|\\ ##", COUCH),
        (" #°·°#", " (╬Ò益Ó)", "/|▓▓▓|\\ ##", COUCH),
    ),
    "tableflip": _emote(
        "flipping the table, done with this",
        ("      ┻━┻", " (╯°□°)╯︵", BODY, COUCH),
        ("   ︵ ┻━┻", " (╯°Д°)╯", BODY, COUCH),
    ),
    "middle-finger": _emote(
        "flipping you off (affectionately)",
        (" °   ·", " (¬_¬)╭∩╮", BODY, COUCH),
        ("  · °", "╭∩╮(¬_¬)╭∩╮", BODY, COUCH),
    ),
    "facepalm": _emote(
        "can't believe what he just saw",
        (" °  ...", " (－‸ლ)", BODY, COUCH),
        ("  · ...", " (ლ‸－)", BODY, COUCH),
    ),
    "flex": _emote(
        "proud, flexing, you did good",
        (" ° ✦", "ᕦ(ò_óˇ)ᕤ", " |▓▓▓| ,,", COUCH),
        ("  ✦ ·", "ᕦ(ò‿óˇ)ᕤ", " |▓▓▓| ,,", COUCH),
    ),
    "hype": _emote(
        "hyped, dancing on the couch",
        (" ♪ °  ♫", " \\(ˆoˆ)/", " |▓▓▓| ,,", COUCH),
        ("  ♫ · ♪", " ┗(ˆoˆ)┛", " /▓▓▓\\ ,,", COUCH),
    ),
    "cry": _emote(
        "crying, it's that bad",
        (" °  ·", " (ಥ﹏ಥ)", BODY, COUCH),
        ("  · °", " (ಥ_ಥ)", "/|▓▓▓|\\ ;;", COUCH),
    ),
    "dead": _emote(
        "dead. deceased. flies everywhere",
        (" °·°·°·", " (x_x)", SLOUCH, COUCH),
        (" ·°·°·°", " (x_X)", SLOUCH, COUCH),
    ),
    "sus": _emote(
        "suspicious side-eye",
        (" °   ·", " (¬_¬ )", BODY, COUCH),
        ("  · °", " ( ¬_¬)", BODY, COUCH),
    ),
    "think": _emote(
        "thinking hard (rare)",
        (" °    ?", " ( ˘_˘)", "/|▓▓▓|ﾉ ,,", COUCH),
        ("  · ...", " (˘_˘ )", "/|▓▓▓|ﾉ ,,", COUCH),
    ),
    "tip": _emote(
        "dropping a trick / pro tip",
        (" °  !", " (•̀ᴗ•́)☝", BODY, COUCH),
        ("  · !!", " (•̀ᴗ•́)☝", BODY, COUCH),
    ),
    "shrug": _emote(
        "whatever, not his problem",
        (" °   ·", "¯\\_(ツ)_/¯", " |▓▓▓| ,,", COUCH),
        ("  · °", " _/(ツ)\\_", " |▓▓▓| ,,", COUCH),
    ),
    "love": _emote(
        "genuinely touched, don't tell anyone",
        (" ♥  °", " (♥‿♥)", BODY, COUCH),
        ("  ♡ ·", " (♡‿♡)", BODY, COUCH),
    ),
    "puke": _emote(
        "physically sick from that code",
        (" °  ·", " (×﹏×)", "/|▓▓▓|\\ ~~", COUCH),
        ("  · °", " (＠﹏＠)", "/|▓▓▓|\\~~~", COUCH),
    ),
}

# Idle life on the couch: longer loops, one frame per second.
EMOTES.update({
    "tea": _emote(
        "sipping tea on the couch, pinky out",
        ("  ~", " (-‿-) 旦", "/|▓▓▓|ﾉ ,,", COUCH),
        (" ~  ~", " (-‿-)旦", "/|▓▓▓ﾉ| ,,", COUCH),
        ("  ~", " (ˆ‿ˆ)旦", "/|▓▓▓ﾉ| ,,", COUCH),
        (" ahh~", " (ˆ▿ˆ) 旦", "/|▓▓▓|ﾉ ,,", COUCH),
    ),
    "nap": _emote(
        "stretched out along the couch, napping",
        ("      z", "", "(-.-)▓▓ ,,", COUCH),
        ("     zZ", "", "(-.-)▓▓ ,,", COUCH),
        ("    zZz", "", "(-o-)▓▓ ,,", COUCH),
        ("   Zzz ", "", "(-.-)▓▓ ,,", COUCH),
    ),
    "phone": _emote(
        "doomscrolling on his phone",
        ("  °", " (・_・)▯", "/|▓▓▓|ﾉ ,,", COUCH),
        ("  ·", " (・_・ )▯", "/|▓▓▓|ﾉ ,,", COUCH),
        ("  °", " (・‿・)▯", "/|▓▓▓|ﾉ ,,", COUCH),
        ("  lol", " (≧▽≦)▯", "/|▓▓▓|ﾉ ,,", COUCH),
    ),
    "stretch": _emote(
        "yawning and stretching",
        ("  °", " (-‿-)", BODY, COUCH),
        (" yaaawn", "\\(˘O˘)/", " |▓▓▓| ,,", COUCH),
        ("  ~", "\\(˘o˘)/", " |▓▓▓| ,,", COUCH),
        ("  ·", " (ˆ‿ˆ)", SLOUCH, COUCH),
    ),
    "game": _emote(
        "playing a beat-up gameboy",
        (" beep", " (°▽°)▣", "/|▓▓▓|ﾉ ,,", COUCH),
        (" boop", " (°o°)▣", "/|▓▓▓|ﾉ ,,", COUCH),
        (" beep", " (ò_ó)▣", "/|▓▓▓|ﾉ ,,", COUCH),
        (" YES", " (≧▽≦)▣", "/|▓▓▓|ﾉ ,,", COUCH),
    ),
    "nosepick": _emote(
        "picking his nose. he's a goblin",
        ("  °", " (¬‿¬)", BODY, COUCH),
        ("  ·", " (¬o¬)ﾉ", "/|▓▓▓|  ,,", COUCH),
        ("  °", " (ˆoˆ)ﾉ•", "/|▓▓▓|  ,,", COUCH),
        ("  ·  •", " (¬‿¬)", BODY, COUCH),
    ),
})

IDLE_BY_MOOD = {
    "comfy": ["chill", "tea", "phone", "stretch", "game", "eat", "scratch",
              "burp", "nosepick"],
    "sleepy": ["sleep", "nap"],
    "grumpy": ["sus", "facepalm"],
    "furious": ["rage"],
}

from . import looks  # noqa: E402
from .rooms import ROOMS  # noqa: E402  (rooms replace the couch versions of these emotes)

EMOTES.update(ROOMS)
EMOTES.update(looks.shared.EMOTES)
EMOTES.update(looks.SIGNATURES)

# While he's saying something he's awake and doing something that fits the line.
TALKING = ["chill", "tea", "scratch", "phone", "eat"]
# Each goblin's own habits (shared moves he likes plus his signature ones) live in looks/.
LIFE_EMOTES = {"song": ["hype", "love", "chill"], "discord": ["phone", "sus"], "dm": ["phone", "sus"],
               "youtube": ["phone", "laugh"], "whatsapp": ["phone", "sus"], "github": ["think", "phone"],
               "steam": ["game"], "sim companies": ["think", "flex"]}
# First match wins; checked against the lowercased line template.
LINE_EMOTES = [
    (("zzz", "*snore", "*mumbles", "*drools", "*rolls over"), "sleep"),
    (("*burp", "*farts"), "burp"),
    (("*scratch",), "scratch"),
    (("*yawns", "stretch", "yawn"), "stretch"),
    (("*picks", "*sniffs"), "nosepick"),
    (("chip", "pizza", "fry ", "ate today", "eat", "munchies"), "eat"),
    (("blunt", "joint", "smoke", "puff", "spark", "420", "lighter"), "smoke"),
    (("trip", "colors", "woah", "the walls"), "trip"),
    (("proud", "you're doing aight"), "love"),
    (("stack overflow", "lemme guess", "judging"), "roast"),
    (("advice", "ctrl+z", "if it compiles", "you know what goes hard"), "tip"),
    (("water", "call your mom", "posture", "go to bed", "go sleep", "sleep is free"), "think"),
]


def for_line(template: str, kind: str | None, feeling: str, seed: str, name: str = "") -> str:
    """An emote that fits what he's saying. `kind` is the life topic, if any."""
    def pick(options: list[str]) -> str:
        return options[zlib.crc32(seed.encode()) % len(options)]

    if kind in LIFE_EMOTES:
        return pick(LIFE_EMOTES[kind])
    lowered = template.lower()
    for words, emote in LINE_EMOTES:
        if any(w in lowered for w in words):
            return emote
    if feeling in ("grumpy", "furious"):
        return pick(IDLE_BY_MOOD[feeling])
    return pick(looks.habits(name) or TALKING)
