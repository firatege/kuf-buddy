"""Goblins shooting the shit about the user while they work.

Every GOSSIP_EVERY seconds two live goblins have a short chat. The schedule is a
pure function of the clock, the live goblins and a facts snapshot shared through
state, so every terminal agrees on who says what, and when, without messaging.
"""

import time
import zlib
from pathlib import Path

from . import facts, screen, state

GOSSIP_EVERY = 240
START_OFFSET = 20
LINE_S = 12


def _has(*keys):
    return lambda f: all(k in f for k in keys)


# Each script: (condition on facts, [(speaker 0|1, emote, line template), ...])
SCRIPTS = [
    (lambda f: f.get("battery", 100) < 25 and not f.get("charging"), [
        (0, "sus", "yo {b}, {user}'s battery is at {battery}%. gonna die mid-commit"),
        (1, "shrug", "good. maybe {user} finally goes outside"),
        (0, "dead", "nah, a charger always shows up. tragic"),
    ]),
    (lambda f: f.get("battery", 0) >= 95, [
        (0, "think", "battery at {battery}% and still plugged in. {user} trusts nothing"),
        (1, "love", "trust issues. relatable as fuck"),
    ]),
    (lambda f: f.get("temp", 0) >= 85, [
        (0, "puke", "laptop's at {temp}°C. i could fry an egg on this couch"),
        (1, "roast", "that's not an egg {a}, that's your face melting"),
        (0, "rage", "{user} needs a cooling pad or a priest"),
    ]),
    (lambda f: 0 < f.get("temp", 0) < 60, [
        (0, "sus", "machine's chilling at {temp}°C. suspicious"),
        (1, "laugh", "cause {user} isn't doing shit, that's why"),
    ]),
    (_has("song"), [
        (0, "hype", "{user}'s blasting {song} again"),
        (1, "love", "banger tbh. don't tell {user} i said that"),
        (0, "laugh", "too late, i'm snitching"),
    ]),
    (lambda f: "steam" in f.get("apps", []), [
        (0, "sus", "steam is open. 'just one game' my ass"),
        (1, "facepalm", "{user} said today was a work day. we all heard it"),
    ]),
    (lambda f: "discord" in f.get("apps", []), [
        (0, "think", "discord's open. who's {user} yapping to?"),
        (1, "shrug", "none of our business. ...tell me later tho"),
    ]),
    (lambda f: 1 <= f.get("hour", 12) < 6, [
        (0, "sleep", "it's {hour}:00 and {user} is still up. someone call their mom"),
        (1, "dead", "their mom is asleep, {a}. like normal people"),
    ]),
    (lambda f: 1 <= f.get("hour", 12) < 6, [
        (0, "sleep", "psst {b}. you awake?"),
        (1, "dead", "no. i'm dead. what do you want"),
        (0, "sus", "{user} is still typing. at {hour}:00. should we worry?"),
        (1, "sleep", "we should sleep. that's what we should do. zzz"),
    ]),
    (lambda f: 1 <= f.get("hour", 12) < 6, [
        (0, "sleep", "*snore*"),
        (1, "sleep", "*louder snore*"),
        (0, "rage", "stop snoring {b}, i'm trying to snore here"),
    ]),
    (lambda f: 1 <= f.get("hour", 12) < 6, [
        (0, "think", "what do you think {user} dreams about?"),
        (1, "laugh", "green tests and a laptop under 80°C. pure fantasy"),
        (0, "cry", "that's beautiful. go back to sleep"),
    ]),
    (lambda f: 6 <= f.get("hour", 0) < 10, [
        (0, "sus", "{user} is up before noon?? something's wrong"),
        (1, "eat", "coffee. it's always coffee"),
    ]),
    (lambda f: f.get("weekday") in ("Saturday", "Sunday"), [
        (0, "facepalm", "it's {weekday} and {user} is coding. no life"),
        (1, "dead", "neither do we. we live in a status line"),
    ]),
    (lambda f: "days" in f.get("uptime", ""), [
        (0, "flex", "this machine's been up {uptime}. no reboot. respect"),
        (1, "burp", "like me. never showering, never rebooting"),
    ]),
    (lambda f: f.get("ram", 0) >= 70, [
        (0, "puke", "ram at {ram}%. what the fuck is {user} running"),
        (1, "roast", "a browser. it's always the browser"),
    ]),
    (lambda f: 0 < f.get("ram", 100) < 40, [
        (0, "laugh", "ram only at {ram}%. amateur hour"),
        (1, "tip", "open another browser tab {user}, we believe in you"),
    ]),
    (lambda f: f.get("a_proj") != f.get("b_proj"), [
        (0, "sus", "what's {user} even doing in {b_proj}?"),
        (1, "flex", "real work. unlike whatever mess {a_proj} is"),
        (0, "middle-finger", "{a_proj} is art. you wouldn't get it"),
    ]),
    (_has("last_file"), [
        (0, "think", "{user} touched {last_file} earlier. bold move"),
        (1, "roast", "bold? no tests. that's not bold, that's reckless"),
    ]),
    (lambda f: True, [
        (0, "think", "you think {user} actually knows what they're doing?"),
        (1, "love", "nah. but they're our dumbass"),
        (0, "eat", "true. *passes the chips*"),
    ]),
    (lambda f: True, [
        (0, "dead", "yo {b}, you ever think about deleting yourself?"),
        (1, "cry", "every day. then {user} opens a new terminal and here i am"),
    ]),
]


