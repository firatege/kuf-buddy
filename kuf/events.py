"""What happened (events), how Küf feels about it (mood), and his canned solo lines
for when Claude doesn't voice him. Talk between goblins is never canned: Claude
writes every jab, reply and last word through kuf_react."""

import re
import zlib
from datetime import datetime
from pathlib import Path

from .clock import is_night
from .config import user_name

GRUMPY_WINDOW_S = 180
FURIOUS_WINDOW_S = 420
RAMPAGE_EDITS = 12

PROMPT_MARKERS = ("claude.md", "agents.md", "/rules/", "/skills/", "/agents/",
                  "/commands/", "/memory/", "prompt", "system_msg", ".cursorrules")
CODE_EXTS = {".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".vue", ".go", ".c", ".h",
             ".cpp", ".java", ".kt", ".swift", ".sh", ".qml", ".sql", ".lua", ".rb",
             ".php", ".cs", ".zig", ".toml", ".yml", ".yaml", ".json", ".css", ".html"}
TEST_CMD = re.compile(r"\b(pytest|cargo test|npm (run )?test|pnpm test|bun test|go test|vitest|jest)\b")

LINES = {
    "idle": [
        "yo {user}, drink some water. you look like me.",
        "you good {user}? blink twice if claude is holding you hostage.",
        "{user} if you refactor one more thing i'm moving out.",
        "*scratches belly* nobody touched shit. perfect.",
        "found a chip under the cushion. it's mine now, fuck off.",
        "don't refactor. just lie down. like me.",
        "this couch has seen things. so has your codebase.",
        "*burp* ...the tests can wait.",
        "haven't showered since the last deploy. no regrets.",
        "wake me up when something breaks.",
        "bro when's the last time you touched grass. deadass asking.",
        "{user}, your posture is a war crime. sit up, my boy.",
        "i'd help but that sounds like effort.",
        "*picks something out of his teeth* ...where were we.",
        "no cap, this couch is the only stable thing in your life.",
        "{user} you ate today? chips count. i checked.",
        "somebody order pizza. i ain't paying tho.",
        "i'm not lazy, i'm in power saving mode, bitch.",
        "your git log reads like a diary of a madman, bro.",
        "one day you'll write docs. and i'll get up. neither is happening.",
        "{user}, stretch. your spine is filing a complaint.",
        "*farts into the cushion* ...that's staying there.",
        "who keeps stealing my remote? oh wait. i'm sitting on it.",
        "bro your desk is dirtier than me. that's an achievement.",
        "i've been on this couch so long it has my shape now.",
        "rent's due and i'm still not paying, my boy.",
        "real talk {user}, you're doing aight. don't let it go to your head.",
        "stack overflow called. they want their code back.",
        "if it compiles, ship it. that's my whole philosophy.",
        "*yawns* is it friday yet? no? fuck.",
        "i dreamt your tests passed. woke up screaming.",
        "bro i found a fry from 2023 in here. still good.",
        "don't mind me, just judging your variable names.",
        "the couch cushion ate my phone again. damn thing's hungry.",
        "{user}, call your mom. i'll wait. i ain't going anywhere.",
        "every time you say 'quick fix' a goblin loses his crumbs.",
        "lemme guess. 'it worked on my machine'. classic.",
        "i'm lowkey proud of you {user}. don't tell nobody.",
        "*scratches* ...i think something lives in this couch with me.",
        "ctrl+z won't fix your life, my boy. but it's a start.",
        "you know what goes hard? naps. try one.",
        "your todo list is longer than my unpaid tabs.",
        "bro i'm the only one here who never crashed. respect me.",
        "tabs vs spaces? i vote couch.",
        "if you need me i'll be right here. forever. literally.",
        "{user}, stop reading the status line and go do shit.",
        "that bug ain't gonna fix itself. neither am i.",
        "yo, who left the terminal open all night? oh right, you.",
        "*sniffs the air* ...smells like technical debt in here.",
        "i'd give you advice but you'd ignore it like the linter.",
    ],
    "code": [
        "yo who touched {file}? it was perfectly broken.",
        "{file}?? i was SLEEPING on that one, damn.",
        "another edit to {file}. did anyone ask? no.",
        "you call that a fix? i've seen cleaner socks.",
        "stop polishing {file}, it's a trash fire and i like it warm.",
        "claude's rearranging my damn furniture again ({file}).",
    ],
    "prompt": [
        "HEY. hands OFF {file}. those are the boss's words, robot.",
        "claude rewrote a prompt ({file}). who the fuck asked?",
        "editing prompts now?? next you'll clean the couch.",
        "{file} was fine. prompts are sacred. like my crumbs.",
    ],
    "rampage": [
        "{n} edits this session. claude, sit the fuck DOWN.",
        "{n} changes?! i'm losing my crumbs over here.",
    ],
    "fail": [
        "LMAO it blew up. {cmd} said no.",
        "{cmd} failed. shocking. truly. *slow clap*",
        "red again? bro that's not a color scheme, that's a cry for help.",
        "that command faceplanted harder than me off this couch.",
    ],
    "win": [
        "tests green?? who are you and what did you do with my boy.",
        "ok ok it passed. don't get cocky, {user}.",
        "look at that, it works. i'm tearing up. it's the mold.",
    ],
    "greet": [
        "*crawls onto the couch* sup {user}. what are we breaking today?",
        "yo {user}. i'm {name}. i live here now. don't touch my crumbs.",
        "another terminal? {user}, you have a problem. i'm {name}, btw.",
        "{name} reporting for duty. by duty i mean lying down. hi {user}.",
        "*yawns* {user}, you woke me up. this better be good.",
        "back again {user}? fine. {name}'s on the couch. do your thing.",
    ],
    "night": [
        "it's {hour}:00. real goblins are asleep. so should you be.",
        "*snore* ...commit tomorrow, dumbass...",
        "zzz... {user}... the bug... it's in the... zzz",
        "*snore* ...five more minutes... of not caring...",
        "{user} go to bed. the code will still suck in the morning.",
        "it's {hour}:00, {user}. nothing good gets pushed after 2am.",
        "*mumbles* ...who moved my crumbs... *snore*",
        "zzz... dreaming about a codebase with tests... nightmare...",
        "{user} your eyes look like my couch. go sleep.",
        "*snore* ...no... not another refactor... zzz",
        "zzz... {user}... you forgot to push... jk... zzz",
        "{hour}:00? bro even the mold is asleep.",
        "*drools on the cushion* ...leave me alone...",
        "whatever you're fixing at {hour}:00, you'll break it again at 9.",
        "zzz *farts in his sleep* ...zzz",
        "{user}, sleep is free. unlike your mistakes at {hour}:00.",
        "*snore* ...merge conflict... in my dreams... again...",
        "go to sleep {user}. claude doesn't need you. i don't need you. night.",
        "zzz... stack overflow... is down... everyone go home... zzz",
        "*rolls over* ...if you wake me up it better be a prod outage.",
        "it's {hour}:00 and you're still here. respect. now fuck off to bed.",
        "zzz... {user}'s mom called... said go to sleep... zzz",
        "*snore* ...rm -rf my problems... zzz",
        "the night shift is you and me, {user}. and i'm asleep. so it's you.",
    ],
}


