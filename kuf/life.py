"""Canned solo lines about what the user is up to right now (song, discord, tabs,
apps). One idle line in ten comes from here when there's something to talk about."""

from .events import chance

LIFE_PCT = 10          # share of idle lines about the user's life; the rest use the plain pool

LIFE: dict[str, list[str]] = {
    "song": [
        "whatever's in your headphones, it's got you typing like a sad poet.",
        "this playlist is giving heartbreak, {user}. who hurt you?",
        "the music says one thing, your commits say another. both kinda sad.",
        "you only play this stuff when you're in your feelings. i noticed.",
        "*nods along* ...ok your taste is questionable but the vibe is real.",
        "music this loud means the bug is winning. i know the signs.",
    ],
    "discord": [
        "you got that 'the boys are online and i'm pretending to work' energy.",
        "somebody on that server is having more fun than you. it shows.",
        "you keep glancing at the server. fomo is a hell of a drug, {user}.",
        "lurking with the gang instead of shipping. i respect the commitment.",
    ],
    "dm": [
        "somebody's got you smiling at your phone. don't lie to the goblin.",
        "that's 'waiting for a reply' energy. i know it well, {user}.",
        "private chats at this hour? something's cooking and it ain't code.",
        "you're half here, half in that DM. pick one, my boy.",
    ],
    "youtube": [
        "that video is not 'research' and we both know it.",
        "you're one autoplay away from a 3 hour rabbit hole. i'll wait.",
        "learning from videos instead of docs again. honestly? smart.",
    ],
    "whatsapp": [
        "people are texting you and you're here with me. loyalty or avoidance?",
        "your phone's got that 'somebody wants something' glow. ignore it. like me.",
        "leaving everybody on read is a lifestyle, huh. respect.",
    ],
    "github": [
        "stalking other people's repos again? comparison is the thief of joy, {user}.",
        "starring projects you'll never read. we all do it.",
    ],
    "steam": [
        "the game launcher is open. the deadline already knows it lost.",
        "that 'just one match' look on your face? i've seen it before.",
        "you're working with one eye on the games. i can tell.",
    ],
    "sim companies": [
        "running a fake empire to feel in control. relatable, honestly.",
        "tycoon in the sim, broke in real life. the dream, {user}.",
    ],
}


def topics(facts: dict) -> list[tuple[str, dict]]:
    """Every (kind, fields) the goblins can talk about given the current facts."""
    found = []
    if facts.get("song"):
        found.append(("song", {"song": facts["song"]}))
    chat = facts.get("discord_chat")
    if chat:
        found.append(("dm", {"dm": chat}) if chat.startswith("@") else ("discord", {"server": chat}))
    if facts.get("youtube"):
        found.append(("youtube", {"video": facts["youtube"]}))
    if facts.get("whatsapp_unread"):
        found.append(("whatsapp", {"unread": facts["whatsapp_unread"]}))
    for site in facts.get("sites", []):
        if site in LIFE and site != "whatsapp":
            found.append((site, {}))
    if "steam" in facts.get("apps", []):
        found.append(("steam", {}))
    return found


def wants_life(seed: str) -> bool:
    """LIFE_PCT% of slots are about the user's life."""
    return chance(seed, "odds", LIFE_PCT)


def candidates(facts: dict, user: str) -> list[tuple[str, str]]:
    """Every (template, filled line) about what the user is up to right now."""
    return [(t, t.format(user=user, **fields)) for kind, fields in topics(facts) for t in LIFE[kind]]


KIND_OF = {t: kind for kind, lines in LIFE.items() for t in lines}
