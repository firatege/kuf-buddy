"""Goblins in split terminals talking shit to each other."""

import time

from . import state
from .buddies import VARIANTS
from .config import user_name
from .events import LINES, pick
from .retorts import lines_for
from .screen import describe_neighbors

BANTER_S = 45          # how long a neighbor's line is worth answering in the status line
REPLY_DELAY_S = 6      # target shows the written reply this long after the jab
LAST_WORD_DELAY_S = 20 # then the jabber gets the last word
EXCHANGE_S = 40        # how long each of those stays up
CONTEXT_S = 900        # how old a neighbor's line can be and still be mentioned to Claude
SNIPPET = 40
RETORT_ODDS = 3        # answer 1 in N neighbor lines that weren't aimed at us
RETORT_EMOTES = ["sus", "laugh", "middle-finger", "roast", "facepalm", "shrug"]
COMEBACK_EMOTES = ["rage", "middle-finger", "tableflip", "roast"]


def _snippet(line: str) -> str:
    return line if len(line) <= SNIPPET else line[: SNIPPET - 1] + "…"


def _aimed_at(reaction: dict, name: str) -> bool:
    return reaction.get("to", "").lower() == name.lower()


def incoming_reply(s: dict, owner: str, my_name: str, now: float) -> tuple[str, str] | None:
    """A reply some other terminal's Claude wrote for us to say back to them."""
    for buddy in state.neighbors(s, owner).values():
        reaction = buddy["reaction"]
        if not reaction or not reaction.get("reply") or not _aimed_at(reaction, my_name):
            continue
        age = now - reaction["ts"]
        if REPLY_DELAY_S <= age < REPLY_DELAY_S + EXCHANGE_S:
            return reaction["reply"]["emote"], reaction["reply"]["line"]
    return None


def last_word(reaction: dict | None, now: float) -> tuple[str, str] | None:
    """Our own closing line after the target had its say."""
    if not reaction or not reaction.get("last_word"):
        return None
    age = now - reaction["ts"]
    if LAST_WORD_DELAY_S <= age < LAST_WORD_DELAY_S + EXCHANGE_S:
        return reaction["last_word"]["emote"], reaction["last_word"]["line"]
    return None


def fresh_neighbor(s: dict, owner: str, since: float, now: float, my_name: str = "",
                   window: float = BANTER_S) -> tuple[str, dict, dict] | None:
    """Newest neighbor reaction after `since` and within `window`: (owner, buddy, reaction)."""
    best = None
    for other, buddy in state.neighbors(s, owner).items():
        reaction = buddy["reaction"]
        if not reaction or reaction.get("source") == "retort":
            continue
        if reaction.get("reply") and _aimed_at(reaction, my_name):
            continue   # a real, written reply is coming; don't talk over it
        if reaction["ts"] <= since or now - reaction["ts"] > window:
            continue
        if best is None or reaction["ts"] > best[2]["ts"]:
            best = (other, buddy, reaction)
    return best


def should_retort(my_name: str, reaction: dict) -> bool:
    """Always answer a call-out; otherwise only now and then, so they talk to the user more."""
    if _aimed_at(reaction, my_name):
        return True
    return int(reaction["ts"] * 1000) % RETORT_ODDS == 0


def retort(my_name: str, other: str, buddy: dict, reaction: dict, owner: str) -> tuple[str, str]:
    """Canned answer to a neighbor that fits what they talked about; harsher if called out."""
    where = describe_neighbors(owner, [other])[other]
    seed = f"{reaction['ts']}{my_name}"
    called_out = _aimed_at(reaction, my_name)
    kind, emotes = ("comeback", COMEBACK_EMOTES) if called_out else ("retort", RETORT_EMOTES)
    # Mostly answer on-topic; the generic pool keeps some variety.
    pool = lines_for(reaction["line"]) * 2 + LINES[kind]
    line = pick(pool, seed).format(them=buddy["name"], where=where, user=user_name(),
                                   snippet=_snippet(reaction["line"]))
    return pick(emotes, seed), line


def context_for_claude(owner: str) -> str:
    """Short note injected each turn: who you voice and who's on screen with you."""
    name = state.register(owner)
    s = state.load()
    me = VARIANTS[name]
    lines = [f"[kuf-buddy] This turn you voice {name} ('{me['meaning']}'): {me['trait']}. "
             f"Talk mostly to the user ({user_name()}). When you jab a neighbor (to=<name>), also "
             f"write their `reply` in THEIR voice and optionally your `last_word`."]
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
        trait = VARIANTS.get(buddy["name"], VARIANTS["Küf"])["trait"]
        lines.append(f"- {buddy['name']} ({trait}) {labels[other]}{said}")
    return "\n".join(lines)
