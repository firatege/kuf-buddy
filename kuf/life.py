"""Canned solo lines about what the user is up to right now (song, discord, tabs,
apps). Three idle lines in four come from here when there's something to talk about."""

import zlib

LIFE_ODDS = 4          # 1 in N idle lines ignores the user's life and uses the plain pool

LIFE: dict[str, list[str]] = {
    "song": [
        "{song} again? bro you got one playlist and it's crying for help.",
        "ayy {song}. ok that one slaps, i'll allow it.",
        "turn up {song}, my boy. the couch is vibing.",
        "{user} coding to {song}. that explains the bugs.",
        "*nods head to {song}* ...don't look at me.",
        "who picked {song}? oh right. you, with your questionable taste.",
    ],
    "discord": [
        "{server} open on discord again? bro, you live there now.",
        "what's the gossip on {server} tonight? spill it, {user}.",
        "{user} said 'just checking {server}'. that was an hour ago.",
        "{server} gang better not be talking shit about me.",
        "bro you got {server} open but you ain't talking. lurker energy.",
    ],
    "dm": [
        "talking to {dm} again? tell 'em the goblin says hi.",
        "{dm} in the DMs, huh. i see you, {user}.",
        "what you and {dm} plotting? i'm snitching either way.",
        "{dm} texting you at this hour? sus as hell, my boy.",
    ],
    "youtube": [
        "\"{video}\"? bro that's not work, that's youtube.",
        "{user} watching \"{video}\". the code misses you.",
        "one more video, he said. \"{video}\", he said.",
        "\"{video}\" huh. put it on the big screen, i'm bored.",
        "bro learned more from \"{video}\" than from the docs. real.",
    ],
    "whatsapp": [
        "{unread} unread on whatsapp and you're here with me. loyalty.",
        "bro, {unread} messages. somebody wants you. answer 'em.",
        "{unread} unread? leaving people on read is a lifestyle, huh.",
    ],
    "github": [
        "github tab open. stalking other people's repos again, {user}?",
        "starring repos you'll never read. classic {user}.",
        "bro's on github like it's instagram. respect.",
    ],
    "steam": [
        "steam's open. 'just one game' my ass.",
        "{user} said today was a work day. steam said otherwise.",
        "steam in the background, code in the foreground. we all know who wins.",
        "if you launch a game i want in. i call player two.",
    ],
    "sim companies": [
        "running a fake company in sim companies instead of the real one. iconic.",
        "how's the sim companies empire, ceo? stock's up?",
        "bro's a tycoon in sim companies and broke in real life. relatable.",
    ],
}


def _pick(options: list, seed: str):
    return options[zlib.crc32(seed.encode()) % len(options)]


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


def life_line(facts: dict, seed: str, user: str) -> str | None:
    """A line about the user's life right now, three times in four; None otherwise."""
    options = topics(facts)
    if not options or zlib.crc32(f"{seed}|odds".encode()) % LIFE_ODDS == 0:
        return None
    kind, fields = _pick(options, f"{seed}|topic")
    return _pick(LIFE[kind], f"{seed}|line").format(user=user, **fields)
