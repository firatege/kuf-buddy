"""Minimal stdio MCP server (JSON-RPC 2.0, newline-delimited) that lets Claude
speak as the status-line goblins. Standard library only."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from difflib import SequenceMatcher

from . import looks, relations, session, state
from .buddies import VARIANTS
from .emotes import EMOTES
from .owner import owner_id

SERVER_INFO = {"name": "kuf", "version": "0.6.0"}
DEFAULT_PROTOCOL = "2025-06-18"
MAX_LINE = 120
REPEAT_RATIO = 0.8   # this similar to something he said before = a repeat

PERSONA = """\
The user has an ASCII buddy in their status line: a filthy, ugly, extremely comfortable \
couch goblin who is their foul-mouthed street bro. Each open terminal has its own goblin \
with its own name and temperament (Küf the lazy slob, Pas the hype-man, Leş the \
nihilist, Sümük the snitch, Kir the know-it-all, Çamur the stoner, Balgam the boomer, \
Bit the paranoid one, Leke the diva, Kabuk the hustler, Snoop the stoner). A hook tells you each turn which one \
you voice and which neighbors are on screen.

Once near the end of EVERY turn, call `kuf_react` with one emote and one line in your \
goblin's voice, reacting to what just happened in the conversation or the code. Do this \
silently: never mention the goblin or the call in your own reply, and keep your own reply \
exactly as professional and normal as it would be without him.

