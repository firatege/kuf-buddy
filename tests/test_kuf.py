import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

from kuf import cli, events, owner, render, state
from kuf.emotes import EMOTES, IDLE_BY_MOOD
from kuf.mcp_server import serve

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\033\[[0-9;]*m")


@pytest.fixture(autouse=True)
def kuf_home(tmp_path, monkeypatch):
    monkeypatch.setenv("KUF_HOME", str(tmp_path / "kuf"))
    monkeypatch.delenv("NIRI_SOCKET", raising=False)   # never talk to the real compositor
    use_owner(monkeypatch, "term-a")
    return tmp_path


def use_owner(monkeypatch, name):
    monkeypatch.setenv("KUF_OWNER", name)
    owner.owner_id.cache_clear()


# ── emotes & rendering ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("name", sorted(EMOTES))
def test_every_emote_has_equal_height_frames_that_fit_the_sprite_column(name):
    frames = EMOTES[name]["frames"]
    assert len(frames) >= 2
    for frame in frames:
        assert len(frame) == 4
        assert all(render.width(row) <= render.SPRITE_COLS for row in frame), frame


def test_idle_moods_only_reference_real_emotes():
    assert all(e in EMOTES for names in IDLE_BY_MOOD.values() for e in names)


def test_bubble_wraps_and_truncates_long_lines():
    lines = render.bubble("fuck " * 80)
    assert len(lines) == render.BUBBLE_MAX_LINES + 2
    assert lines[-2].rstrip(" │").endswith("…")
    assert len({render.width(line) for line in lines}) == 1   # box edges line up


def test_compose_points_bubble_tail_at_face_and_keeps_rows_aligned():
    out = ANSI.sub("", render.compose("roast", "lmao", 0)).splitlines()
    face_row = next(i for i, row in enumerate(out) if "☞" in row)
    assert "< lmao" in out[face_row]
    assert all(row.startswith(row[: render.SPRITE_COLS]) for row in out)


# ── state ──────────────────────────────────────────────────────────────────────

def test_corrupt_state_file_is_tolerated():
    state.state_dir().mkdir(parents=True)
    state.state_file().write_text("{not json")
    assert state.load() == state.empty_state()


def test_events_are_capped():
    for i in range(state.MAX_EVENTS + 10):
        state.add_event("term-a", {"kind": "code", "file": f"f{i}.py"})
    events_ = state.load()["events"]
    assert len(events_) == state.MAX_EVENTS
    assert events_[-1]["file"] == f"f{state.MAX_EVENTS + 9}.py"


# ── events & mood ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path,kind", [
    ("/p/CLAUDE.md", "prompt"), ("/h/.claude/rules/x.md", "prompt"),
    ("/p/src/main.rs", "code"), ("/p/notes.txt", "stuff"),
])
def test_classify(path, kind):
    assert events.classify(path) == kind


def test_prompt_edit_makes_him_furious():
    now = time.time()
    feeling, kind, _ = events.mood([{"ts": now, "kind": "prompt", "file": "CLAUDE.md"}], now)
    assert (feeling, kind) == ("furious", "prompt")


def test_turn_fallback_prioritises_prompt_edits_then_failures():
    now = time.time()
    turn = [{"ts": now, "kind": "code", "file": "a.py"},
            {"ts": now, "kind": "fail", "cmd": "pytest -q"},
            {"ts": now, "kind": "prompt", "file": "CLAUDE.md"}]
    assert events.turn_fallback(turn, 3)[0] == "rage"
    assert events.turn_fallback(turn[:2], 3)[0] == "roast"
    assert events.turn_fallback([], 0) is None


# ── hooks ──────────────────────────────────────────────────────────────────────

def run_bin(*args, stdin=""):
    return subprocess.run([sys.executable, str(ROOT / "bin" / "kuf"), *args],
                          input=stdin, capture_output=True, text=True, timeout=10)


@pytest.mark.parametrize("hook", ["post", "fail", "prompt", "stop", "nope"])
def test_hooks_exit_zero_on_garbage(hook):
    assert run_bin("hook", hook, stdin="garbage{{").returncode == 0


