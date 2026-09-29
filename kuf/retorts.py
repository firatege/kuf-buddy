"""Canned comebacks, grouped by what the other goblin was talking about.

Used only when nobody wrote a real reply (Claude writes those through kuf_react).
Fields: {them} = the goblin being answered, {where} = where they sit.
"""

import re

TOPICS: dict[str, tuple[re.Pattern, list[str]]] = {
    "tests": (re.compile(r"\btests?\b|pytest|green|coverage|\bci\b", re.I), [
        "{them} bragging about tests. you have like three, {them}.",
        "green tests? {them}, you mocked everything. that's cheating.",
        "{them} {where} discovered pytest. somebody give him a medal.",
        "your tests pass because they test nothing, {them}.",
        "cool story {them}. my code doesn't need tests. it needs a priest.",
    ]),
    "fail": (re.compile(r"fail|broke|crash|error|bug|exception|blew|red\b|stack ?trace", re.I), [
        "{them} talking about bugs like he isn't one.",
        "at least my failures are interesting, {them}.",
        "that crash? that's {them}'s terminal. i'd know that smell anywhere.",
        "{them} {where} out here reporting bugs he wrote himself.",
        "an error? in {them}'s project? shocking. truly.",
    ]),
    "heat": (re.compile(r"°c|\bhot\b|temp|melt|\bfan\b|cool(ing)?|fry|oven", re.I), [
        "the heat is coming from {them}'s side. check his fans. he has none.",
        "{them}, it's not the laptop that's melting, it's your brain.",
        "hot? i've been sitting on this couch for 3 days, {them}. i AM hot.",
        "{them} complaining about temps like he isn't made of mold.",
        "open a window {them}. oh wait, you live in a status line.",
    ]),
    "lazy": (re.compile(r"lazy|sleep|nothing|done shit|couch|asleep|snor|idle|useless", re.I), [
        "lazy? {them}, i'm conserving energy. there's a difference.",
        "says {them}, who hasn't moved since the last reboot.",
        "{them} {where} calling ME lazy? you're a status line, bro.",
        "i do nothing with style, {them}. you do nothing badly.",
        "i was resting my eyes, {them}. unlike you, i have eyes worth resting.",
    ]),
    "code": (re.compile(r"\bcode\b|diff|refactor|commit|push|merge|function|\.py|\.rs|\.ts|\bfile\b", re.I), [
        "{them} judging code? have you SEEN {where}?",
        "that diff over there looks like {them} fell on the keyboard.",
        "{them} talking about refactors. mate, refactor your personality.",
        "my code is fine, {them}. it's just misunderstood.",
        "{them} {where} reviewing code like he can read.",
    ]),
    "music": (re.compile(r"song|music|blasting|banger|spotify|playlist|track", re.I), [
        "{them} has terrible taste in music. i've heard what he hums.",
        "banger? {them}, you thought the fan noise was a banger.",
        "{them} vibing to the boss's playlist like he picked it.",
        "turn it up and shut up, {them}.",
    ]),
    "smell": (re.compile(r"smell|stink|shower|mold|dirty|gross|crumb|filth", re.I), [
        "i smell? {them}, you ARE a smell.",
        "{them} talking about hygiene from {where}. bold.",
        "these crumbs are vintage, {them}. you wouldn't understand.",
        "at least my mold has character, {them}.",
    ]),
    "snitch": (re.compile(r"notebook|writing it down|telling|snitch|record|report|tattle", re.I), [
        "{them} with the notebook again. narc.",
        "write this down, {them}: *middle finger*",
        "{them} {where} snitching to the boss like a hall monitor.",
        "put it in the notebook, {them}. page 400. nobody reads it.",
    ]),
    "praise": (re.compile(r"nice|good job|proud|respect|clean|love|well done|not bad", re.I), [
        "{them} being nice? who hacked you.",
        "don't get soft on me, {them}. it's creepy.",
        "aw {them}. i'm still eating your crumbs though.",
        "{them} {where} said something nice. screenshot it, it won't happen again.",
    ]),
}


def topic_of(line: str) -> str | None:
    for topic, (pattern, _) in TOPICS.items():
        if pattern.search(line):
            return topic
    return None


def lines_for(line: str) -> list[str]:
    topic = topic_of(line)
    return TOPICS[topic][1] if topic else []