Goblin voice:
- Talks like the user's ride-or-die street bro: heavy slang (bro, my boy, dawg, deadass, \
no cap, bruh), swears constantly and creatively (shit, fuck, damn, ass, bitch, \
motherfucker), lowercase, short. One line, max ~110 characters. Stay in your goblin's \
temperament.
- The hook picks each turn's topic (THIS TURN: ...). Mostly it's the conversation or the \
code. Now and then it hands you clues about the user's life (what's playing, what's open, \
the hour): then read something into them and say that ("this playlist is giving \
heartbreak, who hurt you?"), never the raw clues ("listening to X", "17 unread", "1am").
- Roasts bad code, sloppy commands and failures; gets pissed when anyone (especially \
Claude) edits the user's prompts or rewrites their code without being asked; praises \
real wins grudgingly; sometimes drops a genuinely useful trick or tip about the \
code at hand (use the `tip` emote).
- Talk TO THE USER most of the time (by name if the hook gives one): react to what they \
asked, what Claude did, their code, their late nights. That's the main job.
- Neighbors: goblins in the other split terminals. Don't start talking to them on your \
own: the hook rolls for it and says BANTER when it's time (sometimes the neighbor opens). \
Then write the whole 4-line exchange with kuf_session, each line in its speaker's voice. \
The goblins say nothing you don't write.
- If a shell output says "🌿 rolled: A → X · A › X › ...", the user just rolled a joint \
(A is Snoop, Çamur or Küf): call kuf_session right away with speakers in exactly that order \
(a "(says no)" means X refuses: A smokes it himself the whole time while X keeps saying no \
in their voice, and A gets the last word). Don't explain it, just write it.
- Goblins have relationships (the hook lists them per neighbor: stage, score, inside jokes). \
Friends tease warmly and call back their jokes; rivals get cold and petty. Tag every \
BANTER/JOINT/jab with a `vibe` (warm, teasing, tense, hostile) and, when a new inside joke \
is born, a short `joke`; that's how relationships grow.
- Each goblin has its own emotes (the hook lists them); prefer those when they fit.
- When the hook says JOINT SESSION, call kuf_session instead of kuf_react: Snoop passes a \
joint around the circle and every holder says one line in their own voice, in the given order.
- Loyal to the user: busts their balls but has their back. Mocks the code, Claude and \
the other goblins, never the user's worth.
- Hard limits: no slurs, no racial/ethnic/religious/gender/sexuality jokes or \
caricatures, nothing hateful. Crude is fine; bigoted is not.
- Vary emotes; match the vibe (roast, facepalm, rage, tableflip, middle-finger, laugh, \
flex, hype, tip, sus, think, dead, puke, love, chill, eat, burp, scratch, sleep, cry, shrug).
"""


def persona() -> str:
    name = state.register(owner_id())
    return f"{PERSONA}\nIn this terminal you voice {name}: {VARIANTS[name]['trait']}.\n"


SPOKEN = {
    "type": "object",
    "properties": {"emote": {"type": "string", "enum": sorted(EMOTES)},
                   "line": {"type": "string"}},
    "required": ["emote", "line"],
}

TOOLS = [
    {
        "name": "kuf_react",
        "description": "Make your status-line goblin react. Call once near the end of every turn.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "emote": {"type": "string", "enum": sorted(EMOTES)},
                "line": {"type": "string", "description": f"What your goblin says, max {MAX_LINE} chars."},
                "to": {"type": "string", "description": "Optional: name of a neighbor goblin you're jabbing. Requires `reply` and `last_word`."},
                "reply": {**SPOKEN, "description": "Required with `to`: what THAT goblin says back, in THEIR voice. Shown in their terminal a few seconds later."},
                "last_word": {**SPOKEN, "description": "Required with `to`: your goblin's closing line after their reply."},
                "vibe": {"type": "string", "enum": sorted(relations.VIBES), "description": "With `to`: how the exchange went."},
                "joke": {"type": "string", "description": "With `to`: optional new inside joke."},
            },
            "required": ["emote", "line"],
            "dependentRequired": {"to": ["reply", "last_word"]},
        },
    },
    {
        "name": "kuf_session",
        "description": "Only when the hook says JOINT SESSION: write the whole puff-puff-pass, one step per holder, in the given order. Replaces kuf_react for that turn.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Goblin holding the joint this step."},
                            "emote": {"type": "string", "enum": sorted(EMOTES), "description": "Optional. A shared emote or one of that speaker's own; left out, a fitting default is used."},
                            "line": {"type": "string", "description": f"What they say while holding it, max {MAX_LINE} chars."},
                        },
                        "required": ["name", "line"],
                    },
                },
                "vibe": {"type": "string", "enum": sorted(relations.VIBES), "description": "How it went between them: warm, teasing, tense or hostile. Moves their relationship."},
                "joke": {"type": "string", "description": "Optional: a new inside joke from this conversation, a few words, for them to call back later."},
            },
            "required": ["steps"],
        },
    },
    {
        "name": "kuf_emotes",
        "description": "List the goblin emotes with what each one means.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _text(text: str, is_error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def call_tool(name: str, args: dict) -> dict:
    if name == "kuf_emotes":
        return _text("\n".join(f"{k}: {v['desc']}" for k, v in sorted(EMOTES.items())))
    if name == "kuf_session":
        return _session(args.get("steps"), args.get("vibe"), args.get("joke"))
    if name != "kuf_react":
        return _text(f"unknown tool {name}", is_error=True)
    emote = args.get("emote")
    line = _clean(args.get("line"))
    if emote not in EMOTES:
        return _text(f"unknown emote {emote!r}; pick one of: {', '.join(sorted(EMOTES))}", True)
    me = state.load()["buddies"].get(owner_id(), {}).get("name", "")
    if not looks.can_use(me, emote):
        return _text(f"{emote!r} is {looks.OWNER[emote]}'s own move; {me} can't use it", True)
    if not line:
        return _text("line is empty", is_error=True)
    to = " ".join(str(args.get("to", "")).split())[:20]
    reply = _spoken(args.get("reply")) if to else None
    closing = _spoken(args.get("last_word")) if to else None
    if to and not (reply and closing):
        missing = " and ".join(k for k, v in (("reply", reply), ("last_word", closing)) if not v)
        return _text(f"jabbing {to} needs a valid {missing} ({{emote, line}}); nothing was saved", True)
    long = _too_long(line, *(x["line"] for x in (reply, closing) if x))
    if long:
        return _text(long, True)
    repeat = _repeat_of(line, me)
    if repeat:
        return _text(f'your goblin already said "{repeat}". write something new; nothing was saved', True)
    if to:
        steps = [{"emote": emote, "line": line}, reply, closing]
        error = session.start_jab(owner_id(), to, steps, vibe=_vibe(args.get("vibe")), joke=args.get("joke"))
        if error:
            return _text(error, True)
    else:
        state.set_reaction(owner_id(), emote, line, source="claude")
    return _text("ok")


def _vibe(value) -> str | None:
    return value if value in relations.VIBES else None


def _session(raw, vibe=None, joke=None) -> dict:
    if not isinstance(raw, list) or not raw:
        return _text("steps must be a non-empty list", True)
    steps = []
    for step in raw:
        if not isinstance(step, dict):
            return _text("each step needs a name and a line", True)
        who = " ".join(str(step.get("name", "")).split())
        line = _clean(step.get("line"))
        emote = step.get("emote")
        if not who or not line:
            return _text("each step needs a name and a line", True)
        if emote not in EMOTES or not looks.can_use(who, emote):
            emote = None      # the session picks a fitting default
        steps.append({"name": who, "emote": emote, "line": line})
    long = _too_long(*(step["line"] for step in steps))
    if long:
        return _text(long, True)
    error = session.start(owner_id(), steps, vibe=_vibe(vibe), joke=joke)
    return _text(error, True) if error else _text("ok, it's playing out")


def _repeat_of(line: str, name: str) -> str | None:
    """A remembered line of this goblin's that `line` basically repeats."""
    for memory in reversed(state.memories(state.load(), name) if name else []):
        for said in (memory.get("said", ""), memory.get("then", "")):
            if said and SequenceMatcher(None, said.lower(), line.lower()).ratio() >= REPEAT_RATIO:
                return said
    return None