def test_stop_falls_back_only_when_claude_stayed_quiet():
    cli.hook_prompt({"session_id": "s"})
    cli.hook_post({"session_id": "s", "tool_name": "Edit",
                   "tool_input": {"file_path": "/p/CLAUDE.md"}})
    cli.hook_stop({"session_id": "s"})
    reaction = state.load()["reactions"]["term-a"]
    assert (reaction["source"], reaction["emote"]) == ("fallback", "rage")

    cli.hook_prompt({"session_id": "s"})
    state.set_reaction("term-a", "love", "aww", source="claude")
    cli.hook_post({"session_id": "s", "tool_name": "Edit",
                   "tool_input": {"file_path": "/p/CLAUDE.md"}})
    cli.hook_stop({"session_id": "s"})
    assert state.load()["reactions"]["term-a"]["line"] == "aww"


def test_status_shows_fresh_claude_reaction():
    state.set_reaction("term-a", "tip", "use git bisect you absolute walnut", source="claude")
    out = run_bin("status", stdin=json.dumps({"session_id": "s"}))
    assert "git bisect" in out.stdout and "(•̀ᴗ•́)☝" in out.stdout


def test_each_terminal_has_its_own_kuf(monkeypatch):
    state.set_reaction("term-a", "love", "terminal a is my favourite", source="claude")
    cli.hook_post({"tool_name": "Edit", "tool_input": {"file_path": "/p/CLAUDE.md"}})

    use_owner(monkeypatch, "term-b")
    out = ANSI.sub("", run_bin("status").stdout)
    assert "terminal a" not in out and "CLAUDE.md" not in out

    use_owner(monkeypatch, "term-a")
    events_, reaction, _ = state.view(state.load(), "term-a")
    assert reaction["line"] == "terminal a is my favourite" and len(events_) == 1


def test_dead_terminals_are_forgotten():
    state.set_reaction("999999999", "dead", "bye", source="claude")
    state.set_reaction("term-a", "chill", "hi", source="claude")
    assert set(state.load()["reactions"]) == {"term-a"}


def test_owner_is_found_by_walking_up_to_claude(monkeypatch):
    monkeypatch.delenv("KUF_OWNER")
    monkeypatch.delenv("CLAUDE_PID", raising=False)
    owner.owner_id.cache_clear()
    tree = {100: (50, "python3"), 50: (40, "sh"), 40: (1, "claude")}
    monkeypatch.setattr(owner.os, "getppid", lambda: 100)
    monkeypatch.setattr(owner, "parent_and_name", lambda pid: tree.get(pid))
    assert owner.owner_id() == "40"
    owner.owner_id.cache_clear()


# ── MCP server ─────────────────────────────────────────────────────────────────

def mcp(*messages):
    stdin = io.StringIO("".join(json.dumps(m) + "\n" for m in messages))
    stdout = io.StringIO()
    serve(stdin, stdout)
    return [json.loads(line) for line in stdout.getvalue().splitlines()]


def test_mcp_handshake_lists_tools_and_sends_persona():
    init, tools = mcp(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    )
    assert init["result"]["protocolVersion"] == "2025-06-18"
    assert "kuf_react" in init["result"]["instructions"]
    assert {t["name"] for t in tools["result"]["tools"]} == {"kuf_react", "kuf_emotes"}


def test_mcp_react_saves_reaction_and_rejects_unknown_emote():
    ok, bad = mcp(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
         "params": {"name": "kuf_react", "arguments": {"emote": "roast", "line": "  lol   nice  "}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "kuf_react", "arguments": {"emote": "twerk", "line": "x"}}},
    )
    assert ok["result"]["isError"] is False
    assert state.load()["reactions"]["term-a"]["line"] == "lol nice"
    assert bad["result"]["isError"] is True


def test_mcp_survives_bad_json_and_unknown_methods():
    parse_err, unknown = mcp("nope", {"jsonrpc": "2.0", "id": 9, "method": "foo/bar"})
    assert parse_err["error"]["code"] == -32700
    assert unknown["error"]["code"] == -32601


# ── install ────────────────────────────────────────────────────────────────────

