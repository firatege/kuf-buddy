"""Snoop's joint sessions: puff, puff, pass.

On some of Snoop's turns the hook plans a session: he offers the joint to a goblin
on screen, and that goblin's personality decides whether he takes it (looks/*.py,
ACCEPTS_JOINT). A refusal is a normal written exchange. An accepted joint goes around
the circle for a few rounds; Claude writes every step in each goblin's own voice
(kuf_session), and the steps play one after another across the terminals, each in
the holder's screen with the joint animation. Everyone closes together at the end,
and it ends early the moment anyone in the circle moves on.
"""

import random
import time

from . import looks, relations, state, stats
from .banter import NOTICE_S, numbered, reading_s

HOSTS = {"Snoop": 0.15, "Çamur": 0.05, "Küf": 0.03}   # who rolls one, and on what share of turns
BANTER_ODDS = 0.30     # share of turns where two goblins on screen trade a few lines
BANTER_STEPS = 4
CALLED_OUT_S = 300     # a neighbor who spoke to you this recently always gets an answer
HOST = "Snoop"         # the main stoner; the others roll one now and then
MAX_GUESTS = 3
ROUNDS = (2, 3)
MAX_STEPS = 9
PLAN_TTL_S = 900       # a plan Claude never acted on goes stale
STEP_MIN_S = 5.0
LINGER_S = 25.0        # the last step stays up this long before everyone closes
ANCHOR_WAIT_S = 120
WAITING = "*eyes on the joint*"
WAITING_FOR = {"banter": "*listening*"}   # what someone waiting his turn shows, per kind
STACK = 3              # how many of his own lines stay stacked in his bubble
ROLL_S = 8.0           # Snoop rolls it first while the others watch; then it's lit and they talk
INTERRUPT_S = 20.0     # a participant's own new line takes over his screen this long
SMOKING = ("joint", "smoke", "snoop-bong", "snoop-rings", "snoop-roll")   # what the roller does when turned down
ROLLING = "*rolling one up*"


# ── planning (prompt hook) ─────────────────────────────────────────────────────

def plan(s: dict, owner: str, visible: set[str] | None, rng: random.Random | None = None,
         now: float | None = None) -> dict | None:
    """Maybe plan a session for this turn. None = no joint this time."""
    rng = rng or random.Random()
    now = time.time() if now is None else now
    me = s["buddies"].get(owner, {}).get("name")
    forced = s["force_joint"].get(owner)
    if me not in HOSTS or (not forced and rng.random() >= HOSTS[me]):
        return None
    neighbors = state.neighbors(s, owner)
    around = sorted(o for o in neighbors if visible is None or o in visible)
    if forced and not around:
        around = sorted(neighbors)          # asked for one: anyone who's open will do
    wanted = [o for o, b in neighbors.items() if forced and b["name"] == forced.get("target")]
    if not around and not wanted:
        return None
    target = wanted[0] if wanted else rng.choice(around)
    target_name = neighbors[target]["name"]
    rolls: dict[str, dict] = {}

    def takes_it(name: str) -> bool:
        """Roll the dice: his character's odds, nudged by how he gets along with Snoop."""
        chance = relations.joint_odds(s, me, name, looks.accepts_joint(name))
        roll = rng.random()
        rolls[name] = {"roll": round(roll * 100), "needs": round(chance * 100), "yes": roll < chance}
        return roll < chance

    if not takes_it(target_name):
        return {"kind": "refused", "host": owner, "target": target_name,
                "why": looks.refusal(target_name), "ts": now, "dice": rolls,
                "host_name": me, "order": [me, target_name, me, target_name, me]}
    guests = [target_name] + [neighbors[o]["name"] for o in around
                              if o != target and takes_it(neighbors[o]["name"])]
    circle = [me] + guests[:MAX_GUESTS]
    order = (circle * rng.choice(ROUNDS))[:MAX_STEPS]
    return {"kind": "session", "host": owner, "host_name": me, "order": order, "ts": now, "dice": rolls}


