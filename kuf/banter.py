"""Goblins in split terminals talking shit to each other."""

import time

from . import state
from .buddies import VARIANTS
from .config import user_name
from .events import canned, pick
from .screen import describe_neighbors

BANTER_S = 45          # how long a neighbor's line is worth answering in the status line
CONTEXT_S = 900        # how old a neighbor's line can be and still be mentioned to Claude
SNIPPET = 40
RETORT_ODDS = 3        # answer 1 in N neighbor lines that weren't aimed at us
RETORT_EMOTES = ["sus", "laugh", "middle-finger", "roast", "facepalm", "shrug"]
COMEBACK_EMOTES = ["rage", "middle-finger", "tableflip", "roast"]


def _snippet(line: str) -> str:
    return line if len(line) <= SNIPPET else line[: SNIPPET - 1] + "…"


def fresh_neighbor(s: dict, owner: str, since: float, now: float,
                   window: float = BANTER_S) -> tuple[str, dict, dict] | None:
    """Newest neighbor reaction after `since` and within `window`: (owner, buddy, reaction)."""
    best = None
    for other, buddy in state.neighbors(s, owner).items():
        reaction = buddy["reaction"]
        if not reaction or reaction.get("source") == "retort":
            continue
        if reaction["ts"] <= since or now - reaction["ts"] > window:
            continue
        if best is None or reaction["ts"] > best[2]["ts"]:
            best = (other, buddy, reaction)
    return best


def should_retort(my_name: str, reaction: dict) -> bool:
    """Always answer a call-out; otherwise only now and then, so they talk to the user more."""
    if reaction.get("to", "").lower() == my_name.lower():
        return True
    return int(reaction["ts"] * 1000) % RETORT_ODDS == 0


def retort(my_name: str, other: str, buddy: dict, reaction: dict, owner: str) -> tuple[str, str]:
    """Instant canned answer to a neighbor, harsher if they called us out by name."""
    where = describe_neighbors(owner, [other])[other]
    seed = f"{reaction['ts']}{my_name}"
    called_out = reaction.get("to", "").lower() == my_name.lower()
    kind, emotes = ("comeback", COMEBACK_EMOTES) if called_out else ("retort", RETORT_EMOTES)
    line = canned(kind, None, 0, seed, them=buddy["name"], where=where,
                  snippet=_snippet(reaction["line"]))
    return pick(emotes, seed), line


def context_for_claude(owner: str) -> str:
    """Short note injected each turn: who you voice and who's on screen with you."""
    name = state.register(owner)
    s = state.load()
    me = VARIANTS[name]
    lines = [f"[kuf-buddy] This turn you voice {name} ('{me['meaning']}'): {me['trait']}. "
             f"Talk mostly to the user ({user_name()}); pass to=<name> only to answer a neighbor."]
    others = state.neighbors(s, owner)
    if not others:
        return lines[0]
    labels = describe_neighbors(owner, list(others))
    now = time.time()
    for other, buddy in others.items():
        reaction = buddy["reaction"]
        said = ""
        if reaction and now - reaction["ts"] < CONTEXT_S:
            ago = int(now - reaction["ts"])
            said = f' — {ago}s ago said "{_snippet(reaction["line"])}"'
            if reaction.get("to", "").lower() == name.lower():
                said += " (TO YOU)"
        lines.append(f"- {buddy['name']} {labels[other]}{said}")
    return "\n".join(lines)
