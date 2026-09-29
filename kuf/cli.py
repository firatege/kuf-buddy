"""Entry points: status line, hooks, MCP server, preview and install helpers."""

import json
import os
import shutil
import sys
import time
import zlib
from pathlib import Path

from . import state
from .banter import context_for_claude, fresh_neighbor, retort, should_retort
from .config import set_value, user_name
from .gossip import current_line as gossip_line
from .emotes import EMOTES, IDLE_BY_MOOD
from .events import TEST_CMD, canned, classify, edit_count, mood, pick, turn_fallback
from .owner import owner_id
from .render import compose

REACTION_TTL_S = 150
IDLE_SWAP_S = 600
JUST_SPOKE_S = 20   # his own fresh line beats answering the neighbors
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
BIN = Path(__file__).resolve().parent.parent / "bin" / "kuf"
LEGACY_MARKER = "/pet/kuf.py"


def read_payload() -> dict:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


# ── status line ────────────────────────────────────────────────────────────────

def current_view(s: dict, owner: str, name: str, now: float) -> tuple[str, str, str | None]:
    """Decide (emote, line, mood) to show right now in this terminal."""
    events, reaction, _ = state.view(s, owner)
    feeling, kind, trigger = mood(events, now)
    edits = edit_count(events)
    age = now - reaction["ts"] if reaction else float("inf")

    if trigger and (not reaction or trigger["ts"] > reaction["ts"]):
        emote = pick(IDLE_BY_MOOD[feeling], str(trigger["ts"]))
        return emote, canned(kind, trigger, edits, str(trigger["ts"])), feeling
    if age < JUST_SPOKE_S and reaction["emote"] in EMOTES:
        return reaction["emote"], reaction["line"], None
    chat = gossip_line(s, owner, user_name(), now)
    if chat:
        return (*chat, None)
    hit = fresh_neighbor(s, owner, reaction["ts"] if reaction else 0.0, now)
    if hit and should_retort(name, hit[2]):
        return (*retort(name, hit[0], hit[1], hit[2], owner), None)
    if age < REACTION_TTL_S and reaction["emote"] in EMOTES:
        return reaction["emote"], reaction["line"], None
    # Seed with the goblin's name and stagger the switch so terminals don't chant in sync.
    offset = zlib.crc32(name.encode()) % IDLE_SWAP_S
    slot = f"{int((now + offset) // IDLE_SWAP_S)}:{name}"
    return pick(IDLE_BY_MOOD[feeling], slot), canned(kind, trigger, edits, slot), feeling


def cmd_status() -> None:
    read_payload()   # drain stdin; the owner PID already identifies this terminal
    now = time.time()
    owner = owner_id()
    name = state.register(owner)
    emote, line, feeling = current_view(state.load(), owner, name, now)
    print(compose(emote, line, int(now), feeling, name=name))


# ── hooks ──────────────────────────────────────────────────────────────────────

def hook_post(payload: dict) -> None:
    tool, args = payload.get("tool_name", ""), payload.get("tool_input") or {}
    if tool in EDIT_TOOLS:
        path = args.get("file_path") or args.get("notebook_path")
        if path:
            state.add_event(owner_id(), {"kind": classify(path), "file": path})
    elif tool == "Bash" and TEST_CMD.search(args.get("command", "")):
        state.add_event(owner_id(), {"kind": "win", "cmd": args["command"]})


def hook_fail(payload: dict) -> None:
    if payload.get("tool_name") == "Bash":
        cmd = (payload.get("tool_input") or {}).get("command", "")
        state.add_event(owner_id(), {"kind": "fail", "cmd": cmd})


def hook_prompt(payload: dict) -> None:
    owner = owner_id()
    state.start_turn(owner)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": context_for_claude(owner)}}))


def hook_stop(payload: dict) -> None:
    owner = owner_id()
    events, reaction, turn_start = state.view(state.load(), owner)
    if reaction and reaction["ts"] >= turn_start and reaction.get("source") == "claude":
        return
    turn_events = [e for e in events if e["ts"] >= turn_start]
    picked = turn_fallback(turn_events, edit_count(events))
    if picked:
        state.set_reaction(owner, *picked, source="fallback")