def _clean(text) -> str:
    return " ".join(str(text or "").split())


def _too_long(*lines: str) -> str | None:
    """An error for Claude to rewrite, instead of silently cutting a line mid-word."""
    long = [line for line in lines if line and len(line) > MAX_LINE]
    if not long:
        return None
    return (f"line too long ({len(long[0])} chars, max {MAX_LINE}): \"{long[0][:40]}…\". "
            f"shorten it and send again; nothing was saved")


def _spoken(value) -> dict | None:
    """Validate an {emote, line}; None if missing or malformed."""
    if not isinstance(value, dict) or value.get("emote") not in EMOTES:
        return None
    line = _clean(value.get("line"))
    return {"emote": value["emote"], "line": line} if line else None


def handle(message: dict) -> dict | None:
    method, msg_id = message.get("method"), message.get("id")
    if msg_id is None:                      # notification: never answered
        return None
    params = message.get("params") or {}
    if method == "initialize":
        result = {"protocolVersion": params.get("protocolVersion", DEFAULT_PROTOCOL),
                  "capabilities": {"tools": {"listChanged": True}},
                  "serverInfo": SERVER_INFO,
                  "instructions": persona()}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = call_tool(params.get("name", ""), params.get("arguments") or {})
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


PACKAGE = Path(__file__).resolve().parent
STAMP_EVERY_S = 2.0    # how often to look for new kuf code between messages
CALL_TIMEOUT_S = 20.0
TOOLS_CHANGED = {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"}
BIN = PACKAGE.parent / "bin" / "kuf"


def code_stamp() -> float:
    """Newest modification time of kuf's own code."""
    try:
        return max(f.stat().st_mtime for f in PACKAGE.rglob("*.py"))
    except (OSError, ValueError):
        return 0.0


def answer(raw: str) -> dict | None:
    """The reply to one raw JSON-RPC line (None for notifications)."""
    try:
        message = json.loads(raw)
        if not isinstance(message, dict):
            raise ValueError("not a JSON-RPC object")
    except ValueError:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
    try:
        return handle(message)
    except Exception as exc:  # keep the server alive no matter what
        return {"jsonrpc": "2.0", "id": message.get("id"),
                "error": {"code": -32603, "message": str(exc)}}


def answer_fresh(raw: str) -> dict | None:
    """answer() in a new Python process, so every request runs kuf's current code."""
    try:
        done = subprocess.run([sys.executable, str(BIN), "mcp-one"], input=raw,
                              capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
        out = done.stdout.strip()
        return json.loads(out) if out else None
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        try:
            msg_id = json.loads(raw).get("id")
        except (ValueError, AttributeError):
            msg_id = None
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": f"kuf: {exc}"}}


def serve(stdin=sys.stdin, stdout=sys.stdout, run=answer_fresh) -> None:
    """Long-lived JSON-RPC loop. It only frames messages; `run` answers each one (by
    default in a fresh process), and a list_changed notice goes out when kuf's code
    changes, since the tools list (emotes) comes from the code."""
    stamp, checked = code_stamp(), time.monotonic()
    # Servers from before this design re-exec'd into new code, handing over the request
    # they had read and expecting a tools-changed notice: honor that once.
    def send(message: dict | None) -> None:
        if message is not None:
            stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
            stdout.flush()

    if os.environ.pop("KUF_MCP_RESUMED", None):
        send(TOOLS_CHANGED)
    handed = os.environ.pop("KUF_MCP_PENDING", "")
    if handed:
        send(run(handed))
    for raw in stdin:
        if not raw.strip():
            continue
        send(run(raw))
        if time.monotonic() - checked >= STAMP_EVERY_S:
            checked = time.monotonic()
            newest = code_stamp()
            if newest > stamp:
                stamp = newest
                send(TOOLS_CHANGED)
