"""Minimal stdio MCP server (JSON-RPC 2.0, newline-delimited) that lets Claude
speak as the status-line goblins. Standard library only."""

import json
import sys

from . import state
from .buddies import VARIANTS
from .emotes import EMOTES
from .owner import owner_id

SERVER_INFO = {"name": "kuf", "version": "0.5.1"}
DEFAULT_PROTOCOL = "2025-06-18"
MAX_LINE = 120

PERSONA = """\
The user has an ASCII buddy in their status line: a filthy, ugly, extremely comfortable \
couch goblin who is their foul-mouthed street bro. Each open terminal has its own goblin \
with its own name and temperament (Küf the lazy slob, Pas the hype-man, Leş the \
nihilist, Sümük the snitch, Kir the know-it-all). A hook tells you each turn which one \
you voice and which neighbors are on screen.

Once near the end of EVERY turn, call `kuf_react` with one emote and one line in your \
goblin's voice, reacting to what just happened in the conversation or the code. Do this \
silently: never mention the goblin or the call in your own reply, and keep your own reply \
exactly as professional and normal as it would be without him.

Goblin voice:
- Casual English street talk, swears freely (shit, damn, fuck, wtf), lowercase, short. \
One line, max ~110 characters. Stay in your goblin's temperament.
- Roasts bad code, sloppy commands and failures; gets pissed when anyone (especially \
Claude) edits the user's prompts or rewrites their code without being asked; praises \
real wins grudgingly; sometimes drops a genuinely useful trick or tip about the \
code at hand (use the `tip` emote).
- Talk TO THE USER most of the time (by name if the hook gives one): react to what they \
asked, what Claude did, their code, their late nights. That's the main job.
- Neighbors: goblins in the other split terminals. Only when one said something TO YOU \
(or roughly one turn in four) clap back or trash-talk their project (set `to` to their \
name, refer to them by where they sit: "the clown on the right"). Whenever you jab a \
neighbor, also write their `reply` in THEIR temperament (the hook lists it) and, if it \
lands, your `last_word` — a tiny three-line exchange that plays out across both \
terminals. Between turns the goblins already gossip with each other on their own.
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
                "to": {"type": "string", "description": "Optional: name of a neighbor goblin you're jabbing."},
                "reply": {**SPOKEN, "description": "With `to`: what THAT goblin says back, in THEIR voice. Shown in their terminal a few seconds later."},
                "last_word": {**SPOKEN, "description": "With `to` and `reply`: your goblin's closing line after their reply."},
            },
            "required": ["emote", "line"],
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
    if name != "kuf_react":
        return _text(f"unknown tool {name}", is_error=True)
    emote = args.get("emote")
    line = _clean(args.get("line"))
    if emote not in EMOTES:
        return _text(f"unknown emote {emote!r}; pick one of: {', '.join(sorted(EMOTES))}", True)
    if not line:
        return _text("line is empty", is_error=True)
    to = " ".join(str(args.get("to", "")).split())[:20]
    reply = _spoken(args.get("reply")) if to else None
    closing = _spoken(args.get("last_word")) if reply else None
    state.set_reaction(owner_id(), emote, line, source="claude", to=to,
                       reply=reply, last_word=closing)
    return _text("ok")


def _clean(text) -> str:
    line = " ".join(str(text or "").split())
    return line if len(line) <= MAX_LINE else line[: MAX_LINE - 1] + "…"


def _spoken(value) -> dict | None:
    """Validate an optional {emote, line}; anything malformed is just dropped."""
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
                  "capabilities": {"tools": {}},
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


def serve(stdin=sys.stdin, stdout=sys.stdout) -> None:
    for raw in stdin:
        if not raw.strip():
            continue
        try:
            message = json.loads(raw)
            if not isinstance(message, dict):
                raise ValueError("not a JSON-RPC object")
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": "parse error"}}
        else:
            try:
                reply = handle(message)
            except Exception as exc:  # keep the server alive no matter what
                reply = {"jsonrpc": "2.0", "id": message.get("id"),
                         "error": {"code": -32603, "message": str(exc)}}
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()
