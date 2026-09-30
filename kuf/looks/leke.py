"""Leke's own animations and habits."""

from ._kit import scene

NAME = "Leke"
HABITS = ['cry', 'love']             # shared emotes he falls back to; his own ones are added too
ACCEPTS_JOINT = 0.4           # chance he takes the joint when Snoop passes it
REFUSAL = 'worried about her voice before the show'

TALK = {c: "y" for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!?.,'"}
COUCH = "▐█▄▄▄▄▄▄▄█▌"
STAGE = "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
SOFA = "▐█▄▄▄▄▄█▌"
MIRROR_FLOOR = " ▔▔▔▔▔▔┻▔▔▔▔▔▔  "

EMOTES: dict[str, dict] = {
    "leke-spotlight": scene("center stage in the spotlight, bowing while the roses rain in", [
        ["   ╲   ✦   ╱    ",
         "    (ˆ▽ˆ)/    ✿ ",
         "   /|▓▓▓|       ",
         STAGE],
        ["   ╲   ✦   ╱  ✿ ",
         "    (˘▽˘)ﾉ  ✿   ",
         "   /|▓▓▓|\\      ",
         STAGE],
        ["  ╲  bravo!  ╱  ",
         "    (≧▽≦)  ✿    ",
         "   \\|▓▓▓|/ ✿ ✿  ",
         STAGE],
        ["  ╲ thank u ╱   ",
         "  ✿ (ˆ‿ˆ)✿      ",
         "   /|▓▓▓|\\ ✿✿✿  ",
         STAGE],
    ], {**TALK, "╲": "y", "╱": "y", "✦": "y", "✿": "e", "▄": "w"}),
    "leke-mirror": scene("mirror selfie: pose, duck face, flash, hates it, again", [
        ["  pose ┃ esop   ",
         " (ˆ‿ˆ)▯┃▯(ˆ‿ˆ)  ",
         " |▓▓▓|/┃\\|░░░|  ",
         MIRROR_FLOOR],
        ["  mwah ┃ hawm   ",
         " (˘з˘)▯┃▯(˘з˘)  ",
         " |▓▓▓|/┃\\|░░░|  ",
         MIRROR_FLOOR],
        [" ✦  ✧  ┃  ✧  ✦  ",
         " (>‿<)✸┃✸(>‿<)  ",
         " |▓▓▓|/┃\\|░░░|  ",
         MIRROR_FLOOR],
        [" again ┃ niaga  ",
         " (ಠ_ಠ)▯┃▯(ಠ_ಠ)  ",
         " |▓▓▓|/┃\\|░░░|  ",
         MIRROR_FLOOR],
    ], {**TALK, "┃": "w", "┻": "w", "▔": "w", "░": "c", "▯": "m", "✸": "y", "✦": "y", "✧": "y"}),
    "leke-faint": scene("clutches her chest and faints onto the couch, peeks to check who saw", [
        ["   oh no...     ",
         "  (ಥ_ಥ)ﾉ       ",
         "  /|▓▓▓|        ",
         "   / \\ " + SOFA],
        ["   i can't...   ",
         "   (ಥдಥ)ﾉ      ",
         "   /|▓▓▓|       ",
         "   / / " + SOFA],
        ["     *swoon*    ",
         "       ~(×д×)   ",
         "        ╲▓▓▓╲   ",
         "       " + SOFA],
        ["   did anyone   ",
         "     see that?  ",
         "       (×_ಠ)▓▓▓═",
         "       " + SOFA],
    ], {**TALK, "*": "y", "~": "s", "▐": "w", "█": "w", "▄": "w", "▌": "w"}),
    "leke-oscar": scene("tearful award speech clutching the trophy, refuses to be played off", [
        ["  ♛             ",
         "  ﾉ(ಥ‿ಥ)        ",
         "   |▓▓▓|\\       ",
         STAGE],
        ["  ♛ i'd like to ",
         "  ﾉ(ಥ‿ಥ) thank  ",
         "   |▓▓▓|\\       ",
         STAGE],
        ["  ♛ my mom, my  ",
         "  ﾉ(ಥдಥ) agent  ",
         "   |▓▓▓|\\       ",
         STAGE],
        ["  ♛ ♪♫ wrap up  ",
         "  ﾉ(ಠдಠ)NOT DONE",
         "   |▓▓▓|\\       ",
         STAGE],
    ], {**TALK, "♛": "y", "♪": "e", "♫": "e", "▄": "w"}),
    "leke-fan": scene("fanning herself on the couch like she's dying of the vapors", [
        ["   so hot...    ",
         "  (˘д˘)ﾉ◤  ≈   ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["  i'm MELTING   ",
         "  (˘д˘)ﾉ◣ ≈    ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["  WATER, darling",
         "  (ಥдಥ)ﾉ◤≈  ≈  ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["   *pant pant*  ",
         "  (×д×)ﾉ◣  ≈   ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
    ], {**TALK, "*": "y", "◤": "e", "◣": "e", "≈": "s"}),
}
