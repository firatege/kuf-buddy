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

from .buddies import assign
from .owner import is_alive

MAX_EVENTS = 200
STALE_S = 86_400


def state_dir() -> Path:
    return Path(os.environ.get("KUF_HOME", Path.home() / ".claude" / "kuf"))


def state_file() -> Path:
    return state_dir() / "state.json"


def empty_state() -> dict:
    return {"events": [], "reactions": {}, "turns": {}, "buddies": {}}


def load() -> dict:
    try:
        data = json.loads(state_file().read_text())
    except (OSError, ValueError):
        return empty_state()
    if not isinstance(data, dict):
        return empty_state()
    merged = {**empty_state(), **data}
    return {key: merged[key] for key in empty_state()}   # drops old-format keys


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
    """Forget terminals that closed or went quiet for a day."""
    def keep(owner: str, ts: float) -> bool:
        return now - ts < STALE_S and is_alive(owner)

    return {
        "events": [e for e in s["events"] if keep(e.get("owner", ""), e["ts"])][-MAX_EVENTS:],
        "reactions": {o: r for o, r in s["reactions"].items() if keep(o, r["ts"])},
        "turns": {o: ts for o, ts in s["turns"].items() if keep(o, ts)},
        "buddies": {o: b for o, b in s["buddies"].items() if is_alive(o)},
    }


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


def set_reaction(owner: str, emote: str, line: str, source: str, to: str = "") -> dict:
    reaction = {"emote": emote, "line": line, "source": source, "to": to, "ts": time.time()}
    return update(lambda s: {**s, "reactions": {**s["reactions"], owner: reaction}})


def start_turn(owner: str) -> dict:
    return update(lambda s: {**s, "turns": {**s["turns"], owner: time.time()}})


def view(s: dict, owner: str) -> tuple[list[dict], dict | None, float]:
    """This terminal's (events, last reaction, current turn start)."""
    events = [e for e in s["events"] if e.get("owner") == owner]
    return events, s["reactions"].get(owner), s["turns"].get(owner, 0.0)


def register(owner: str) -> str:
    """Name of this terminal's goblin, picking a free one the first time we see it."""
    known = load()["buddies"].get(owner)
    if known:
        return known["name"]

    def change(s: dict) -> dict:
        if owner in s["buddies"]:
            return s
        taken = {b["name"] for o, b in s["buddies"].items() if is_alive(o)}
        buddy = {"name": assign(owner, taken), "since": time.time()}
        return {**s, "buddies": {**s["buddies"], owner: buddy}}

    return update(change)["buddies"][owner]["name"]


def neighbors(s: dict, owner: str) -> dict[str, dict]:
    """Other live terminals' goblins: owner -> {name, reaction}."""
    return {o: {"name": b["name"], "reaction": s["reactions"].get(o)}
            for o, b in s["buddies"].items() if o != owner}
