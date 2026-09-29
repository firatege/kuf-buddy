"""What happened (events), how Küf feels about it (mood), and his canned lines
for when Claude doesn't voice him."""

import re
import zlib
from datetime import datetime
from pathlib import Path

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
        "*scratches belly* nobody touched shit. perfect.",
        "found a chip under the cushion. it's mine now, fuck off.",
        "don't refactor. just lie down. like me.",
        "this couch has seen things. so has your codebase.",
        "*burp* ...the tests can wait.",
        "haven't showered since the last deploy. no regrets.",
        "wake me up when something breaks.",
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
        "ok ok it passed. don't get cocky.",
        "look at that, it works. i'm tearing up. it's the mold.",
    ],
    "retort": [
        "{them} {where} thinks he's funny. he isn't.",
        "lmao listen to {them} {where}: \"{snippet}\". clown.",
        "yo {them}, mind your own damn terminal.",
        "{them} {where} is yapping again. *throws a chip at him*",
        "nobody asked you, {them}. go touch grass. or mold.",
    ],
    "comeback": [
        "{them} came at me?? your code smells worse than me, {them}.",
        "oh {them} wants smoke. bring it, you crusty bastard.",
        "talk to me when your tests pass, {them}.",
        "{them} {where} talking shit again. i'll eat your crumbs, bitch.",
    ],
    "night": [
        "it's {hour}:00. real goblins are asleep. so should you be.",
        "*snore* ...commit tomorrow, dumbass...",
    ],
}


def classify(path: str) -> str:
    lowered = path.lower()
    if any(marker in lowered for marker in PROMPT_MARKERS):
        return "prompt"
    return "code" if Path(lowered).suffix in CODE_EXTS else "stuff"


def pick(options: list, seed: str):
    return options[zlib.crc32(seed.encode()) % len(options)]


def _fields(event: dict | None, n: int) -> dict:
    event = event or {}
    return {"file": Path(event.get("file", "")).name or "that file",
            "cmd": (event.get("cmd") or "that").split()[0] if event.get("cmd") else "that",
            "n": n, "hour": f"{datetime.now().hour:02d}"}


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
    if 1 <= datetime.now().hour < 6:
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
