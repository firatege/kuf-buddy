"""Timed moments that take over a goblin's screen for a few seconds (crowd reactions,
spotlights, break nags): fire one with a cooldown, then ask whether it's still on."""

import time
from typing import Callable

from . import state


def fire(name: str, payload: dict, cooldown: float, per: str = "", now: float | None = None,
         also: Callable[[dict], dict] | None = None) -> bool:
    """Start moment `name` unless the same one (`name` + `per`) fired within `cooldown`.
    `also` can change the state in the same write. True if it started."""
    now = time.time() if now is None else now
    started = []

    def change(s: dict) -> dict:
        last = s.get("moment_last", {})
        slot = f"{name}:{per}"
        if now - last.get(slot, 0.0) < cooldown:
            return s
        started.append(True)
        fired = {**s, "moments": {**s.get("moments", {}), name: {**payload, "ts": now}},
                 "moment_last": {**last, slot: now}}
        return also(fired) if also else fired

    state.update(change)
    return bool(started)


def put(s: dict, name: str, payload: dict, now: float) -> dict:
    """Start moment `name` inside a change you're already making (no cooldown)."""
    return {**s, "moments": {**s.get("moments", {}), name: {**payload, "ts": now}}}


def current(s: dict, name: str, span: float, now: float) -> dict | None:
    """The payload of moment `name` while it's still on screen."""
    moment = s.get("moments", {}).get(name)
    return moment if moment and 0 <= now - moment["ts"] < span else None
