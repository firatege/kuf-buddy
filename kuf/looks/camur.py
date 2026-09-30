"""Çamur's own animations and habits."""

import string

from ._kit import scene

NAME = "Çamur"
HABITS = ['trip', 'stretch']             # shared emotes he falls back to; his own ones are added too
ACCEPTS_JOINT = 0.95           # chance he takes the joint when Snoop passes it
REFUSAL = ''

COUCH = "▐█▄▄▄▄▄▄▄█▌"
TEXT = dict.fromkeys(string.ascii_letters + string.digits + ".,!?'", "y")
LAMP = dict.fromkeys("╭╮╰╯─│▀", "m")
COSMOS = dict.fromkeys("✦✧˚·*◇○◎╲╱│─~≈", "r")

EMOTES: dict[str, dict] = {
    "camur-lavalamp": scene("zoned out on the lava lamp, blobs rising forever", [
        ["            ╭──╮",
         "  (˘‿˘)     │  │",
         "▐▌/|▓▓▓|\\▐▌ │● │",
         COUCH + " ╰▀▀╯"],
        ["            ╭──╮",
         "  (◕‿◕)     │ ●│",
         "▐▌/|▓▓▓|\\▐▌ │∘ │",
         COUCH + " ╰▀▀╯"],
        ["   woah...  ╭●─╮",
         "  (@‿@)     │∘ │",
         "▐▌/|▓▓▓|\\▐▌ │  │",
         COUCH + " ╰▀▀╯"],
        ["   ...bro   ╭──╮",
         "  (˘ω˘)     │ ∘│",
         "▐▌/|▓▓▓|\\▐▌ │ ●│",
         COUCH + " ╰▀▀╯"],
    ], {**TEXT, **LAMP, "●": "e", "∘": "e"}),
    "camur-clouds": scene("lying on the floor watching clouds, they all look like dicks", [
        ["  ▗▟█▙▖     ▄▄  ",
         "                ",
         " (˘‿˘)▓▓▓══     ",
         "▔▔▔▔▔▔▔▔▔▔▔▔▔▔  "],
        [" ▟█▙▖     ▄▄    ",
         "      bro...    ",
         " (˘ᴗ˘)▓▓▓══     ",
         "▔▔▔▔▔▔▔▔▔▔▔▔▔▔  "],
        ["▟▙▖     ▄▄    ▗▟",
         " that one's a   ",
         " (◕‿◕)▓▓▓══     ",
         "▔▔▔▔▔▔▔▔▔▔▔▔▔▔  "],
        ["▙      ▄▄    ▗▟█",
         "  ...dick. lol  ",
         " (ˆ▽ˆ)▓▓▓══     ",
         "▔▔▔▔▔▔▔▔▔▔▔▔▔▔  "],
    ], {**TEXT, "▗": "s", "▟": "s", "█": "s", "▙": "s", "▖": "s", "▄": "s", "▔": "w"}),
    "camur-galaxy": scene("'what if...': a galaxy spinning above his head", [
        [" ˚·✦  ─◎─  ✧·˚  ",
         "  (˘‿˘) hmm.    ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        ["  ·✧˚ ╲◎╲ ˚·✦   ",
         "  (°‿°) what if ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        [" ✦˚·  │◎│  ·˚✧  ",
         "  (◉‿◉) we're   ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        ["  ✧·˚ ╱◎╱ ·✦˚   ",
         "  (@_@) the bug?",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
    ], {**TEXT, **COSMOS}),
    "camur-mudbath": scene("soaking in a warm mud bath, blorping bubbles", [
        ["                ",
         "    (-‿-)    °  ",
         "▐▒▒/|▓▓▓|\\▒°▒▌  ",
         "▝▀▀▀▀▀▀▀▀▀▀▀▀▘  "],
        ["             °  ",
         "    (˘‿˘)   ○   ",
         "▐░▒/|▓▓▓|\\▒▒░▌  ",
         "▝▀▀▀▀▀▀▀▀▀▀▀▀▘  "],
        ["            ○   ",
         "    (˘ε˘)ﾉ      ",
         "▐▒░/|▓▓▓| ▒°▒▌  ",
         "▝▀▀▀▀▀▀▀▀▀▀▀▀▘  "],
        ["  ·  blorp  *   ",
         "    (ˆ‿ˆ)    °  ",
         "▐▒▒/|▓▓▓|\\░▒▒▌  ",
         "▝▀▀▀▀▀▀▀▀▀▀▀▀▘  "],
    ], {**TEXT, "▒": "w", "░": "w", "°": "w", "○": "w", "·": "w", "*": "w",
        "▐": "m", "▌": "m", "▝": "m", "▀": "m", "▘": "m"}),
    "camur-float": scene("floating up off the couch into the cosmos", [
        ["      ˚         ",
         "  (-‿-)         ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        ["  ˚    ✧   ·    ",
         "  (˘‿˘)    ˚    ",
         "  ~|▓▓▓|~       ",
         "▐▌ ˚ · ˚ ▐▌     "],
        ["✦   ·  ✧    ˚   ",
         "  (◉‿◉)  ·      ",
         " ✧ |▓▓▓| ✧      ",
         "   ˚  ·  ˚      "],
        [" ✧ i am couch ✧ ",
         " \\(@‿@)/  ˚     ",
         "  ~|▓▓▓|~   ·   ",
         " ·   ˚   ·    ✦ "],
    ], {**TEXT, **COSMOS}),
}
