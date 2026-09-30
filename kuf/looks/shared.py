"""Animations every goblin can use that aren't tied to a room: the joint, and saying no to it."""

from ._kit import scene

SMOKE = {"░": "s", "▒": "s", "▓": "s", "~": "s", "*": "e", "✸": "e", "═": "g"}   # joint paper is green
COUCH = "▐█▄▄▄▄▄▄▄█▌"

EMOTES = {
    "joint": scene("holding the joint: takes it, drags, exhales, passes it on", [
        ["     ✧          ",
         "  (ˆ‿ˆ)y═*      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["         ░      ",
         "  (˘ε˘)y═✸      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["   ░▒▓▒░  ~     ",
         "  (˘‿˘)y═*      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["  ░   ▒   ░     ",
         "  (ˆ‿ˆ)ﾉ═* pass ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
    ], {**SMOKE, "✧": "y", "p": "y", "a": "y", "s": "y"}),
    "nope": scene("turning it down, hands up", [
        ["     ?          ",
         "  (ಠ_ಠ)         ",
         "▐▌/|▓▓▓|\\▐▌     ",
         COUCH],
        ["   nah          ",
         "  (¬_¬)ﾉ ✗      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["      nope      ",
         "  (ಠ‿ಠ)ﾉ ✗      ",
         "▐▌/|▓▓▓| ▐▌     ",
         COUCH],
        ["                ",
         "  \\(ಠ_ಠ)/      ",
         "▐▌ |▓▓▓| ▐▌     ",
         COUCH],
    ], {"?": "y", "n": "y", "a": "y", "h": "y", "o": "y", "p": "y", "e": "y", "✗": "e"}),
}
