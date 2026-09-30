"""Entry points: status line, hooks, MCP server, preview and install helpers."""

import json
import os
import shutil
import sys
import time
import zlib
from pathlib import Path
from typing import NamedTuple

from . import breaks, clock, crowd, facts, idle, life, looks, relations, session, spotlight, state
from .banter import context_for_claude
from .config import set_value, user_name
from .emotes import EMOTES, IDLE_BY_MOOD, for_line
from .events import TEST_CMD, candidates, canned, chance, classify, edit_count, mood, pick, turn_fallback
from .owner import owner_id
from .render import compose
from .screen import adopt_window, side_of, visible_owners

REACTION_TTL_S = 150
IDLE_SWAP_S = 60    # a new idle line about every minute
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

class View(NamedTuple):
    emote: str
    line: str
    mood: str | None = None
    toward: str | None = None   # owner of the neighbor he's talking to; None = look ahead
    glow: bool | None = None    # None = glow whenever he's turned toward someone


def current_view(s: dict, owner: str, name: str, now: float) -> View:
    """Decide what to show right now in this terminal."""
    events, reaction, _ = state.view(s, owner)
    feeling, kind, trigger = mood(events, now)
    edits = edit_count(events)
    age = now - reaction["ts"] if reaction else float("inf")

    outburst = (breaks.view(s, owner, name, now) or spotlight.view(s, owner, name, now)
                or crowd.view(s, name, now))
    if outburst:
        return View(*outburst, mood=feeling)
    if trigger and (not reaction or trigger["ts"] > reaction["ts"]):
        emote = pick(IDLE_BY_MOOD[feeling], str(trigger["ts"]))
        return View(emote, canned(kind, trigger, edits, str(trigger["ts"])), feeling)
    joint = session.view(s, owner, now)
    if joint:
        emote, line, facing, glowing = joint
        return View(emote, line, toward=facing, glow=glowing)
    if age < REACTION_TTL_S and reaction["emote"] in EMOTES:
        return View(reaction["emote"], reaction["line"])
    # Seed with the goblin's name and stagger the switch so terminals don't chant in sync.
    offset = zlib.crc32(name.encode()) % IDLE_SWAP_S
    slot = f"{int((now + offset) // IDLE_SWAP_S)}:{name}"
    def pool() -> list[tuple[str, str]]:
        """Built only when a new slot's line gets picked (about once a minute)."""
        user = user_name()
        about_life = life.candidates(facts.cached(state.state_dir() / "facts.json"), user)
        about_now = clock.candidates(clock.moment(), user) if feeling != "sleepy" else []
        if about_life and life.wants_life(slot):
            return about_life
        if about_now and chance(slot, "clock", clock.MOOD_PCT):
            return about_now          # the hour, the day, the season
        return candidates(kind, trigger, edits)

    template, line = idle.line_for_slot(owner, name, slot, now, pool, s)
    return View(idle_emote(template, feeling, slot, name), line, feeling)


def idle_emote(template: str, feeling: str, slot: str, name: str) -> str:
    """The move that goes with an idle line: the clock pool names one, else it's guessed."""
    timed = clock.EMOTE_OF.get(template)
    if timed and looks.can_use(name, timed):
        return timed
    return for_line(template, life.KIND_OF.get(template), feeling, slot, name)


def cmd_status() -> None:
    read_payload()   # drain stdin; the owner PID already identifies this terminal
    now = time.time()
    owner = owner_id()
    s = state.load()
    name = state.register(owner, s)
    if state.mark_seen(owner, now, s):
        adopt_window(owner)
    view = current_view(s, owner, name, now)
    facing = side_of(owner, view.toward) if view.toward else "right"
    other = s["buddies"].get(view.toward, {}).get("name") if view.toward else None
    print(compose(view.emote, view.line, int(now), view.mood, name=name, facing=facing or "right",
                  highlight=view.toward is not None if view.glow is None else view.glow,
                  marker=relations.marker(s, name, other) if other else ""))


# ── hooks ──────────────────────────────────────────────────────────────────────

def hook_post(payload: dict) -> None:
    tool, args = payload.get("tool_name", ""), payload.get("tool_input") or {}
    if tool in EDIT_TOOLS:
        path = args.get("file_path") or args.get("notebook_path")
        if path:
            state.add_event(owner_id(), {"kind": classify(path), "file": path})
    elif tool == "Bash" and TEST_CMD.search(args.get("command", "")):
        state.add_event(owner_id(), {"kind": "win", "cmd": args["command"]})
        crowd.trigger("win", owner_id())
    if tool == "Bash":
        kind = spotlight.classify(args.get("command", ""))
        if kind:
            spotlight.trigger(kind, owner_id())


def hook_fail(payload: dict) -> None:
    if payload.get("tool_name") == "Bash":
        cmd = (payload.get("tool_input") or {}).get("command", "")
        state.add_event(owner_id(), {"kind": "fail", "cmd": cmd})
        if TEST_CMD.search(cmd):
            crowd.trigger("fail", owner_id())


def hook_prompt(payload: dict) -> None:
    owner = owner_id()
    now = time.time()
    context = context_for_claude(owner)
    s = state.load()
    visible = visible_owners(list(s["buddies"]))
    pending = session.pending(s, owner)       # rolled by `kuf joint` but not written yet
    if pending:
        planned = pending
    elif session.busy(s, time.time()):
        planned = None                         # let the one on screen finish first
    else:
        planned = session.plan(s, owner, visible) or session.plan_banter(s, owner, visible)
    due = []

    def change(cur: dict) -> dict:
        """Turn start, this turn's plan and the activity log in one write."""
        logged, remind = breaks.activity(session.with_plan(state.turn(cur, owner, now), owner, planned),
                                         owner, now)
        due.append(remind)
        return logged

    after = state.update(change)
    extra = session.note(planned)
    if due and due[-1]:
        extra = f"{extra}\n{breaks.note(after, now)}".strip()
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": f"{context}\n{extra}" if extra else context}}))


