"""Shared on-disk state. Hooks, the MCP server and the status line all touch it,
so every write goes through a file lock and an atomic rename.

Everything is keyed by *owner* (the Claude Code process, see owner.py), so every
terminal gets its own Küf with his own mood and his own last words.
"""

import fcntl
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from .buddies import VARIANTS, assign, resolve
from .owner import is_alive

MAX_EVENTS = 200
STALE_S = 86_400
MEMORY_LINES = 12      # what each goblin remembers saying, kept across terminals
SEEN_EVERY_S = 10      # how often a status line stamps "still here"
GHOST_S = 60           # no status line for this long = a ghost (process alive, nobody drawing it)
GHOST_PRUNE_S = 600


def state_dir() -> Path:
    return Path(os.environ.get("KUF_HOME", Path.home() / ".claude" / "kuf"))


def state_file() -> Path:
    return state_dir() / "state.json"


def empty_state() -> dict:
    return {"events": [], "reactions": {}, "turns": {}, "buddies": {}, "history": {},
            "idle": {}, "said": {}, "plans": {}, "session": None,
            "force_joint": {}}


def load() -> dict:
    try:
        data = json.loads(state_file().read_text())
    except (OSError, ValueError):
        return empty_state()
    if not isinstance(data, dict):
        return empty_state()
    # Keep keys we don't know: a terminal running newer kuf code may have written them,
    # and an older process dropping them would wipe sessions, plans, memories.
    return {**empty_state(), **data}


@contextmanager
def _locked():
    state_dir().mkdir(parents=True, exist_ok=True)
    with open(state_dir() / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _prune(s: dict, now: float) -> dict:
    """Forget terminals that closed or went quiet for a day. Memories stay."""
    def keep(owner: str, ts: float) -> bool:
        return now - ts < STALE_S and is_alive(owner)

    return {
        **s,
        "events": [e for e in s["events"] if keep(e.get("owner", ""), e["ts"])][-MAX_EVENTS:],
        "reactions": {o: r for o, r in s["reactions"].items() if keep(o, r["ts"])},
        "turns": {o: ts for o, ts in s["turns"].items() if keep(o, ts)},
        "buddies": _unique({o: b for o, b in s["buddies"].items()
                            if is_alive(o) and now - b.get("seen", now) < GHOST_PRUNE_S}),
        "history": {n: h[-MEMORY_LINES:] for n, h in s["history"].items()},   # even goblins we don't know yet
        "idle": {o: i for o, i in s["idle"].items() if is_alive(o)},
        "said": {n: [x for x in said if now - x["ts"] < STALE_S]
                 for n, said in s["said"].items()},
        "plans": {o: p for o, p in s["plans"].items() if is_alive(o) and now - p["ts"] < 3600},
        "session": s["session"] if s["session"] and now - s["session"]["ts"] < 3600 else None,
        "force_joint": {o: f for o, f in s["force_joint"].items() if is_alive(o) and now - f["ts"] < 3600},
    }


def last_seen(buddy: dict) -> float:
    """When its status line was last drawn; registration time until the first draw."""
    return buddy.get("seen") or buddy.get("since", 0.0)


def is_ghost(buddy: dict, now: float | None = None) -> bool:
    """Alive but nobody draws its status line anymore, e.g. the terminal-side process
    of a session that Claude Code moved into its background daemon."""
    return (time.time() if now is None else now) - last_seen(buddy) > GHOST_S


def _unique(buddies: dict) -> dict:
    """Give a newer terminal a free goblin when its name is already taken (ghosts don't count)."""
    result: dict = {}
    live = {o: b for o, b in buddies.items() if not is_ghost(b)}
    for owner, buddy in sorted(live.items(), key=lambda kv: kv[1].get("since", 0)):
        names = {b["name"] for b in result.values()}
        if buddy["name"] in names and len(names) < len(VARIANTS):
            buddy = {**buddy, "name": assign(owner, names)}
        result = {**result, owner: buddy}
    return {**{o: b for o, b in buddies.items() if o not in live}, **result}


def update(change: Callable[[dict], dict]) -> dict:
    """Apply `change` (old state -> new state) under the lock and persist it."""
    with _locked():
        new_state = _prune(change(load()), time.time())
        tmp = state_file().with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(new_state, ensure_ascii=False))
        tmp.replace(state_file())
    return new_state


def add_event(owner: str, event: dict) -> dict:
    stamped = {"ts": time.time(), "owner": owner, **event}
    return update(lambda s: {**s, "events": s["events"] + [stamped]})


def set_reaction(owner: str, emote: str, line: str, source: str, to: str = "",
                 reply: dict | None = None, last_word: dict | None = None) -> dict:
    reaction = {"emote": emote, "line": line, "source": source, "to": to,
                "reply": reply, "last_word": last_word, "ts": time.time()}

    def change(s: dict) -> dict:
        updated = {**s, "reactions": {**s["reactions"], owner: reaction}}
        me = s["buddies"].get(owner, {}).get("name")
        return remember(updated, me, reaction) if source == "claude" and me else updated

    return update(change)