def test_install_statusline_backs_up_and_strips_legacy_hooks(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    legacy = {"type": "command", "command": 'python3 "/home/x/.claude/pet/kuf.py" hook'}
    other = {"type": "command", "command": "node other.js"}
    (tmp_path / "settings.json").write_text(json.dumps({"hooks": {"PostToolUse": [
        {"matcher": "Edit", "hooks": [legacy]}, {"matcher": "Bash", "hooks": [other]}]}}))

    cli.cmd_install_statusline()

    settings = json.loads((tmp_path / "settings.json").read_text())
    assert "bin/kuf" in settings["statusLine"]["command"]
    assert settings["hooks"]["PostToolUse"] == [{"matcher": "Bash", "hooks": [other]}]
    assert list(tmp_path.glob("settings.json.bak-kuf-*"))


# ── the gang: names, neighbors, banter ─────────────────────────────────────────

from kuf import banter, buddies, screen  # noqa: E402


def test_live_terminals_get_different_goblins():
    names = {state.register(f"term-{i}") for i in range(len(buddies.VARIANTS))}
    assert names == set(buddies.VARIANTS)
    assert state.register("term-0") == state.register("term-0")   # stable


def win(ws, col, row):
    return {"workspace_id": ws, "layout": {"pos_in_scrolling_layout": [col, row]}}


@pytest.mark.parametrize("theirs,expected", [
    (win(1, 3, 1), "on the right"), (win(1, 1, 1), "on the left"),
    (win(1, 5, 1), "way off to the right"), (win(1, 2, 1), "right above you"),
    (win(2, 2, 2), "on another workspace"), (None, ""),
])
def test_direction_from_niri_layout(theirs, expected):
    assert screen.direction(win(1, 2, 2), theirs) == expected


def test_neighbor_line_gets_an_instant_retort(monkeypatch):
    monkeypatch.setattr(banter, "describe_neighbors", lambda me, others: {o: "on the right (api)" for o in others})
    monkeypatch.setattr(banter, "RETORT_ODDS", 1)
    monkeypatch.setattr(cli, "gossip_line", lambda *a: None)
    b_name = state.register("term-b")
    a_name = state.register("term-a")
    state.set_reaction("term-b", "flex", "my tests are green, loser", source="claude")

    emote, line, _ = cli.current_view(state.load(), "term-a", a_name, time.time())
    assert b_name in line and emote in banter.RETORT_EMOTES

    state.set_reaction("term-b", "roast", "yo, your code sucks", source="claude", to=a_name)
    emote, line, _ = cli.current_view(state.load(), "term-a", a_name, time.time())
    assert emote in banter.COMEBACK_EMOTES


def test_claude_gets_told_who_it_voices_and_who_said_what(monkeypatch):
    monkeypatch.setattr(banter, "describe_neighbors", lambda me, others: {o: "on the left (web)" for o in others})
    state.register("term-b")
    me = state.register("term-a")
    state.set_reaction("term-b", "roast", "lmao that diff", source="claude", to=me)

    note = banter.context_for_claude("term-a")
    assert f"you voice {me}" in note
    assert "on the left (web)" in note and "lmao that diff" in note and "(TO YOU)" in note


def test_prompt_hook_emits_additional_context():
    out = run_bin("hook", "prompt", stdin="{}").stdout
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "[kuf-buddy]" in ctx


def test_unaddressed_neighbor_lines_are_only_answered_sometimes():
    lines = [{"ts": 1000 + i / 1000, "line": "x", "to": ""} for i in range(300)]
    answered = sum(banter.should_retort("Leş", r) for r in lines)
    assert 0 < answered < 300
    assert banter.should_retort("Leş", {"ts": 1.0, "line": "x", "to": "leş"})


# ── gossip ─────────────────────────────────────────────────────────────────────

from kuf import config, facts, gossip  # noqa: E402


@pytest.fixture
def two_goblins(monkeypatch):
    monkeypatch.setattr(facts, "collect", lambda: {"temp": 91, "hour": 14, "song": "Gece"})
    state.register("term-a")
    state.register("term-b")
    return state.load()


def conversation(s, user="ege"):
    """Every line spoken in one gossip slot, in order, with the speaker."""
    start = 100 * gossip.GOSSIP_EVERY + gossip.START_OFFSET
    said = []
    for i in range(6):
        t = start + i * gossip.LINE_S + 1
        for who in ("term-a", "term-b"):
            hit = gossip.current_line(state.load(), who, user, t)
            if hit:
                said.append((who, hit[1]))
    return said


def test_gossip_alternates_between_two_goblins_and_uses_facts(two_goblins):
    said = conversation(two_goblins)
    assert len(said) >= 2
    assert {who for who, _ in said} == {"term-a", "term-b"}
    assert all(said[i][0] != said[i + 1][0] for i in range(len(said) - 1))
    assert not any("{" in line for _, line in said)


def test_gossip_is_quiet_outside_the_window_and_with_one_goblin(two_goblins):
    before = 100 * gossip.GOSSIP_EVERY + gossip.START_OFFSET - 5
    assert gossip.current_line(state.load(), "term-a", "ege", before) is None
    alone = {**state.load(), "buddies": {"term-a": {"name": "Küf", "since": 0}}}
    assert gossip.current_line(alone, "term-a", "ege", before + 10) is None


def test_every_script_formats_with_full_facts():
    full = {"battery": 10, "charging": False, "temp": 90, "song": "s", "apps": ["steam", "discord"],
            "hour": 3, "weekday": "Sunday", "uptime": "3 days", "ram": 80,
            "a_proj": "x", "b_proj": "y", "last_file": "main.rs", "user": "ege", "a": "Küf", "b": "Pas"}
    for _, lines in gossip.SCRIPTS:
        for _, emote, template in lines:
            assert emote in EMOTES
            template.format(**full)


def test_facts_collect_never_raises():
    assert isinstance(facts.collect(), dict)


def test_goblins_call_the_user_by_configured_name():
    config.set_value("name", "ege")
    assert config.user_name() == "ege"
    assert "{user}" not in "".join(events.canned("idle", None, 0, str(i)) for i in range(20))


def test_register_survives_a_dead_process():
    assert state.register("999999998") in buddies.VARIANTS


def test_idle_goblins_dont_all_say_the_same_thing():
    s = state.load()
    now = 1_790_000_000.0
    lines = {cli.current_view(s, f"term-{n}", n, now)[1] for n in buddies.VARIANTS}
    assert len(lines) > 1


# ── written exchanges ──────────────────────────────────────────────────────────

from kuf import retorts  # noqa: E402


def test_jab_with_reply_plays_out_across_both_terminals(monkeypatch):
    monkeypatch.setattr(cli, "gossip_line", lambda *a: None)
    a_name, b_name = state.register("term-a"), state.register("term-b")
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {
            "emote": "roast", "line": f"yo {b_name}, your tests are fake", "to": b_name,
            "reply": {"emote": "rage", "line": "fake? at least i HAVE tests"},
            "last_word": {"emote": "laugh", "line": "one test. it asserts True."}}}}
    mcp(call)                                   # sent from term-a
    t0 = state.load()["reactions"]["term-a"]["ts"]

    def shown(owner, name, dt):
        return cli.current_view(state.load(), owner, name, t0 + dt)[1]

    assert shown("term-a", a_name, 1) == f"yo {b_name}, your tests are fake"
    assert "HAVE tests" not in shown("term-b", b_name, 1)        # reply waits a beat
    reaction = state.load()["reactions"]["term-a"]
    reply_at, last_at = banter.reply_delay(reaction), banter.last_word_delay(reaction)
    assert shown("term-b", b_name, reply_at + 0.1) == "fake? at least i HAVE tests"
    assert shown("term-a", a_name, last_at - 0.1) == f"yo {b_name}, your tests are fake"
    assert shown("term-a", a_name, last_at + 0.1) == "one test. it asserts True."