def classify(path: str) -> str:
    lowered = path.lower()
    if any(marker in lowered for marker in PROMPT_MARKERS):
        return "prompt"
    return "code" if Path(lowered).suffix in CODE_EXTS else "stuff"


def pick(options: list, seed: str):
    return options[zlib.crc32(seed.encode()) % len(options)]


def chance(seed: str, tag: str, pct: int) -> bool:
    """A stable `pct`% roll for this seed (the same slot always rolls the same)."""
    return zlib.crc32(f"{seed}|{tag}".encode()) % 100 < pct


def _fields(event: dict | None, n: int) -> dict:
    event = event or {}
    return {"user": user_name(),
            "file": Path(event.get("file", "")).name or "that file",
            "cmd": (event.get("cmd") or "that").split()[0] if event.get("cmd") else "that",
            "n": n, "hour": f"{datetime.now().hour:02d}"}


def candidates(kind: str, event: dict | None, n: int, **extra: str) -> list[tuple[str, str]]:
    """Every (template, filled line) of one kind."""
    fields = {**_fields(event, n), **extra}
    return [(t, t.format(**fields)) for t in LINES[kind]]


def canned(kind: str, event: dict | None, n: int, seed: str, **extra: str) -> str:
    return pick(LINES[kind], seed).format(**{**_fields(event, n), **extra})


def edit_count(events: list[dict]) -> int:
    return sum(1 for e in events if e.get("kind") in ("code", "prompt", "stuff"))


def mood(events: list[dict], now: float) -> tuple[str, str, dict | None]:
    """Return (mood, line kind, triggering event) from one terminal's recent events."""
    last = events[-1] if events else None
    age = now - last["ts"] if last else float("inf")
    if last and last.get("kind") == "prompt" and age < FURIOUS_WINDOW_S:
        return "furious", "prompt", last
    if edit_count(events) >= RAMPAGE_EDITS and age < GRUMPY_WINDOW_S:
        return "furious", "rampage", last
    if last and last.get("kind") in ("code", "stuff", "fail") and age < GRUMPY_WINDOW_S:
        return "grumpy", "fail" if last["kind"] == "fail" else "code", last
    if is_night(datetime.now().hour):
        return "sleepy", "night", None
    return "comfy", "idle", None


FALLBACK_EMOTE = {"prompt": "rage", "rampage": "tableflip", "fail": "roast",
                  "code": "sus", "win": "flex", "stuff": "shrug"}


def turn_fallback(turn_events: list[dict], edits: int) -> tuple[str, str] | None:
    """Pick (emote, line) summarizing a turn Claude didn't react to. None = stay quiet."""
    if not turn_events:
        return None
    seed = str(turn_events[-1]["ts"])
    by_kind = {e["kind"]: e for e in turn_events}
    for kind in ("prompt", "fail"):
        if kind in by_kind:
            return FALLBACK_EMOTE[kind], canned(kind, by_kind[kind], edits, seed)
    if edits >= RAMPAGE_EDITS:
        return FALLBACK_EMOTE["rampage"], canned("rampage", None, edits, seed)
    if "win" in by_kind:
        return FALLBACK_EMOTE["win"], canned("win", by_kind["win"], edits, seed)
    if "code" in by_kind or "stuff" in by_kind:
        event = by_kind.get("code") or by_kind["stuff"]
        return FALLBACK_EMOTE["code"], canned("code", event, edits, seed)
    return None
