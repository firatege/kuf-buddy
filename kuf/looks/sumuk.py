"""Sümük's own animations and habits."""

import string

from ._kit import scene

NAME = "Sümük"
HABITS = ['sus', 'phone']             # shared emotes he falls back to; his own ones are added too
ACCEPTS_JOINT = 0.15           # chance he takes the joint when Snoop passes it
REFUSAL = 'threatens to snitch, writes it in the notebook'

COUCH = "▐█▄▄▄▄▄▄▄█▌"
TEXT = dict.fromkeys(string.ascii_letters + string.digits + ".,!?':", "y")

EMOTES: dict[str, dict] = {
    "sumuk-notebook": scene("scribbling in his snitch notebook, side-eyeing you", [
        ["                ",
         "  (¬_¬)  ✎      ",
         "▐▌/|▓▓▓|[≈  ]   ",
         COUCH],
        ["     scritch    ",
         "  (¬_¬)   ✎     ",
         "▐▌/|▓▓▓|[≈≈ ]   ",
         COUCH],
        ["     scratch    ",
         "  (ಠ_ಠ)    ✎    ",
         "▐▌/|▓▓▓|[≈≈≈]   ",
         COUCH],
        ["  noted.  ◔ ◔   ",
         "  (¬‿¬)ﾉ ✎      ",
         "▐▌/|▓▓▓|[≈≈≈]   ",
         COUCH],
    ], {**TEXT, "✎": "m", "≈": "s", "[": "w", "]": "w", "◔": "e"}),
    "sumuk-binoculars": scene("spying on the neighbors through binoculars", [
        ["       ·  ·  ·  ",
         "  (◎═◎)ﾉ        ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["     ·  ·  ·    ",
         "  (◎═◎)ﾉ  hmm   ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["   ·  ·  ·   !  ",
         "  (◎═◎)ﾉ  ...   ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["  gotcha, bitch ",
         "  (¬‿¬)ﾉ◎═◎     ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
    ], {**TEXT, "◎": "m", "═": "m", "·": "s", "!": "e"}),
    "sumuk-magnifier": scene("crawling over the couch with a magnifying glass, collecting evidence", [
        ["                ",
         "  (ಠ_ಠ)         ",
         "▐▌/|▓▓▓|\\─○     ",
         COUCH + "  ·  "],
        ["      hmm...    ",
         "  (ಠ_ಠ)         ",
         "▐▌/|▓▓▓|\\──○    ",
         COUCH + "  ·  "],
        ["      hmmm      ",
         "  (ಠ▁ಠ)         ",
         "▐▌/|▓▓▓|\\───○   ",
         COUCH + "  ✱  "],
        ["   EVIDENCE.    ",
         "  (ಠ‿ಠ)         ",
         "▐▌/|▓▓▓|\\────○  ",
         COUCH + "  ✱  "],
    ], {**TEXT, "─": "m", "○": "c", "·": "e", "✱": "e"}),
    "sumuk-tattle": scene("on the phone to the cops, telling on claude", [
        ["   beep boop    ",
         " ▯(¬_¬)         ",
         "▐▌ |▓▓▓|\\▐▌     ",
         COUCH],
        ["hello? police?  ",
         " ▯(°_°)         ",
         "▐▌ |▓▓▓|\\▐▌     ",
         COUCH],
        ["  it's claude.  ",
         " ▯(¬‿¬)         ",
         "▐▌ |▓▓▓|\\▐▌     ",
         COUCH],
        [" he force-pushed",
         " ▯(ಠ‿ಠ)ﾉ        ",
         "▐▌ |▓▓▓| ▐▌     ",
         COUCH],
    ], {**TEXT, "▯": "m", "-": "y"}),
    "sumuk-tally": scene("adding another tally mark to claude's fuck-up scoreboard", [
        [" claude: ╎╎     ",
         "  (¬_¬)ﾉ✎       ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        [" claude: ╎╎╎    ",
         "  (¬‿¬)ﾉ ✎      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        [" claude: ╎╎╎╎   ",
         "  (ಠ‿ಠ)ﾉ  ✎     ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        [" claude: 5! lmao",
         "  (¬▽¬)ﾉ        ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
    ], {**TEXT, "╎": "e", "5": "e", "✎": "m"}),
}