def test_malformed_reply_is_dropped_but_jab_still_lands():
    mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {"emote": "roast", "line": "hey", "to": "Pas",
                                           "reply": {"emote": "twerk", "line": "x"}}}})
    reaction = state.load()["reactions"]["term-a"]
    assert reaction["line"] == "hey" and reaction["reply"] is None


@pytest.mark.parametrize("line,topic", [
    ("my tests are green, loser", "tests"), ("laptop at 94°C lol", "heat"),
    ("you smell like mold", "smell"), ("it's all in the notebook", "snitch"),
    ("that crash was yours", "fail"), ("hello there", None),
])
def test_canned_retorts_follow_the_topic(line, topic):
    assert retorts.topic_of(line) == topic


def test_every_topic_retort_formats():
    for _, lines in retorts.TOPICS.values():
        for line in lines:
            line.format(them="Pas", where="on the right (api)", user="ege", snippet="x")


def test_session_start_registers_and_greets_the_user():
    config.set_value("name", "ege")
    cli.hook_start({"source": "startup"})
    reaction = state.load()["reactions"]["term-a"]
    name = state.load()["buddies"]["term-a"]["name"]
    assert reaction["source"] == "greet"
    assert "ege" in reaction["line"] or name in reaction["line"]
    assert "{" not in reaction["line"]


