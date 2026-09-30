"""Kir's own animations and habits."""

import string

from ._kit import scene

NAME = "Kir"
HABITS = ['tip', 'think']             # shared emotes he falls back to; his own ones are added too
ACCEPTS_JOINT = 0.3           # chance he takes the joint when Snoop passes it
REFUSAL = 'claims it hurts his 10x productivity'

COUCH = "▐█▄▄▄▄▄▄▄█▌"
TEXT = dict.fromkeys(string.ascii_letters + string.digits + ".,!?'*$²", "y")
BOARD = dict.fromkeys("┌┐└┘│┬", "m")

EMOTES: dict[str, dict] = {
    "kir-whiteboard": scene("drawing the architecture on a whiteboard: db, arrow, ai, arrow, money", [
        ["┌────────┐      ",
         "│[db]    │ (¬‿¬)",
         "│        │ﾉ|▓▓▓|",
         "└┬──────┬┘  / \\ "],
        ["┌────────┐      ",
         "│[db]──┐ │ (¬‿¬)",
         "│      ↓ │ﾉ|▓▓▓|",
         "└┬──────┬┘  / \\ "],
        ["┌────────┐      ",
         "│[db]──┐ │ (ಠ‿ಠ)",
         "│[ai]←─┘ │ﾉ|▓▓▓|",
         "└┬──────┬┘  / \\ "],
        ["┌────────┐ ez.  ",
         "│[db]──┐ │ (¬▽¬)",
         "│[$$]←─┘ │ﾉ|▓▓▓|",
         "└┬──────┬┘  / \\ "],
    ], {**TEXT, **BOARD, "─": "e", "↓": "e", "←": "e", "[": "c", "]": "c", "$": "g"}),
    "kir-10x": scene("typing on three keyboards at once, one of them with his foot", [
        [" clack   tak    ",
         "   (ò_ó)        ",
         "▦▦\\|▓▓▓|_▩▦     ",
         "    / \\▦▦▦      "],
        ["   tik  clack   ",
         "   (ó_ò)        ",
         "▩▦_|▓▓▓|/▦▦     ",
         "    / ‾▦▩▦      "],
        [" 10x   tak  tik ",
         "   (ò‿ó)        ",
         "▦▦\\|▓▓▓|_▦▩     ",
         "    / \\▩▦▦      "],
        [" shipped. ez    ",
         "  (⌐■_■)        ",
         "▦▦\\|▓▓▓|/▦▦     ",
         "    / \\▦▦▦      "],
    ], {**TEXT, "▦": "m", "▩": "c", "■": "c", "⌐": "m"}),
    "kir-glasses": scene("smugly pushing his glasses up, lens glint, 'actually...'", [
        ["    *ahem*      ",
         "  (□_□)         ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        ["                ",
         "  (□_□)ﾉ        ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["       ✦        ",
         "  (■_■)ﾉ        ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["  ✧ actually... ",
         "  (■‿■)         ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
    ], {**TEXT, "□": "m", "■": "c", "✦": "y", "✧": "y"}),
    "kir-lecture": scene("lecturing with a pointer stick, tapping the board", [
        [" listen up.     ",
         " (¬‿¬)   ┌────┐ ",
         "/|▓▓▓|━━━│n²  │ ",
         " / \\     └────┘ "],
        [" *tap* *tap*    ",
         " (¬‿¬)  ╱┌────┐ ",
         "/|▓▓▓|╱  │n²→ │ ",
         " / \\     └────┘ "],
        [" n² is for noobs",
         " (ಠ▽ಠ)   ┌────┐ ",
         "/|▓▓▓|━━━│n²→n│ ",
         " / \\     └────┘ "],
        [" any questions? ",
         " (¬_¬)   ┌────┐ ",
         "/|▓▓▓|━━━│n²→1│ ",
         " / \\     └────┘ "],
    ], {**TEXT, **BOARD, "─": "m", "━": "w", "╱": "w", "→": "e"}),
    "kir-coffee": scene("hooked up to a coffee IV drip, eyes slowly opening", [
        ["  ┌▆┐   sip...  ",
         "  └┬┘  (-_-)    ",
         "   ╰──/|▓▓▓|\\▐▌ ",
         "    ▐█▄▄▄▄▄▄▄█▌ "],
        ["  ┌▅┐           ",
         "  └┬┘  (-_-)    ",
         "   •──/|▓▓▓|\\▐▌ ",
         "    ▐█▄▄▄▄▄▄▄█▌ "],
        ["  ┌▃┐    !      ",
         "  └┬┘  (°_°)    ",
         "   ╰•─/|▓▓▓|\\▐▌ ",
         "    ▐█▄▄▄▄▄▄▄█▌ "],
        ["  ┌▂┐ ✦10x✦     ",
         "  └┬┘  (⊙▽⊙)ﾉ   ",
         "   ╰─•/|▓▓▓| ▐▌ ",
         "    ▐█▄▄▄▄▄▄▄█▌ "],
    ], {**TEXT, **BOARD, "╰": "m", "─": "m", "▆": "w", "▅": "w", "▃": "w", "▂": "w",
        "•": "w", "✦": "y"}),
}