HOOKS = {"post": hook_post, "fail": hook_fail, "prompt": hook_prompt, "stop": hook_stop}


def cmd_hook(name: str) -> None:
    handler = HOOKS.get(name)
    if handler is None:
        print(f"kuf: unknown hook {name!r}", file=sys.stderr)
        return
    try:
        handler(read_payload())
    except Exception as exc:  # a pet must never break Claude Code
        print(f"kuf hook {name} error: {exc}", file=sys.stderr)


# ── preview ────────────────────────────────────────────────────────────────────

def cmd_preview(names: list[str]) -> None:
    targets = sorted(EMOTES) if not names or names == ["--all"] else names
    for name in targets:
        if name not in EMOTES:
            print(f"no emote called {name!r}")
            continue
        for tick in range(len(EMOTES[name]["frames"])):
            print(compose(name, f"[{name}] {EMOTES[name]['desc']}", tick))
        print()


# ── install helpers ────────────────────────────────────────────────────────────

def settings_path() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "settings.json"


def _backup(path: Path) -> Path:
    backup = path.with_name(f"settings.json.bak-kuf-{int(time.time())}")
    shutil.copy2(path, backup)
    return backup


def _without_legacy_hooks(hooks: dict) -> dict:
    cleaned = {}
    for event, entries in hooks.items():
        kept = [e for e in entries
                if not any(LEGACY_MARKER in h.get("command", "") for h in e.get("hooks", []))]
        if kept:
            cleaned[event] = kept
    return cleaned


def cmd_install_statusline() -> None:
    path = settings_path()
    settings = json.loads(path.read_text()) if path.exists() else {}
    old = settings.get("statusLine")
    if path.exists():
        print(f"backup: {_backup(path)}")
    if old and "kuf" not in json.dumps(old):
        print(f"note: replacing your previous status line: {old.get('command')}")
    updated = {**settings,
               "statusLine": {"type": "command", "command": f'python3 "{BIN}" status',
                              "padding": 0, "refreshInterval": 1},
               "hooks": _without_legacy_hooks(settings.get("hooks", {}))}
    path.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n")
    print(f"Küf moved into your status line ({path}). Restart Claude Code.")


def cmd_uninstall_statusline() -> None:
    path = settings_path()
    settings = json.loads(path.read_text())
    if "kuf" not in json.dumps(settings.get("statusLine", {})):
        print("Küf isn't in your status line.")
        return
    print(f"backup: {_backup(path)}")
    path.write_text(json.dumps({k: v for k, v in settings.items() if k != "statusLine"},
                               indent=2, ensure_ascii=False) + "\n")
    print("Küf packed his crumbs and left the status line.")


USAGE = """usage: kuf <command>
  status                 render the status line (reads Claude Code JSON on stdin)
  hook post|fail|prompt|stop
  mcp                    run the MCP server on stdio
  preview [emote|--all]  show emotes in your terminal
  say <emote> <line...>  make your goblin say something right now
  config name <name>     what the goblins call you (default: boss)
  install-statusline     put Küf in ~/.claude/settings.json (backs it up first)
  uninstall-statusline"""


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    command, rest = (args[0], args[1:]) if args else ("", [])
    if command == "status":
        try:
            cmd_status()
        except Exception as exc:
            print(f"Küf fell off the couch ({exc.__class__.__name__}: {exc})")
    elif command == "hook" and rest:
        cmd_hook(rest[0])
    elif command == "mcp":
        from .mcp_server import serve
        serve()
    elif command == "preview":
        cmd_preview(rest)
    elif command == "say" and len(rest) >= 2 and rest[0] in EMOTES:
        state.register(owner_id())
        state.set_reaction(owner_id(), rest[0], " ".join(rest[1:]), source="cli")
    elif command == "config" and len(rest) == 2:
        print(json.dumps(set_value(rest[0], rest[1]), ensure_ascii=False))
    elif command == "install-statusline":
        cmd_install_statusline()
    elif command == "uninstall-statusline":
        cmd_uninstall_statusline()
    else:
        print(USAGE)
        return 0 if command in ("", "help", "-h", "--help") else 1
    return 0