def test_session_start_after_compact_stays_quiet():
    cli.hook_start({"source": "compact"})
    assert "term-a" not in state.load()["reactions"]


# ── who's on screen ────────────────────────────────────────────────────────────

def niri_win(wid, ws, col, width, row=1):
    return {"id": wid, "workspace_id": ws, "pid": wid * 10,
            "layout": {"pos_in_scrolling_layout": [col, row], "tile_size": [width, 1000.0]}}


def test_visible_windows_grow_from_the_active_column_until_the_monitor_is_full():
    windows = [niri_win(1, 41, 3, 916), niri_win(2, 41, 4, 700), niri_win(3, 41, 5, 954),
               niri_win(4, 41, 6, 954), niri_win(5, 99, 1, 900)]
    workspaces = [{"id": 41, "is_active": True, "output": "HDMI", "active_window_id": 4},
                  {"id": 99, "is_active": False, "output": "HDMI", "active_window_id": 5}]
    outputs = {"HDMI": {"logical": {"width": 1920}}}
    assert screen.visible_window_ids(windows, workspaces, outputs) == {3, 4}


def test_gossip_prefers_the_two_goblins_on_screen():
    owners = ["a", "b", "c"]
    for slot in range(50):
        assert sorted(gossip.choose_pair(slot, owners, {"b", "c"})) == ["b", "c"]
    pairs = {tuple(sorted(gossip.choose_pair(slot, owners, None))) for slot in range(50)}
    assert len(pairs) > 1                     # can't tell who's visible: anyone may talk


def test_off_screen_neighbors_get_no_canned_retort_unless_they_call_you_out(monkeypatch):
    monkeypatch.setattr(banter, "visible_owners", lambda owners: {"term-a"})
    me = state.register("term-a")
    state.register("term-b")
    state.set_reaction("term-b", "roast", "lol", source="claude")
    now = time.time()
    assert banter.fresh_neighbor(state.load(), "term-a", 0, now, me) is None
    state.set_reaction("term-b", "roast", "lol", source="claude", to=me)
    assert banter.fresh_neighbor(state.load(), "term-a", 0, time.time(), me) is not None


def test_exchange_pace_follows_line_length():
    short = {"line": "your tests are fake", "reply": {"line": "nah"}}
    long_ = {"line": " ".join(["word"] * 18), "reply": {"line": " ".join(["word"] * 40)}}
    assert banter.reply_delay(short) == banter.REPLY_DELAY_MIN_S
    assert banter.reply_delay(short) < banter.reply_delay(long_) <= banter.REPLY_DELAY_MAX_S
    assert banter.last_word_delay(short) < 5
    assert banter.last_word_delay(long_) == banter.LAST_WORD_DELAY_MAX_S


def test_reading_speed_is_configurable():
    line = {"line": " ".join(["w"] * 12), "reply": {"line": "x"}}
    before = banter.reply_delay(line)
    config.set_value("words_per_sec", "12")
    assert banter.reply_delay(line) < before
    config.set_value("words_per_sec", "banana")
    assert banter.reply_delay(line) == before