def _seed(*parts) -> int:
    return zlib.crc32("|".join(map(str, parts)).encode())


def choose_pair(slot: int, owners: list[str], visible: set[str] | None) -> list[str]:
    """Two goblins for this slot, preferring the terminals the user can actually see."""
    on_screen = sorted(o for o in owners if visible and o in visible)
    pool = on_screen if len(on_screen) >= 2 else owners
    first = _seed(slot, "a") % len(pool)
    second = (first + 1 + _seed(slot, "b") % (len(pool) - 1)) % len(pool)
    return [pool[first], pool[second]]


def snapshot(slot: int, s: dict) -> dict:
    """{pair, facts} for this slot, decided once and shared through state so every
    terminal agrees even if the user scrolls mid-conversation."""
    cached = s.get("gossip") or {}
    if cached.get("slot") == slot and cached.get("pair"):
        return cached
    owners = sorted(s["buddies"])
    pair = choose_pair(slot, owners, screen.visible_owners(owners))
    fresh = {"slot": slot, "pair": pair,
             "facts": {**facts.collect(), **_project_facts(s, pair)}}

    def change(current: dict) -> dict:
        existing = current.get("gossip") or {}
        if existing.get("slot") == slot and existing.get("pair"):
            return current
        return {**current, "gossip": fresh}

    return state.update(change)["gossip"]


def _project_facts(s: dict, pair: list[str]) -> dict:
    edited = [e for e in s["events"] if e.get("owner") in pair and e.get("file")]
    extra = {"a_proj": screen.project_of(pair[0]), "b_proj": screen.project_of(pair[1])}
    return {**extra, "last_file": Path(edited[-1]["file"]).name} if edited else extra


def current_line(s: dict, owner: str, user: str, now: float | None = None) -> tuple[str, str] | None:
    """(emote, line) if `owner` is speaking in the gossip right now, else None."""
    now = time.time() if now is None else now
    owners = sorted(s["buddies"])
    if len(owners) < 2 or owner not in owners:
        return None
    slot = int(now // GOSSIP_EVERY)
    index = int((now - slot * GOSSIP_EVERY - START_OFFSET) // LINE_S)
    if index < 0:
        return None

    snap = snapshot(slot, s)
    pair = snap["pair"]
    if owner not in pair or any(p not in s["buddies"] for p in pair):
        return None

    info = snap["facts"]
    eligible = [lines for cond, lines in SCRIPTS if cond(info)]
    script = eligible[_seed(slot, "script") % len(eligible)]
    if index >= len(script):
        return None
    speaker, emote, template = script[index]
    if pair[speaker] != owner:
        return None
    names = {o: b["name"] for o, b in s["buddies"].items()}
    fields = {**info, "user": user, "a": names[pair[0]], "b": names[pair[1]]}
    try:
        return emote, template.format(**fields)
    except (KeyError, IndexError, ValueError):
        return None
