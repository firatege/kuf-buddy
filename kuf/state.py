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
SAID_CAP = 60          # idle lines remembered per goblin for the no-repeat cooldowns
CMD_CAP = 120          # commands are stored this short in events
PLAN_KEEP_S = 3600     # plans, sessions and rolled joints are dropped after this
LEGACY = ("crowd", "spotlight", "spotlight_last", "nag", "session")   # keys older versions wrote
SEEN_EVERY_S = 10      # how often a status line stamps "still here"
GHOST_S = 60           # no status line for this long = a ghost (process alive, nobody drawing it)
GHOST_PRUNE_S = 600


def state_dir() -> Path:
    return Path(os.environ.get("KUF_HOME", Path.home() / ".claude" / "kuf"))


def state_file() -> Path:
    return state_dir() / "state.json"


def empty_state() -> dict:
    return {"events": [], "reactions": {}, "turns": {}, "buddies": {}, "history": {},
            "idle": {}, "said": {}, "plans": {}, "sessions": {},
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

    kept = {k: v for k, v in s.items() if k not in LEGACY}
    return {
        **kept,
        "events": [_short(e) for e in s["events"] if keep(e.get("owner", ""), e["ts"])][-MAX_EVENTS:],
        "reactions": {o: r for o, r in s["reactions"].items() if keep(o, r["ts"])},
        "turns": {o: ts for o, ts in s["turns"].items() if keep(o, ts)},
        "buddies": _unique({o: b for o, b in s["buddies"].items()
                            if is_alive(o) and now - b.get("seen", now) < GHOST_PRUNE_S}),
        "history": {n: h[-MEMORY_LINES:] for n, h in s["history"].items()},   # even goblins we don't know yet
        "idle": {o: i for o, i in s["idle"].items() if is_alive(o)},
        "said": {n: [x for x in said if now - x["ts"] < STALE_S][-SAID_CAP:]
                 for n, said in s["said"].items()},
        "plans": {o: p for o, p in s["plans"].items() if is_alive(o) and now - p["ts"] < PLAN_KEEP_S},
        "sessions": {o: x for o, x in s["sessions"].items() if now - x["ts"] < PLAN_KEEP_S},
        "force_joint": {o: f for o, f in s["force_joint"].items() if is_alive(o) and now - f["ts"] < PLAN_KEEP_S},
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
        old = load()
        changed = change(old)
        if changed is old:
            return old          # nothing to do: skip the prune and the rewrite
        new_state = _prune(changed, time.time())
        tmp = state_file().with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(new_state, ensure_ascii=False))
        tmp.replace(state_file())
    return new_state


def _short(event: dict) -> dict:
    cmd = event.get("cmd")
    return {**event, "cmd": cmd[:CMD_CAP]} if isinstance(cmd, str) and len(cmd) > CMD_CAP else event


def add_event(owner: str, event: dict) -> dict:
    stamped = {"ts": time.time(), "owner": owner, **_short(event)}
    return update(lambda s: {**s, "events": s["events"] + [stamped]})


def set_reaction(owner: str, emote: str, line: str, source: str) -> dict:
    reaction = {"emote": emote, "line": line, "source": source, "ts": time.time()}

    def change(s: dict) -> dict:
        me = s["buddies"].get(owner, {}).get("name")
        updated = {**s, "reactions": {**s["reactions"], owner: {**reaction, "name": me}}}
        return remember(updated, me, reaction) if source == "claude" and me else updated

    return update(change)


def remember(s: dict, name: str, reaction: dict) -> dict:
    """A line Claude wrote goes into its goblin's memory (conversations: session._remember)."""
    if name not in VARIANTS:
        return s
    memory = {"ts": reaction["ts"], "said": reaction["line"]}
    return {**s, "history": {**s["history"], name: (s["history"].get(name, []) + [memory])[-MEMORY_LINES:]}}


def memories(s: dict, name: str) -> list[dict]:
    return s["history"].get(name, [])


def turn(s: dict, owner: str, now: float) -> dict:
    """Mark the start of this terminal's turn (pure; see start_turn)."""
    return {**s, "turns": {**s["turns"], owner: now}}


def start_turn(owner: str) -> dict:
    return update(lambda s: turn(s, owner, time.time()))


def view(s: dict, owner: str) -> tuple[list[dict], dict | None, float]:
    """This terminal's (events, last reaction, current turn start)."""
    events = [e for e in s["events"] if e.get("owner") == owner]
    return events, owned(s, owner, "reactions"), s["turns"].get(owner, 0.0)


def register(owner: str, s: dict | None = None) -> str:
    """Name of this terminal's goblin, picking one the first time we see it: the one in
    $KUF_GOBLIN if set (e.g. `KUF_GOBLIN=snoop claude`), else a free one."""
    known = (s if s is not None else load())["buddies"].get(owner)
    if known:
        return known["name"]
    wanted = resolve(os.environ.get("KUF_GOBLIN", ""))
    if wanted:
        return claim(owner, wanted)

    def change(s: dict) -> dict:
        if owner in s["buddies"]:
            return s
        taken = live_names(s)
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
        return {**s, "buddies": buddies}   # records stamped with the old name stop counting (owned)

    buddy = update(change)["buddies"].get(owner)
    return buddy["name"] if buddy else name


def owned(s: dict, owner: str, table: str) -> dict | None:
    """`s[table][owner]`, unless it was written for a goblin this terminal no longer has.
    Records are stamped with the goblin's name, so swapping goblins (`goblin rnd`)
    drops the old one's reaction, idle line, plan or rolled joint everywhere at once."""
    record = s.get(table, {}).get(owner)
    if not record:
        return None
    current = s["buddies"].get(owner, {}).get("name")
    return record if record.get("name") in (None, current) else None


def stamped(s: dict, owner: str, record: dict) -> dict:
    """`record`, marked as this terminal's current goblin's (see `owned`)."""
    return {**record, "name": s["buddies"].get(owner, {}).get("name")}


def live_names(s: dict, exclude: str | None = None) -> set[str]:
    """Goblins someone is actually looking at (alive, status line drawn), minus `exclude`'s."""
    return {b["name"] for o, b in s["buddies"].items()
            if o != exclude and is_alive(o) and not is_ghost(b)}


def moved_on(s: dict, owners: set[str], since: float) -> bool:
    """Any of these terminals did something (edit, test run, failure) after `since`."""
    return any(e["ts"] > since and e.get("owner") in owners for e in s["events"])


def neighbors(s: dict, owner: str) -> dict[str, dict]:
    """Other live terminals' goblins: owner -> {name, reaction}. Ghosts are left out."""
    return {o: {"name": b["name"], "reaction": owned(s, o, "reactions")}
            for o, b in s["buddies"].items() if o != owner and not is_ghost(b)}


def mark_seen(owner: str, now: float | None = None, s: dict | None = None) -> bool:
    """Stamp that this terminal's status line is being drawn. True if it wrote."""
    now = time.time() if now is None else now
    buddy = (s if s is not None else load())["buddies"].get(owner)
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