def remember(s: dict, name: str, reaction: dict) -> dict:
    """Both sides of a written exchange go into the speakers' memories."""
    ts = reaction["ts"]
    to = next((v for v in VARIANTS if v.lower() == reaction.get("to", "").lower()),
              reaction.get("to", ""))
    memories = {name: {"ts": ts, "said": reaction["line"], "to": to}}
    if to and reaction.get("reply"):
        memories = {name: {**memories[name], "they_said": reaction["reply"]["line"],
                           "then": (reaction.get("last_word") or {}).get("line", "")},
                    to: {"ts": ts, "heard": reaction["line"], "from": name,
                         "said": reaction["reply"]["line"]}}
    history = dict(s["history"])
    for who, memory in memories.items():
        if who in VARIANTS:
            history[who] = (history.get(who, []) + [memory])[-MEMORY_LINES:]
    return {**s, "history": history}


def memories(s: dict, name: str) -> list[dict]:
    return s["history"].get(name, [])


def anchor_exchange(owner: str, reaction_ts: float) -> dict:
    """Mark when the turn that wrote this reaction finished, so the written reply and
    last word play out after the user has read Claude's answer, not while it's typing."""
    now = time.time()

    def change(s: dict) -> dict:
        reaction = s["reactions"].get(owner)
        if not reaction or reaction["ts"] != reaction_ts:
            return s
        return {**s, "reactions": {**s["reactions"], owner: {**reaction, "anchor": now}}}

    return update(change)


def start_turn(owner: str) -> dict:
    return update(lambda s: {**s, "turns": {**s["turns"], owner: time.time()}})


def view(s: dict, owner: str) -> tuple[list[dict], dict | None, float]:
    """This terminal's (events, last reaction, current turn start)."""
    events = [e for e in s["events"] if e.get("owner") == owner]
    return events, s["reactions"].get(owner), s["turns"].get(owner, 0.0)


def register(owner: str) -> str:
    """Name of this terminal's goblin, picking one the first time we see it: the one in
    $KUF_GOBLIN if set (e.g. `KUF_GOBLIN=snoop claude`), else a free one."""
    known = load()["buddies"].get(owner)
    if known:
        return known["name"]
    wanted = resolve(os.environ.get("KUF_GOBLIN", ""))
    if wanted:
        return claim(owner, wanted)

    def change(s: dict) -> dict:
        if owner in s["buddies"]:
            return s
        taken = {b["name"] for o, b in s["buddies"].items() if is_alive(o) and not is_ghost(b)}
        buddy = {"name": assign(owner, taken), "since": time.time()}
        return {**s, "buddies": {**s["buddies"], owner: buddy}}

    buddy = update(change)["buddies"].get(owner)
    # A process that died meanwhile gets pruned; still answer with a sensible name.
    return buddy["name"] if buddy else assign(owner, set())


def claim(owner: str, name: str) -> str:
    """Make `name` this terminal's goblin. Whoever had him gets a free one."""
    now = time.time()

    def change(s: dict) -> dict:
        mine = s["buddies"].get(owner, {"since": now})
        buddies = {**s["buddies"], owner: {**mine, "name": name, "seen": now}}
        taken = {b["name"] for b in buddies.values()}
        for other, buddy in s["buddies"].items():
            if other != owner and buddy["name"] == name:
                buddies = {**buddies, other: {**buddy, "name": assign(other, taken)}}
                taken = taken | {buddies[other]["name"]}
        idle = {o: i for o, i in s["idle"].items() if buddies.get(o, {}).get("name") == s["buddies"].get(o, {}).get("name")}
        return {**s, "buddies": buddies, "idle": idle}

    buddy = update(change)["buddies"].get(owner)
    return buddy["name"] if buddy else name


def neighbors(s: dict, owner: str) -> dict[str, dict]:
    """Other live terminals' goblins: owner -> {name, reaction}. Ghosts are left out."""
    return {o: {"name": b["name"], "reaction": s["reactions"].get(o)}
            for o, b in s["buddies"].items() if o != owner and not is_ghost(b)}


def mark_seen(owner: str, now: float | None = None) -> bool:
    """Stamp that this terminal's status line is being drawn. True if it wrote."""
    now = time.time() if now is None else now
    buddy = load()["buddies"].get(owner)
    if not buddy or now - buddy.get("seen", 0.0) < SEEN_EVERY_S:
        return False

    def change(s: dict) -> dict:
        current = s["buddies"].get(owner)
        if not current:
            return s
        return {**s, "buddies": {**s["buddies"], owner: {**current, "seen": now}}}

    update(change)
    return True


def adopt(owner: str, ghost: str) -> dict:
    """`owner` takes over `ghost`'s window: from now on it's found through the ghost's pid."""
    def change(s: dict) -> dict:
        me = s["buddies"].get(owner)
        if not me or ghost not in s["buddies"]:
            return s
        rest = {o: b for o, b in s["buddies"].items() if o != ghost}
        return {**s, "buddies": {**rest, owner: {**me, "via": ghost}}}

    return update(change)