def hook_stop(payload: dict) -> None:
    owner = owner_id()
    s = state.load()
    events, reaction, turn_start = state.view(s, owner)
    if session.written_by(s, owner, turn_start):
        session.anchor(owner)                              # a joint or chat written this turn starts now
        return
    if reaction and reaction["ts"] >= turn_start and reaction.get("source") == "claude":
        return
    turn_events = [e for e in events if e["ts"] >= turn_start]
    picked = turn_fallback(turn_events, edit_count(events))
    if picked:
        state.set_reaction(owner, *picked, source="fallback")


def hook_start(payload: dict) -> None:
    """New terminal: claim a goblin and say hi so he's alive from the first second."""
    if payload.get("source") not in (None, "startup", "resume", "clear"):
        return   # e.g. after /compact he's already here
    owner = owner_id()
    name = state.register(owner)
    line = canned("greet", None, 0, f"{time.time()}{owner}", name=name)
    state.set_reaction(owner, pick(["chill", "scratch", "burp", "eat"], owner), line,
                       source="greet")


HOOKS = {"post": hook_post, "fail": hook_fail, "prompt": hook_prompt, "stop": hook_stop,
         "start": hook_start}


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


def cmd_be(rest: list[str]) -> None:
    """`kuf be snoop`: pick this terminal's goblin. `kuf be`: who you are, who's free.
    `kuf be stats` (so `goblin stats` works): the couch stats."""
    from .buddies import VARIANTS, resolve
    owner = owner_id()
    if rest == ["stats"]:
        cmd_stats()
        return
    if rest in (["rnd"], ["random"]):
        print(f"this terminal is now {state.claim(owner, random_goblin(owner))}.")
        return
    if not rest:
        s = state.load()
        mine = s["buddies"].get(owner, {}).get("name", "nobody yet")
        taken = state.live_names(s, exclude=owner)
        print(f"this terminal: {mine}")
        print("free: " + ", ".join(n for n in VARIANTS if n not in taken and n != mine))
        print("taken: " + (", ".join(sorted(taken)) or "-"))
        return
    wanted = resolve(" ".join(rest))
    if not wanted:
        print(f"no goblin called {' '.join(rest)!r}. pick one of: {', '.join(VARIANTS)}")
        return
    print(f"this terminal is now {state.claim(owner, wanted)}.")


def random_goblin(owner: str) -> str:
    """Anyone but the one this terminal has now; free goblins first."""
    import random
    from .buddies import VARIANTS
    s = state.load()
    mine = s["buddies"].get(owner, {}).get("name")
    taken = state.live_names(s, exclude=owner)
    others = [n for n in VARIANTS if n != mine]
    free = [n for n in others if n not in taken]
    return random.choice(free or others)


def cmd_stats() -> None:
    from . import stats
    print(stats.show(state.load()["buddies"].get(owner_id(), {}).get("name", "")))


def cmd_joint(rest: list[str]) -> None:
    """`kuf joint [goblin]`: roll it now; Claude sees the output and writes it right away."""
    from .buddies import resolve
    owner = owner_id()
    me = state.register(owner)
    if me not in session.HOSTS:
        print(f"only {', '.join(session.HOSTS)} roll one. this terminal is {me} (goblin snoop to switch).")
        return
    target = resolve(" ".join(rest)) if rest else None
    if rest and not target:
        print(f"no goblin called {' '.join(rest)!r}.")
        return
    session.force(owner, target)
    s = state.load()
    planned = session.plan(s, owner, visible_owners(list(s["buddies"])))
    if not planned:
        print(f"rolled. nobody around yet; {me} passes it on your next message.")
        return
    session.save_plan(owner, {**planned, "forced": True})
    who = planned.get("target") or ", ".join(n for n in dict.fromkeys(planned["order"]) if n != me)
    how = " (says no)" if planned["kind"] == "refused" else ""
    print(f"🌿 rolled: {me} → {who}{how} · {' › '.join(planned['order'])}")
    dice = session.dice_line(planned)
    if dice:
        print(dice)


USAGE = """usage: kuf <command>
  status                 render the status line (reads Claude Code JSON on stdin)
  hook start|post|fail|prompt|stop
  mcp                    run the MCP server on stdio
  preview [emote|--all]  show emotes in your terminal
  say <emote> <line...>  make your goblin say something right now
  be [goblin]            pick this terminal's goblin (no name: list who's free, rnd: random)
                         start with one: KUF_GOBLIN=snoop claude
  joint [goblin]         Snoop passes one on your next message
  stats                  who smoked what, who talks to whom (also: goblin stats)
  config name <name>     what the goblins call you (default: boss)
  config words_per_sec <n>  reading speed that paces written exchanges (default: 2)
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
    elif command == "mcp-one":             # one JSON-RPC request on stdin, its reply on stdout
        from .mcp_server import answer
        reply = answer(sys.stdin.read())
        if reply is not None:
            print(json.dumps(reply, ensure_ascii=False))
    elif command == "preview":
        cmd_preview(rest)
    elif command == "say" and len(rest) >= 2 and rest[0] in EMOTES:
        state.register(owner_id())
        state.set_reaction(owner_id(), rest[0], " ".join(rest[1:]), source="cli")
    elif command == "be":
        cmd_be(rest)
    elif command == "joint":
        cmd_joint(rest)
    elif command == "stats":
        cmd_stats()
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