def plan_banter(s: dict, owner: str, visible: set[str] | None, rng: random.Random | None = None,
                now: float | None = None) -> dict | None:
    """Maybe plan a 4-line exchange with a goblin on screen. Either side may open it."""
    rng = rng or random.Random()
    now = time.time() if now is None else now
    me = s["buddies"].get(owner, {}).get("name")
    neighbors = state.neighbors(s, owner)
    around = sorted(o for o in neighbors if visible is None or o in visible)
    if not me or not around:
        return None
    callers = [o for o in around if (r := neighbors[o]["reaction"]) and now - r["ts"] < CALLED_OUT_S
               and r.get("to", "").lower() == me.lower()]
    if not callers and rng.random() >= BANTER_ODDS:
        return None
    other = callers[0] if callers else rng.choice(around)
    them = neighbors[other]["name"]
    first, second = (me, them) if callers or rng.random() < 0.5 else (them, me)
    order = [first, second] * (BANTER_STEPS // 2)
    return {"kind": "banter", "host": owner, "with": them, "opener": first, "order": order, "ts": now}


def dice_line(planned: dict) -> str:
    """'🎲 Kir 34 (needs ≤30) → no · Çamur 12 (needs ≤95) → takes it'"""
    parts = [f"{name} {d['roll']} (needs ≤{d['needs']}) → {'takes it' if d['yes'] else 'no'}"
             for name, d in planned.get("dice", {}).items()]
    return "🎲 " + " · ".join(parts) if parts else ""


def pending(s: dict, owner: str, now: float | None = None) -> dict | None:
    """A joint rolled earlier by `kuf joint` that nobody has written yet."""
    now = time.time() if now is None else now
    planned = s["plans"].get(owner)
    fresh = planned and planned.get("forced") and now - planned["ts"] < PLAN_TTL_S
    return planned if fresh else None


def busy(s: dict, now: float) -> bool:
    """A written session hasn't finished playing (or hasn't started yet)."""
    session = s.get("session")
    if not session or _cut(s, session):
        return False
    start_at = _start(session, now)
    if start_at is None:
        return True
    total = intro_s(session) + sum(durations(session["steps"])) + LINGER_S
    return now - start_at < total


def force(owner: str, target: str | None = None) -> None:
    """`kuf joint [goblin]`: Snoop passes one on the next turn, no dice roll."""
    state.update(lambda s: {**s, "force_joint": {**s["force_joint"],
                                                 owner: {"target": target, "ts": time.time()}}})


def save_plan(owner: str, planned: dict | None) -> None:
    def change(s: dict) -> dict:
        plans = {o: p for o, p in s["plans"].items() if o != owner}
        forced = {o: f for o, f in s["force_joint"].items() if o != owner or not planned}
        return {**s, "plans": {**plans, owner: planned} if planned else plans, "force_joint": forced}

    state.update(change)


def note(planned: dict | None) -> str:
    """What Claude is told to do with the plan this turn."""
    if not planned:
        return ""
    if planned["kind"] == "banter":
        other = planned["with"]
        who = "you open" if planned["opener"] != other else f"{other} opens, talking to you"
        return (f"BANTER instead of kuf_react this turn: a {len(planned['order'])}-line exchange with "
                f"{other} ({who}). Call kuf_session with exactly {len(planned['order'])} steps, speakers "
                f"in this order: {' -> '.join(planned['order'])}. Each line in the speaker's own "
                f"voice (the hook lists {other}'s temperament), answering the line before: trash talk "
                f"each other, their project, their couch habits, what the user just did. Lowercase, "
                f"short, one line each.")
    if planned["kind"] == "refused":
        why = f" ({planned['why']})" if planned["why"] else ""
        target = planned["target"]
        host = planned.get("host_name", HOST)
        return (f"JOINT, REFUSED, instead of kuf_react this turn: {host} rolls one and offers it to "
                f"{target}, who won't touch it{why}. Its own kind of conversation: {host} smokes it "
                f"himself the whole time (more for him), {target} keeps refusing in their own voice. "
                f"Call kuf_session with exactly {len(planned['order'])} steps, speakers in this order: "
                f"{' -> '.join(planned['order'])}. {host} offers, {target} says no, {host} takes a hit "
                f"and pushes, {target} refuses harder, {host} blows smoke and has the last word. For "
                f"{target} use 'nope' or one of their own emotes. Lowercase, short.")
    circle = ", ".join(dict.fromkeys(planned["order"]))
    return (f"JOINT SESSION instead of kuf_react this turn: {planned.get('host_name', HOST)} sparks one up and passes it "
            f"around ({circle}). Call kuf_session with exactly {len(planned['order'])} steps, "
            f"speakers in this order: {' -> '.join(planned['order'])}. Each step is the holder "
            f"taking a hit and saying one line in their own voice, answering the one before, "
            f"so it builds into a real stoned conversation. Lowercase, short, no raw facts.")


# ── starting (MCP tool) ────────────────────────────────────────────────────────

DEFAULT_EMOTE = {"session": "joint", "refused": "nope", "banter": "chill"}


def default_emote(kind: str, name: str, host: str = HOST) -> str:
    """What a step shows when Claude didn't pick an emote."""
    return "joint" if kind == "refused" and name == host else DEFAULT_EMOTE[kind]


def _emote_for(kind: str, name: str, picked: str | None, host: str = HOST) -> str:
    """Claude's pick, except: nobody refusing the joint is shown smoking it, and whoever
    rolled it, turned down, smokes it himself every step."""
    if kind == "refused" and name == host:
        return picked if picked in SMOKING else "joint"
    if not picked or (kind == "refused" and picked == "joint"):
        return default_emote(kind, name, host)
    return picked


def start(owner: str, steps: list[dict], now: float | None = None, vibe: str | None = None,
          joke: str | None = None) -> str | None:
    """Store a written session. Returns an error message, or None when it's on."""
    now = time.time() if now is None else now
    s = state.load()
    planned = s["plans"].get(owner)
    if not planned or planned["kind"] not in DEFAULT_EMOTE or now - planned["ts"] > PLAN_TTL_S:
        return "no joint session or banter is planned for this turn; use kuf_react"
    names = [step["name"] for step in steps]
    if [n.lower() for n in names] != [n.lower() for n in planned["order"]]:
        return f"steps must follow this order exactly: {' -> '.join(planned['order'])}"
    owners = {b["name"]: o for o, b in s["buddies"].items()}
    host_name = planned.get("host_name", HOST)
    written = [{"owner": owners.get(canon, ""), "name": canon, "line": step["line"],
                "emote": _emote_for(planned["kind"], canon, step.get("emote"), host_name)}
               for canon, step in zip(planned["order"], steps)]
    if any(not w["owner"] for w in written):
        return "someone in the circle left; nothing was saved"
    session = {"host": owner, "host_name": host_name, "kind": planned["kind"], "steps": written, "ts": now}

    def change(cur: dict) -> dict:
        plans = {o: p for o, p in cur["plans"].items() if o != owner}
        # The host's own reaction is his first line in it, never someone else's.
        me = cur["buddies"].get(owner, {}).get("name")
        first = next((w for w in written if w["name"] == me), written[0])
        reaction = {"emote": first["emote"] if first["name"] == me else "chill",
                    "line": first["line"] if first["name"] == me else WAITING_FOR.get(planned["kind"], WAITING),
                    "source": "claude", "to": "", "reply": None, "last_word": None, "ts": now}
        started = {**cur, "plans": plans, "session": session,
                   "reactions": {**cur["reactions"], owner: reaction}}
        remembered = _remember(started, written, now, planned["kind"])
        related = relations.record(remembered, planned["order"], planned["kind"], vibe, joke,
                                   host=host_name, now=now)
        return stats.after_session(related, planned["kind"], planned["order"], host_name)

    state.update(change)
    return None


def _remember(s: dict, steps: list[dict], now: float, kind: str = "session") -> dict:
    history = dict(s["history"])
    circle = list(dict.fromkeys(w["name"] for w in steps))
    for name in circle:
        mine = [w["line"] for w in steps if w["name"] == name]
        memory = {"ts": now, "said": mine[-1], "session": [f'{w["name"]}: {w["line"]}' for w in steps],
                  "with": [n for n in circle if n != name], "kind": kind}
        history[name] = (history.get(name, []) + [memory])[-state.MEMORY_LINES:]
    return {**s, "history": history}


def anchor(owner: str) -> None:
    """The turn that wrote the session ended: start the clock now."""
    def change(s: dict) -> dict:
        session = s.get("session")
        if not session or session["host"] != owner or session.get("anchor"):
            return s
        return {**s, "session": {**session, "anchor": time.time()}}

    state.update(change)


# ── playing (status line) ──────────────────────────────────────────────────────

def durations(steps: list[dict]) -> list[float]:
    return [max(STEP_MIN_S, reading_s(step["line"]) + NOTICE_S) for step in steps]


def _start(session: dict, now: float) -> float | None:
    if session.get("anchor"):
        return session["anchor"]
    return session["ts"] if now - session["ts"] > ANCHOR_WAIT_S else None


def _cut(s: dict, session: dict) -> bool:
    """Anyone in the circle really moved on (edited a file, ran tests, hit an error) since
    it started playing. A plain new line from their own Claude only interrupts them for a
    moment (see `_interrupted`), and what the writing turn itself did doesn't count."""
    circle = {step["owner"] for step in session["steps"]}
    since = session.get("anchor") or session["ts"]
    return any(e["ts"] > since and e.get("owner") in circle for e in s["events"])


def _interrupted(s: dict, session: dict, owner: str, now: float) -> bool:
    """His own Claude just said something: show that for a bit, then back to the circle."""
    mine = s["reactions"].get(owner)
    since = session.get("anchor") or session["ts"]
    # (the host's own reaction stamped when the session was written doesn't count)
    return bool(mine) and mine["ts"] > max(since, session["ts"]) and now - mine["ts"] < INTERRUPT_S


def intro_s(session: dict) -> float:
    """Joints get rolled before anyone talks; plain banter starts right away."""
    return ROLL_S if session.get("kind", "session") in ("session", "refused") else 0.0


def view(s: dict, owner: str, now: float) -> tuple[str, str, str | None, bool] | None:
    """(emote, line, owner he faces, glowing) while this terminal is in a running session."""
    session = s.get("session")
    if not session or owner not in {step["owner"] for step in session["steps"]}:
        return None
    # Swapped goblins mid-session (`goblin rnd`): the new one doesn't inherit the old one's joint.
    mine_now = s["buddies"].get(owner, {}).get("name")
    if mine_now not in {step["name"] for step in session["steps"] if step["owner"] == owner}:
        return None
    start_at = _start(session, now)
    if start_at is None or _cut(s, session) or _interrupted(s, session, owner, now):
        return None
    steps, spans = session["steps"], durations(session["steps"])
    elapsed = now - start_at - intro_s(session)
    if elapsed < -intro_s(session) or elapsed >= sum(spans) + LINGER_S:
        return None
    host = session["host"]
    if elapsed < 0:
        # Rolling it: the host works on the joint, everyone else turns to watch. No glow yet.
        if owner == host:
            others = [st["owner"] for st in steps if st["owner"] != owner]
            rolling = "snoop-roll" if session.get("host_name", HOST) == HOST else "joint"
            return rolling, ROLLING, others[0] if others else None, False
        return "chill", WAITING, host, False
    current, clock = len(steps) - 1, 0.0
    for i, span in enumerate(spans):
        if elapsed < clock + span:
            current = i
            break
        clock += span
    holder = steps[current]
    # His lines so far stack up in one bubble, like a jab and its last word do.
    mine = [numbered(i + 1, step["line"]) for i, step in enumerate(steps[: current + 1])
            if step["owner"] == owner][-STACK:]
    others = [st["owner"] for st in steps[current + 1:] + steps[:current] if st["owner"] != owner]
    if holder["owner"] == owner:
        # Face whoever gets it next (or anyone else in the circle).
        return holder["emote"], "\n".join(mine), others[0] if others else None, True
    waiting = WAITING_FOR.get(session.get("kind", "session"), WAITING)
    return "chill", "\n".join(mine) if mine else waiting, holder["owner"], True

