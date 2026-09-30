"""Picking idle lines without repeats.

Each slot's line is decided once and stored, so every status-line refresh in that
slot shows the same thing. A goblin doesn't repeat a line for OWN_COOLDOWN_S, and
nobody says what another goblin said in the last SHARED_COOLDOWN_S. When the pool
runs dry, the line said longest ago wins, so repeats are spread as far apart as possible.
"""

import zlib
from typing import Callable

from . import state
from .events import pick

OWN_COOLDOWN_S = 1800
SHARED_COOLDOWN_S = 300


def key(template: str) -> int:
    """Templates are remembered by hash; keeps the no-repeat memory small."""
    return zlib.crc32(template.encode())


def _last_said(s: dict, name: str, now: float) -> dict:
    """template key -> when it was last said, counting other goblins only while shared-cooling."""
    last: dict = {}
    for who, said in s["said"].items():
        for item in said:
            if who != name and now - item["ts"] >= SHARED_COOLDOWN_S:
                continue
            last[item["t"]] = max(item["ts"], last.get(item["t"], 0.0))
    return last


def choose(candidates: list[tuple[str, str]], last: dict, now: float,
           seed: str) -> tuple[str, str]:
    """(template, text): a fresh one if any, else the one said longest ago."""
    fresh = [c for c in candidates if key(c[0]) not in last or now - last[key(c[0])] >= OWN_COOLDOWN_S]
    if fresh:
        return pick(fresh, seed)
    return min(candidates, key=lambda c: last[key(c[0])])


def line_for_slot(owner: str, name: str, slot: str, now: float,
                  candidates: Callable[[], list[tuple[str, str]]],
                  s: dict | None = None) -> tuple[str, str]:
    """This slot's (template, line), picked once and remembered. `candidates` is only
    called when a new line is needed."""
    current = state.owned(s if s is not None else state.load(), owner, "idle")
    if current and current["slot"] == slot:
        return current.get("t", ""), current["line"]
    pool = candidates()
    if not pool:
        return "", ""

    def change(cur: dict) -> dict:
        existing = state.owned(cur, owner, "idle")
        if existing and existing["slot"] == slot:
            return cur
        template, text = choose(pool, _last_said(cur, name, now), now, slot)
        said = cur["said"].get(name, []) + [{"t": key(template), "ts": now}]
        entry = state.stamped(cur, owner, {"slot": slot, "t": template, "line": text})
        return {**cur, "idle": {**cur["idle"], owner: entry},
                "said": {**cur["said"], name: said}}

    picked = state.update(change)["idle"].get(owner, {})
    return picked.get("t", ""), picked.get("line", "")
