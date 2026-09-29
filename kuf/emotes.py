"""Küf's emote sheet: a filthy couch goblin, 4 rows tall, 2 animation frames each.

Row order is always: effects/flies, face, body, couch.
"""

COUCH = "▀█▀▀▀▀▀▀█▀"
BODY = "/|▓▓▓|\\ ,,"
SLOUCH = " |▓▓▓|~ ,,"


def _emote(desc: str, frame_a: tuple, frame_b: tuple) -> dict:
    return {"desc": desc, "frames": [list(frame_a), list(frame_b)]}


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

IDLE_BY_MOOD = {
    "comfy": ["chill", "eat", "scratch", "burp"],
    "sleepy": ["sleep"],
    "grumpy": ["sus", "facepalm"],
    "furious": ["rage"],
}
