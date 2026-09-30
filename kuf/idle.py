"""Picking idle lines without repeats.

Each slot's line is decided once and stored, so every status-line refresh in that
slot shows the same thing. A goblin doesn't repeat a line for OWN_COOLDOWN_S, and
nobody says what another goblin said in the last SHARED_COOLDOWN_S. When the pool
runs dry, the line said longest ago wins, so repeats are spread as far apart as possible.
"""

import zlib

from . import state

OWN_COOLDOWN_S = 1800
SHARED_COOLDOWN_S = 300
MAX_SAID = state.SAID_CAP   # remembered (template, when) pairs per goblin


def _last_said(s: dict, name: str, now: float) -> dict[str, float]:
    """template -> when it was last said, counting other goblins only while shared-cooling."""
    last: dict[str, float] = {}
    for who, said in s["said"].items():
        for item in said:
            if who != name and now - item["ts"] >= SHARED_COOLDOWN_S:
                continue
            last = {**last, item["t"]: max(item["ts"], last.get(item["t"], 0.0))}
    return last


def choose(candidates: list[tuple[str, str]], last: dict[str, float], now: float,
           seed: str) -> tuple[str, str]:
    """(template, text): a fresh one if any, else the one said longest ago."""
    fresh = [c for c in candidates if c[0] not in last or now - last[c[0]] >= OWN_COOLDOWN_S]
    if fresh:
        return fresh[zlib.crc32(seed.encode()) % len(fresh)]
    return min(candidates, key=lambda c: last[c[0]])


def line_for_slot(owner: str, name: str, slot: str, now: float,
                  candidates: list[tuple[str, str]]) -> tuple[str, str]:
    """This slot's (template, line), picked once and remembered."""
    current = state.load()["idle"].get(owner)
    if current and current["slot"] == slot:
        return current.get("t", ""), current["line"]
    if not candidates:
        return "", ""

    def change(s: dict) -> dict:
        existing = s["idle"].get(owner)
        if existing and existing["slot"] == slot:
            return s
        template, text = choose(candidates, _last_said(s, name, now), now, slot)
        said = (s["said"].get(name, []) + [{"t": template, "ts": now}])[-MAX_SAID:]
        return {**s, "idle": {**s["idle"], owner: {"slot": slot, "t": template, "line": text}},
                "said": {**s["said"], name: said}}

    picked = state.update(change)["idle"].get(owner, {})
    return picked.get("t", ""), picked.get("line", "")
