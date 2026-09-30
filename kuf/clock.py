"""Time of day, day of week and season: goblins act their hour. Mornings are coffee and
regret, evenings are for smoking, weekends are a party, Mondays nobody talks, winter
is blankets and summer is sweat."""

from datetime import datetime

from . import tr
from .config import turkish

MOOD_PCT = 30          # share of idle lines that come from the moment's pool, when there is one

# pool -> (emote, line template); {user} is filled in
POOLS: dict[str, list[tuple[str, str]]] = {
    "morning": [
        ("tea", "coffee first. talking later. way later."),
        ("tea", "*sips* is it morning? who approved this."),
        ("stretch", "*yawns* {user}, why are we awake. why."),
        ("tea", "don't push anything before the second coffee, {user}."),
        ("scratch", "the sun is up and so are my problems."),
    ],
    "evening": [
        ("smoke", "sun's down. shoulders down. that's the rule."),
        ("chill", "evening, {user}. anything you break now is tomorrow's problem."),
        ("tea", "*puts feet up* the couch clocks in now."),
        ("chill", "golden hour on the couch. nobody deploy."),
        ("smoke", "evening shift: me, the couch, and zero plans."),
    ],
    "weekend": [
        ("hype", "IT'S THE WEEKEND, {user}. why is there a terminal open."),
        ("hype", "weekend couch party. dress code: sweatpants."),
        ("game", "weekend = games. the code can wait till monday."),
        ("hype", "no standup today. just the couch and the vibes."),
    ],
    "monday": [
        ("sus", "monday. don't talk to me."),
        ("facepalm", "it's monday and the tests already know it."),
        ("sus", "monday, {user}. lower your expectations. then lower them again."),
        ("tea", "*stares into coffee* monday wins again."),
    ],
    "winter": [
        ("kuf-burrito", "it's freezing. i'm living in this blanket now."),
        ("tea", "winter's here. hot tea, cold code."),
        ("chill", "too cold to move. perfect excuse. i was never moving anyway."),
    ],
    "summer": [
        ("chill", "summer heat. the couch is sticking to me. or i'm sticking to it."),
        ("eat", "it's hot. we need ice cream. medically."),
        ("chill", "too hot to code. too hot to not code. too hot."),
    ],
    "autumn": [
        ("tea", "leaves falling, commits falling. cozy season."),
        ("chill", "autumn. perfect weather to stay inside and do nothing."),
    ],
    "spring": [
        ("stretch", "spring's here. open a window, {user}. i won't, but you should."),
        ("chill", "birds are singing. the linter is screaming. spring."),
    ],
}

SEASONS = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
           6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}


def is_night(hour: int) -> bool:
    """1 to 6 am: goblins sleep, commits get yelled at."""
    return 1 <= hour < 6


def moment(when: datetime | None = None) -> dict:
    when = when or datetime.now()
    hour = when.hour
    part = ("night" if is_night(hour) else "morning" if hour < 11 else
            "afternoon" if hour < 18 else "evening")
    weekday = when.strftime("%A")
    return {"part": part, "weekday": weekday, "season": SEASONS[when.month],
            "weekend": weekday in ("Saturday", "Sunday"), "monday": weekday == "Monday"}


def pools(m: dict) -> list[str]:
    """Which pools fit this moment, strongest flavor first."""
    found = []
    if m["weekend"]:
        found.append("weekend")
    elif m["monday"] and m["part"] in ("morning", "afternoon"):
        found.append("monday")
    if m["part"] in ("morning", "evening"):
        found.append(m["part"])
    found.append(m["season"])
    return found


def candidates(m: dict, user: str) -> list[tuple[str, str]]:
    """(template, line) for every pooled line that fits right now."""
    table = tr.CLOCK if turkish() else POOLS
    return [(t, t.format(user=user)) for pool in pools(m) for _, t in table[pool]]


EMOTE_OF = {t: e for table in (POOLS, tr.CLOCK) for lines in table.values() for e, t in lines}


def describe(m: dict) -> str:
    """'a Monday morning in winter', for Claude."""
    return f"it's a {m['weekday']} {m['part']} in {m['season']}" + (" (weekend)" if m["weekend"] else "")
