"""Break reminders: after two hours of work with no real pause, the goblin tells the
user to get up, drink water, look at something far away. Once every 45 minutes at most."""

import time

from . import moments, state

GAP_S = 15 * 60        # a pause this long counts as a break and resets the streak
STREAK_S = 2 * 3600    # nonstop work before a reminder
EVERY_S = 45 * 60      # at most one reminder this often
SHOW_S = 30.0          # how long the goblin nags on screen

NAG: dict[str, tuple[str, str]] = {
    "Küf":    ("stretch", "even i got up once today. your turn. water. now."),
    "Pas":    ("pas-sprint", "BREAK TIME!! STAND UP!! HYDRATE!! LET'S GOOO!!"),
    "Leş":    ("les-coffin", "two hours straight. your spine is writing its will. stand up."),
    "Sümük":  ("sumuk-notebook", "two hours, no break. noted. i'm telling your mom."),
    "Kir":    ("kir-lecture", "actually, focus drops after 90 min. take 10. science."),
    "Çamur":  ("camur-clouds", "bro... look out a window. the sky's been waiting for you."),
    "Balgam": ("balgam-fist", "*hack* back in my day we took breaks. get up, kid."),
    "Bit":    ("bit-blinds", "they want you glued to the screen. resist. take a walk."),
    "Leke":   ("leke-faint", "two hours?! darling, you'll wither. water. NOW."),
    "Kabuk":  ("kabuk-calculator", "breaks boost productivity 30%. that's free money. go."),
    "Snoop":  ("snoop-rings", "slow down, boss... stretch, water, breathe. the code ain't goin nowhere."),
}
FALLBACK = ("stretch", "you've been at it for hours. stand up, drink some water.")


def activity(s: dict, owner: str, now: float) -> tuple[dict, bool]:
    """Log one prompt of activity: (new state, whether this is the moment to remind)."""
    act = s.get("activity") or {"start": now, "last": now, "reminded": 0.0}
    start = now if now - act["last"] > GAP_S else act["start"]
    remind = now - start >= STREAK_S and now - act["reminded"] >= EVERY_S
    logged = {**s, "activity": {"start": start, "last": now,
                                "reminded": now if remind else act["reminded"]}}
    return (moments.put(logged, "nag", {"by": owner}, now) if remind else logged), remind


def on_prompt(owner: str, now: float | None = None) -> bool:
    """Log activity; True when this prompt is the moment to remind."""
    now = time.time() if now is None else now
    due = []

    def change(s: dict) -> dict:
        logged, remind = activity(s, owner, now)
        due.append(remind)
        return logged

    state.update(change)
    return due[-1]


def streak(s: dict, now: float) -> float:
    act = s.get("activity")
    return 0.0 if not act or now - act["last"] > GAP_S else now - act["start"]


def view(s: dict, owner: str, name: str, now: float) -> tuple[str, str] | None:
    nag = moments.current(s, "nag", SHOW_S, now)
    if not nag or nag["by"] != owner:
        return None
    return NAG.get(name, FALLBACK)


def note(s: dict, now: float) -> str:
    hours = streak(s, now) / 3600
    return (f"BREAK: the user has been working {hours:.1f} hours without a real pause. This "
            f"turn your goblin line tells them, in your voice, to get up, drink water, stretch.")
