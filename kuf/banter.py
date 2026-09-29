"""Goblins in split terminals talking shit to each other, in lines Claude writes."""

import random
import time

from . import facts, state
from .buddies import VARIANTS
from .config import load as load_config, user_name
from .screen import describe_neighbors

WORDS_PER_S = 2.0      # relaxed reading speed; `kuf config words_per_sec <n>`
NOTICE_S = 2.0         # a beat to spot the new line, often in another terminal
REPLY_DELAY_MIN_S, REPLY_DELAY_MAX_S = 4.0, 14.0
LAST_WORD_DELAY_MAX_S = 28.0
EXCHANGE_S = 60        # how long the finished exchange stays up before both close
ANCHOR_WAIT_S = 120    # give up waiting for the turn to end after this long
CONTEXT_S = 900        # how old a neighbor's line can be and still be mentioned to Claude
SNIPPET = 40
RECALL = 6             # how many of his own past lines Claude is reminded of
LIFE_ODDS = 0.75      # 3 turns in 4 the line is about what the user is up to


def _snippet(line: str) -> str:
    return line if len(line) <= SNIPPET else line[: SNIPPET - 1] + "…"


def _words_per_sec() -> float:
    try:
        return max(0.5, float(load_config().get("words_per_sec", WORDS_PER_S)))
    except (TypeError, ValueError):
        return WORDS_PER_S


def reading_s(line: str) -> float:
    """Roughly how long it takes to read a line: a beat to notice it, then the words."""
    return NOTICE_S + len(line.split()) / _words_per_sec()


def exchange_start(reaction: dict, now: float) -> float | None:
    """When the exchange clock starts: the end of the turn that wrote it.

    Claude calls kuf_react before writing its answer; starting the reply then means
    it plays out while the user is still reading. None = the turn is still running.
    """
    if reaction.get("anchor"):
        return reaction["anchor"]
    if reaction.get("source") != "claude" or now - reaction["ts"] > ANCHOR_WAIT_S:
        return reaction["ts"]
    return None


def reply_delay(reaction: dict) -> float:
    """The reply lands once the jab has had time to be read."""
    return min(max(reading_s(reaction["line"]), REPLY_DELAY_MIN_S), REPLY_DELAY_MAX_S)


def last_word_delay(reaction: dict) -> float:
    reply = reaction.get("reply") or {}
    return min(reply_delay(reaction) + reading_s(reply.get("line", "")), LAST_WORD_DELAY_MAX_S)


def exchange_end(reaction: dict) -> float:
    """Seconds after the start when both sides of the exchange close, together."""
    return last_word_delay(reaction) + EXCHANGE_S


def exchange_over(reaction: dict | None, now: float) -> bool:
    if not reaction or not reaction.get("reply"):
        return False
    start = exchange_start(reaction, now)
    return start is not None and now - start >= exchange_end(reaction)


def _aimed_at(reaction: dict, name: str) -> bool:
    return reaction.get("to", "").lower() == name.lower()


def incoming_reply(s: dict, owner: str, my_name: str, now: float) -> tuple[str, str, str] | None:
    """(emote, line, their owner): a reply another terminal's Claude wrote for us."""
    for other, buddy in state.neighbors(s, owner).items():
        reaction = buddy["reaction"]
        if not reaction or not reaction.get("reply") or not _aimed_at(reaction, my_name):
            continue
        start = exchange_start(reaction, now)
        delay = reply_delay(reaction)
        if start is not None and delay <= now - start < exchange_end(reaction):
            return reaction["reply"]["emote"], reaction["reply"]["line"], other
    return None


def last_word(reaction: dict | None, now: float) -> tuple[str, str] | None:
    """Our closing line after the target had its say, stacked under our jab so the
    whole exchange stays readable."""
    if not reaction or not reaction.get("last_word"):
        return None
    start = exchange_start(reaction, now)
    delay = last_word_delay(reaction)
    if start is not None and delay <= now - start < exchange_end(reaction):
        return reaction["last_word"]["emote"], f'{reaction["line"]}\n{reaction["last_word"]["line"]}'
    return None


def topic_note(life: str, roll: float | None = None) -> str:
    """This turn's topic, drawn here so the 3:1 split holds without Claude keeping count."""
    roll = random.random() if roll is None else roll
    if life and roll < LIFE_ODDS:
        return (f"THIS TURN: talk about what {user_name()} is up to right now, not the task: "
                f"{life}.")
    what = f" (for later: {life})" if life else ""
    return f"THIS TURN: react to the conversation or the code.{what}"


def _ago(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m ago"
    return f"{minutes // 60}h ago" if minutes < 1440 else f"{minutes // 1440}d ago"


def recall(s: dict, name: str, now: float) -> str:
    """His recent lines, so running jokes and grudges carry over between turns."""
    lines = []
    for m in state.memories(s, name)[-RECALL:]:
        when = _ago(now - m["ts"])
        if m.get("heard"):
            lines.append(f'  {when}, {m["from"]} to you: "{m["heard"]}" / you: "{m["said"]}"')
        elif m.get("they_said"):
            lines.append(f'  {when}, you to {m["to"]}: "{m["said"]}" / {m["to"]}: '
                         f'"{m["they_said"]}" / you: "{m.get("then", "")}"')
        else:
            lines.append(f'  {when}, you: "{m["said"]}"')
    if not lines:
        return ""
    return (f"What {name} said lately (remember it: keep running jokes and grudges going, "
            f"call back to them, never repeat a line):\n" + "\n".join(lines))


def context_for_claude(owner: str) -> str:
    """Short note injected each turn: who you voice and who's on screen with you."""
    name = state.register(owner)
    s = state.load()
    me = VARIANTS[name]
    lines = [f"[kuf-buddy] This turn you voice {name} ('{me['meaning']}'): {me['trait']}. "
             f"Talk mostly to the user ({user_name()}). When you jab a neighbor (to=<name>), also "
             f"write their `reply` in THEIR voice AND your `last_word` (both required). Prefer "
             f"neighbors that are on screen.", topic_note(facts.describe(facts.cached(state.state_dir() / "facts.json")))]
    memory = recall(s, name, time.time())
    if memory:
        lines.append(memory)
    others = state.neighbors(s, owner)
    if not others:
        return "\n".join(lines)
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
