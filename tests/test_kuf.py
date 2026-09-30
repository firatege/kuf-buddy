import hashlib
import io
import os
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

from kuf import cli, events, facts, owner, render, state
from kuf.emotes import EMOTES, IDLE_BY_MOOD
from kuf.mcp_server import TOOLS, serve

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\033\[[0-9;]*m")
REAL_COLLECT = facts.collect


@pytest.fixture(autouse=True)
def kuf_home(tmp_path, monkeypatch):
    monkeypatch.setenv("KUF_HOME", str(tmp_path / "kuf"))
    monkeypatch.delenv("NIRI_SOCKET", raising=False)   # never talk to the real compositor
    monkeypatch.setattr(facts, "collect", lambda: {})  # nor to playerctl
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
    assert {t["name"] for t in tools["result"]["tools"]} == {"kuf_react", "kuf_session", "kuf_emotes"}


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


def test_neighbor_lines_get_no_canned_answer(monkeypatch):
    monkeypatch.setattr(banter, "describe_neighbors", lambda me, others: {o: "on the right (api)" for o in others})
    b_name = state.register("term-b")
    a_name = state.register("term-a")
    state.set_reaction("term-b", "roast", "yo, your code sucks", source="claude", to=a_name)

    view = cli.current_view(state.load(), "term-a", a_name, time.time())
    assert view.toward is None and b_name not in view.line


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


# ── config ─────────────────────────────────────────────────────────────────────

from kuf import config  # noqa: E402


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

def test_jab_with_reply_plays_out_across_both_terminals(monkeypatch):
    a_name, b_name = state.register("term-a"), state.register("term-b")
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {
            "emote": "roast", "line": f"yo {b_name}, your tests are fake", "to": b_name,
            "reply": {"emote": "rage", "line": "fake? at least i HAVE tests"},
            "last_word": {"emote": "laugh", "line": "one test. it asserts True."}}}}
    mcp(call)                                   # sent from term-a
    t_call = state.load()["reactions"]["term-a"]["ts"]
    assert "HAVE tests" not in cli.current_view(state.load(), "term-b", b_name, t_call + 30)[1]
    cli.hook_stop({})                           # Claude finished writing its answer
    t0 = state.load()["reactions"]["term-a"]["anchor"]

    def shown(owner, name, dt):
        return cli.current_view(state.load(), owner, name, t0 + dt)[1]

    assert shown("term-a", a_name, 1) == f"1› yo {b_name}, your tests are fake"
    assert "HAVE tests" not in shown("term-b", b_name, 1)        # reply waits a beat
    reaction = state.load()["reactions"]["term-a"]
    reply_at, last_at = banter.reply_delay(reaction), banter.last_word_delay(reaction)
    assert shown("term-b", b_name, reply_at + 0.1) == "2› fake? at least i HAVE tests"
    assert shown("term-a", a_name, last_at - 0.1) == f"1› yo {b_name}, your tests are fake"
    # the last word stacks under the jab instead of replacing it
    assert shown("term-a", a_name, last_at + 0.1) == f"1› yo {b_name}, your tests are fake\n3› one test. it asserts True."
    end = banter.exchange_end(reaction)
    assert shown("term-b", b_name, end - 0.1) == "2› fake? at least i HAVE tests"
    # ...and both sides close together
    assert "fake" not in shown("term-a", a_name, end + 0.1)
    assert "HAVE tests" not in shown("term-b", b_name, end + 0.1)


@pytest.mark.parametrize("extra", [
    {},                                                               # no reply, no last word
    {"reply": {"emote": "rage", "line": "what"}},                     # last word missing
    {"reply": {"emote": "twerk", "line": "x"}, "last_word": {"emote": "laugh", "line": "ha"}},
])
def test_jab_without_reply_and_last_word_is_rejected(extra):
    out = mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {"emote": "roast", "line": "hey", "to": "Pas", **extra}}})
    assert out[0]["result"]["isError"]
    assert "term-a" not in state.load()["reactions"]


def test_last_word_is_required_by_the_schema():
    schema = next(t for t in TOOLS if t["name"] == "kuf_react")["inputSchema"]
    assert schema["dependentRequired"]["to"] == ["reply", "last_word"]


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


def test_exchange_pace_follows_line_length():
    short = {"line": "your tests are fake", "reply": {"line": "nah"}}
    long_ = {"line": " ".join(["word"] * 18), "reply": {"line": " ".join(["word"] * 40)}}
    assert banter.reply_delay(short) == banter.REPLY_DELAY_MIN_S
    assert banter.reply_delay(short) < banter.reply_delay(long_) <= banter.REPLY_DELAY_MAX_S
    assert banter.last_word_delay(short) < 8
    assert banter.last_word_delay(long_) == banter.LAST_WORD_DELAY_MAX_S


def test_reading_speed_is_configurable():
    line = {"line": " ".join(["w"] * 12), "reply": {"line": "x"}}
    before = banter.reply_delay(line)
    config.set_value("words_per_sec", "12")
    assert banter.reply_delay(line) < before
    config.set_value("words_per_sec", "banana")
    assert banter.reply_delay(line) == before


def test_exchange_falls_back_to_call_time_if_the_turn_never_ends():
    reaction = {"ts": 100.0, "source": "claude", "line": "x", "reply": {"emote": "sus", "line": "y"}}
    assert banter.exchange_start(reaction, 150.0) is None
    assert banter.exchange_start(reaction, 100.0 + banter.ANCHOR_WAIT_S + 1) == 100.0
    assert banter.exchange_start({**reaction, "source": "cli"}, 101.0) == 100.0


# ── facing ─────────────────────────────────────────────────────────────────────

def test_mirror_flips_direction_and_keeps_rows_aligned():
    rows = ["(☞ﾟ∀ﾟ)☞", "▐▌/|▓▓▓|\\▐▌,,"]
    flipped = render.mirror(rows)
    assert flipped[0].strip() == "☜(ﾟ∀ﾟ☜)"
    assert flipped[1] == ",,▐▌/|▓▓▓|\\▐▌"
    assert len({render.width(r) for r in flipped}) == 1
    assert render.mirror(render.mirror(["(•̀ᴗ•́)☝"]))[0].strip() == "(•̀ᴗ•́)☝"


def test_goblin_faces_the_neighbor_he_talks_to_and_looks_ahead_otherwise(monkeypatch):
    a_name, b_name = state.register("term-a"), state.register("term-b")
    state.set_reaction("term-b", "roast", "hey", source="cli", to=a_name,
                       reply={"emote": "rage", "line": "what"})
    t = state.load()["reactions"]["term-b"]["ts"]
    assert cli.current_view(state.load(), "term-a", a_name, t + 10).toward == "term-b"
    assert cli.current_view(state.load(), "term-a", a_name, t + 500).toward is None


def test_left_facing_layout_puts_bubble_first_with_tail_toward_him():
    out = ANSI.sub("", render.compose("roast", "lmao", 0, facing="left")).splitlines()
    face = next(row for row in out if "☜" in row)
    assert face.index(">") < face.index("☜")


@pytest.mark.parametrize("name", ["tea", "nap", "phone", "stretch", "game", "nosepick"])
def test_idle_life_emotes_are_looping_animations(name):
    assert len(EMOTES[name]["frames"]) >= 4


# ── what the user is up to ─────────────────────────────────────────────────────

def test_facts_collect_never_raises():
    assert isinstance(REAL_COLLECT(), dict)


@pytest.mark.parametrize("title,chat", [
    ("@Piroz - Discord", "@Piroz"), ("🎮 ODA-1 | KAINAT - Discord", "KAINAT"),
    ("Friends - Discord", None), ("Discord", None), ("some browser tab", None),
])
def test_discord_title_names_the_chat(title, chat):
    assert facts.discord_chat(title) == chat


def test_describe_mentions_song_and_discord():
    line = facts.describe({"song": "Ezhel - Felaket", "discord_chat": "@Piroz", "hour": 3,
                           "weekday": "Tuesday", "apps": ["steam"]})
    assert "listening to Ezhel - Felaket" in line and "with @Piroz" in line
    assert "steam" in line and "03:00" in line
    assert "the KAINAT discord server" in facts.describe({"discord_chat": "KAINAT"})


def test_one_turn_in_ten_reads_into_the_users_life():
    rolls = [i / 100 for i in range(100)]
    about_life = sum("clues" in banter.topic_note("listening to x", r) for r in rolls)
    assert about_life == 10
    assert "conversation or the code" in banter.topic_note("", 0.0)   # nothing known: fall back


def test_other_turns_dont_leak_the_users_facts():
    note = banter.topic_note("listening to Ezhel - Felaket; 17 unread", 0.99)
    assert "Ezhel" not in note and "17" not in note


def test_context_carries_the_topic_for_this_turn(monkeypatch):
    monkeypatch.setattr(facts, "collect", lambda: {"song": "Ezhel - Felaket"})
    monkeypatch.setattr(banter.random, "random", lambda: 0.05)
    note = banter.context_for_claude("term-a")
    assert "read boss's mood" in note and "Ezhel - Felaket" in note
    assert "Never repeat the clues" in note


# ── unique names & memory ─────────────────────────────────────────────────────

def test_duplicate_names_are_given_to_free_goblins(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    now = time.time()
    dupes = {"old": {"name": "Kir", "since": now - 2}, "new": {"name": "Kir", "since": now - 1}}
    state.update(lambda s: {**s, "buddies": dupes})
    buddies_now = state.load()["buddies"]
    assert buddies_now["old"]["name"] == "Kir"
    assert buddies_now["new"]["name"] not in ("Kir",) and buddies_now["new"]["name"] in buddies.VARIANTS


def test_both_goblins_remember_a_written_exchange():
    a_name, b_name = state.register("term-a"), state.register("term-b")
    mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {
            "emote": "roast", "line": "your tests are fake", "to": b_name.lower(),
            "reply": {"emote": "rage", "line": "at least i HAVE tests"},
            "last_word": {"emote": "laugh", "line": "one test. asserts True."}}}})
    s = state.load()
    mine, theirs = state.memories(s, a_name)[-1], state.memories(s, b_name)[-1]
    assert mine["said"] == "your tests are fake" and mine["then"] == "one test. asserts True."
    assert theirs["heard"] == "your tests are fake" and theirs["from"] == a_name

    note = banter.context_for_claude("term-b")
    assert "your tests are fake" in note and "at least i HAVE tests" in note


def distinct(i: int) -> str:
    return hashlib.sha256(str(i).encode()).hexdigest()[:40]


def test_memory_is_capped_and_outlives_the_terminal():
    name = state.register("term-a")
    for i in range(state.MEMORY_LINES + 5):
        mcp({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {
            "name": "kuf_react", "arguments": {"emote": "sus", "line": distinct(i)}}})
    history = state.memories(state.load(), name)
    assert len(history) == state.MEMORY_LINES and history[-1]["said"] == distinct(state.MEMORY_LINES + 4)
    state.update(lambda s: {**s, "buddies": {}})
    assert state.memories(state.load(), name)


# ── idle lines about the user's life ───────────────────────────────────────────

from kuf import life  # noqa: E402

FULL_FACTS = {"song": "Yaşlı Amca - Kimsesiz", "discord_chat": "KAINAT", "youtube": "lofi",
              "whatsapp_unread": 17, "sites": ["github", "sim companies", "whatsapp"],
              "apps": ["steam", "discord"]}


def test_every_life_line_formats():
    fields = {"user": "ege", "song": "s", "server": "K", "dm": "@p", "video": "v", "unread": 3}
    for lines in life.LIFE.values():
        for line in lines:
            assert "{" not in line.format(**fields)


def test_one_idle_line_in_ten_is_about_the_users_life():
    said = [life.life_line(FULL_FACTS, str(slot), "ege") for slot in range(4000)]
    share = sum(line is not None for line in said) / len(said)
    assert 0.07 < share < 0.13
    assert life.life_line({}, "1", "ege") is None


def test_idle_pool_has_fifty_lines_and_no_heat_talk():
    idle = events.LINES["idle"]
    assert len(idle) == len(set(idle)) == 50
    every = " ".join(line for lines in events.LINES.values() for line in lines).lower()
    assert not any(word in every for word in ("melt", "cooling", "°c"))


@pytest.mark.parametrize("title,info", [
    ("(3) Lofi beats - YouTube - Brave", {"youtube": "Lofi beats"}),
    ("(17) WhatsApp - Brave", {"site": "whatsapp", "whatsapp_unread": 17}),
    ("Benzin istasyonu - Sim Companies - Brave", {"site": "sim companies"}),
    ("Auth-ism/niri-setup: niri desktop - Brave", {"site": "github"}),
    ("My bank account - Brave", {}),
])
def test_only_known_sites_are_read_from_tabs(title, info):
    assert facts.site_of(title) == info


def test_facts_are_cached_between_status_line_runs(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(facts, "collect", lambda: calls.append(1) or {"song": "x"})
    path = tmp_path / "facts.json"
    assert facts.cached(path, now=100.0) == {"song": "x"}
    assert facts.cached(path, now=100.0 + facts.CACHE_S - 1) == {"song": "x"}
    assert len(calls) == 1
    facts.cached(path, now=100.0 + facts.CACHE_S + 1)
    assert len(calls) == 2


def test_idle_line_changes_about_once_a_minute(monkeypatch):
    monkeypatch.setattr(facts, "collect", lambda: FULL_FACTS)
    name = state.register("term-a")
    base = time.time()
    step = cli.IDLE_SWAP_S
    assert cli.IDLE_SWAP_S == 60
    lines = [cli.current_view(state.load(), "term-a", name, base + k * step)[1] for k in range(6)]
    assert len(set(lines)) == 6


# ── no repeats ─────────────────────────────────────────────────────────────────

from kuf import idle  # noqa: E402


def react(line: str) -> dict:
    return mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_react", "arguments": {"emote": "sus", "line": line}}})[0]["result"]


def test_claude_cant_make_a_goblin_repeat_himself():
    state.register("term-a")
    assert not react("bro you got one playlist and it's crying for help")["isError"]
    again = react("bro, you got ONE playlist and it's crying for help!")
    assert again["isError"] and "already said" in again["content"][0]["text"]
    assert not react("steam's open again, work day my ass")["isError"]


def test_idle_line_stays_put_within_a_slot_and_never_repeats_back_to_back():
    T0 = time.time()
    name = state.register("term-a")
    pool = [(f"t{i}", f"line {i}") for i in range(5)]
    first = idle.line_for_slot("term-a", name, "1", T0, pool)
    assert idle.line_for_slot("term-a", name, "1", T0 + 10, pool) == first
    said = [idle.line_for_slot("term-a", name, str(k), T0 + 20 * k, pool) for k in range(2, 6)]
    assert len({first, *said}) == 5            # all five before any repeat
    sixth = idle.line_for_slot("term-a", name, "6", T0 + 120, pool)
    assert sixth == first                      # pool exhausted: the oldest comes back


def test_goblins_dont_echo_each_other(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    T0 = time.time()
    a, b = state.register("term-a"), state.register("term-b")
    pool = [("t1", "one"), ("t2", "two")]
    first = idle.line_for_slot("term-a", a, "1", T0, pool)
    assert idle.line_for_slot("term-b", b, "1", T0 + 1, pool) != first
    later = T0 + idle.SHARED_COOLDOWN_S + 1       # after a while the line is fair game
    assert idle.choose(pool, idle._last_said(state.load(), b, later), later, "x") in pool


# ── cut exchanges & glow ───────────────────────────────────────────────────────

def jab_from_a(b_name: str) -> float:
    state.set_reaction("term-a", "roast", "your tests are fake", source="cli", to=b_name,
                       reply={"emote": "rage", "line": "at least i HAVE tests"},
                       last_word={"emote": "laugh", "line": "one test. asserts True."})
    return state.load()["reactions"]["term-a"]["ts"]


@pytest.mark.parametrize("who_moves_on", ["term-a", "term-b"])
def test_exchange_ends_on_both_screens_when_either_side_moves_on(monkeypatch, who_moves_on):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    a_name, b_name = state.register("term-a"), state.register("term-b")
    t = jab_from_a(b_name)
    reaction = state.load()["reactions"]["term-a"]
    mid = t + banter.last_word_delay(reaction) + 1
    assert "HAVE tests" in cli.current_view(state.load(), "term-b", b_name, mid).line
    assert "asserts True" in cli.current_view(state.load(), "term-a", a_name, mid).line

    state.add_event(who_moves_on, {"kind": "code", "file": "/x/main.py"})
    later = time.time() + 1
    assert "HAVE tests" not in cli.current_view(state.load(), "term-b", b_name, later).line
    assert "tests are fake" not in cli.current_view(state.load(), "term-a", a_name, later).line


def test_target_saying_something_new_cuts_the_exchange(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    a_name, b_name = state.register("term-a"), state.register("term-b")
    t = jab_from_a(b_name)
    time.sleep(0.01)
    state.set_reaction("term-b", "chill", "anyway, back to work", source="cli")
    now = t + 8
    assert cli.current_view(state.load(), "term-b", b_name, now).line == "anyway, back to work"
    assert "tests are fake" not in cli.current_view(state.load(), "term-a", a_name, now).line


def test_talking_goblins_glow_white():
    plain = render.compose("roast", "hey", 0)
    glowing = render.compose("roast", "hey", 0, highlight=True)
    assert render.GLOW not in plain and render.GLOW in glowing
    assert ANSI.sub("", plain) == ANSI.sub("", glowing)


# ── ghosts (daemon sessions) ───────────────────────────────────────────────────

def test_goblin_whose_status_line_stopped_is_a_ghost_and_leaves_the_neighbors(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    state.register("term-a")
    state.register("term-b")
    now = time.time()
    assert "term-b" in state.neighbors(state.load(), "term-a")
    stale = now - state.GHOST_S - 5
    state.update(lambda s: {**s, "buddies": {**s["buddies"],
                                             "term-b": {**s["buddies"]["term-b"], "since": stale, "seen": stale}}})
    assert "term-b" not in state.neighbors(state.load(), "term-a")
    assert state.mark_seen("term-a", now + state.SEEN_EVERY_S + 1)
    assert not state.mark_seen("term-a", now + state.SEEN_EVERY_S + 2)   # throttled


def test_windowless_daemon_session_adopts_the_ghosts_window(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    windows = [{"id": 207, "pid": 50, "workspace_id": 1, "layout": {"pos_in_scrolling_layout": [6, 1]}},
               {"id": 214, "pid": 60, "workspace_id": 1, "layout": {"pos_in_scrolling_layout": [5, 1]}}]
    tree = {"501": 50, "601": 60, "999": 1}          # 999 = daemon worker, no terminal above it
    monkeypatch.setattr(screen, "niri_windows", lambda: windows)
    monkeypatch.setattr(screen, "parent_and_name", lambda pid: (tree.get(str(pid), 1), "claude"))
    for owner in ("501", "601", "999"):
        state.register(owner)
    stale = time.time() - state.GHOST_S - 5
    state.update(lambda s: {**s, "buddies": {**s["buddies"], "501": {**s["buddies"]["501"], "seen": stale, "since": stale}}})

    assert screen.window_of("999", windows) is None
    assert screen.adopt_window("999") == "501"
    assert screen.window_of("999", windows)["id"] == 207
    assert "501" not in state.load()["buddies"]
    assert screen.direction(screen.window_of("999", windows), screen.window_of("601", windows)) == "on the left"


def test_goblins_registered_before_seen_tracking_keep_their_names(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    old = time.time() - state.GHOST_PRUNE_S * 10
    state.update(lambda s: {**s, "buddies": {"legacy": {"name": "Kir", "since": old}}})
    assert state.load()["buddies"]["legacy"]["name"] == "Kir"     # not pruned, not renamed


def test_discord_chat_is_forgotten_once_discord_sits_unused(monkeypatch):
    window = {"app_id": "discord", "title": "@Piroz - Discord", "is_focused": False,
              "focus_timestamp": {"secs": 1000, "nanos": 0}}
    monkeypatch.setattr(facts, "niri_windows", lambda: [window])
    monkeypatch.setattr(facts.time, "clock_gettime", lambda clock: 1000 + 60)
    assert facts.discord() == {"discord_chat": "@Piroz"}
    monkeypatch.setattr(facts.time, "clock_gettime", lambda clock: 1000 + facts.DISCORD_FRESH_S + 1)
    assert facts.discord() == {}
    assert facts.idle_for({**window, "is_focused": True}) == 0.0


# ── looks & fitting emotes ─────────────────────────────────────────────────────

from kuf import emotes  # noqa: E402


@pytest.mark.parametrize("name", sorted(buddies.VARIANTS))
@pytest.mark.parametrize("emote", ["chill", "nap", "puke", "rage", "tea"])
def test_every_goblin_wears_his_own_skin_without_breaking_the_sprite(name, emote):
    plain = EMOTES[emote]["frames"][0]
    dressed = render.dress(plain, name)
    assert [render.width(r) for r in dressed] == [render.width(r) for r in plain]
    torso, _ = buddies.skin(name)
    assert torso[0] in dressed[2]


def test_goblins_look_different():
    bodies = {render.dress(EMOTES["chill"]["frames"][0], n)[2] for n in buddies.VARIANTS}
    assert len(bodies) == len(buddies.VARIANTS)


def test_talking_goblins_never_nap_by_day():
    for template in events.LINES["idle"]:
        for seed in range(5):
            assert emotes.for_line(template, None, "comfy", str(seed)) not in ("nap", "sleep")


@pytest.mark.parametrize("template,kind,expected", [
    ("steam's open. 'just one game' my ass.", "steam", {"game"}),
    ("{server} open on discord again?", "discord", {"phone", "sus"}),
    ("*burp* ...the tests can wait.", None, {"burp"}),
    ("found a chip under the cushion.", None, {"eat"}),
    ("zzz... {user}... the bug... zzz", None, {"sleep"}),
])
def test_emote_fits_the_line(template, kind, expected):
    assert emotes.for_line(template, kind, "comfy", "1") in expected


def test_every_life_kind_has_emotes():
    assert set(life.LIFE) <= set(emotes.LIFE_EMOTES)
    assert all(e in EMOTES for options in emotes.LIFE_EMOTES.values() for e in options)
    assert all(e in EMOTES for _, e in emotes.LINE_EMOTES)


# ── rooms & snoop ──────────────────────────────────────────────────────────────

from kuf.rooms import ROOMS  # noqa: E402


@pytest.mark.parametrize("name", sorted(ROOMS))
def test_room_masks_match_their_frames(name):
    spec = ROOMS[name]
    assert len(spec["frames"]) == len(spec["masks"]) == 4
    for rows, masks in zip(spec["frames"], spec["masks"]):
        assert len(rows) == len(masks) == 4
        for row, mask in zip(rows, masks):
            assert render.width(row) <= render.SPRITE_COLS
            assert set(mask) <= set(". r" + "".join(render.ROLE_COLORS))


def test_rooms_color_their_parts_and_keep_the_goblins_shirt():
    out = render.compose("smoke", "yo", 1, name="Kabuk")
    assert "\033[38;5;208m" in out                     # glowing ember
    assert "$$$" in ANSI.sub("", out)                  # his own shirt, even on the balcony
    trip = [render.compose("trip", "yo", t, name="Snoop") for t in range(2)]
    assert trip[0] != trip[1]                          # rainbow shifts every frame


def test_mirrored_goblin_keeps_words_readable():
    out = ANSI.sub("", render.compose("roast", "hi", 0, facing="left"))
    assert "LMAO" in out and "OAML" not in out


def test_snoop_is_a_goblin_who_mostly_smokes():
    assert "Snoop" in buddies.VARIANTS
    picks = [emotes.for_line("bro what's up", None, "comfy", str(i), "Snoop") for i in range(200)]
    smoking = {"smoke", "snoop-bong", "snoop-rings", "snoop-roll"}
    assert sum(p in smoking for p in picks) > len(picks) / 3 and "trip" in picks
    assert emotes.for_line("sparking a blunt, relax", None, "comfy", "1") == "smoke"


# ── looks & joint sessions ─────────────────────────────────────────────────────

import random  # noqa: E402

from kuf import looks, session  # noqa: E402
from kuf.looks import _kit  # noqa: E402


def test_every_goblin_has_a_looks_module():
    assert set(looks.MODULES) == set(buddies.VARIANTS)
    for name in looks.MODULES:
        assert all(e in EMOTES for e in looks.habits(name)), name
        assert 0.0 <= looks.accepts_joint(name) <= 1.0


def test_kit_builds_masks_that_line_up():
    spec = _kit.scene("x", [["  (ˆ‿ˆ)y═*", "  (ಠ益ಠ)", "▐▌/|▓▓▓| ▐▌", "░▓░"]] * 4, {"░": "s", "▓": "s", "*": "e", "═": " "})
    body, smoke = spec["masks"][0][2], spec["masks"][0][3]
    assert body == "........ .."                                       # shirt keeps goblin color
    assert smoke == "sss"
    assert len(spec["masks"][0][1]) == render.width("  (ಠ益ಠ)")        # wide chars take two cells


@pytest.mark.parametrize("name", sorted(looks.shared.EMOTES))
def test_shared_joint_emotes_fit(name):
    for rows, masks in zip(EMOTES[name]["frames"], EMOTES[name]["masks"]):
        assert len(rows) == 4 and all(render.width(r) <= render.SPRITE_COLS for r in rows)
        assert [len(m) for m in masks] == [render.width(r) for r in rows]


def test_signature_moves_belong_to_their_goblin(monkeypatch):
    monkeypatch.setitem(looks.OWNER, "kabuk-cash", "Kabuk")
    assert looks.can_use("Kabuk", "kabuk-cash") and not looks.can_use("Bit", "kabuk-cash")
    assert looks.can_use("Bit", "chill")


def circle(monkeypatch, *names):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    now = time.time()
    buddies_now = {f"t{i}": {"name": n, "since": now, "seen": now} for i, n in enumerate(names)}
    state.update(lambda s: {**s, "buddies": buddies_now})
    return state.load()


class Rolls(random.Random):
    """random.Random whose .random() returns scripted values; choice() takes the first
    option unless a test replaces it (the stock one would eat the scripted values)."""
    def __init__(self, *values):
        super().__init__(0)
        self.values = list(values)

    def random(self):
        return self.values.pop(0) if self.values else 0.0

    def choice(self, seq):
        return seq[0]


def test_snoop_passes_the_joint_and_personality_decides(monkeypatch):
    s = circle(monkeypatch, "Snoop", "Çamur", "Bit")
    assert session.plan(s, "t2", None, Rolls(0.0)) is None                       # Bit never rolls one
    assert session.plan(s, "t1", None, Rolls(0.06)) is None                      # Çamur rolls one only 5% of turns
    assert session.plan(s, "t0", None, Rolls(0.99)) is None                      # most turns: no joint
    rng = Rolls(0.0, 0.0, 0.5)                                                # Bit rolls 50 vs 5
    rng.choice = lambda seq: seq[0] if seq and isinstance(seq[0], str) and seq[0].startswith("t") else 2
    planned = session.plan(s, "t0", None, rng)
    assert planned["kind"] == "session" and planned["order"][:2] == ["Snoop", "Çamur"]
    assert "Bit" not in planned["order"]                                        # Bit almost never takes it
    assert planned["dice"]["Bit"] == {"roll": 50, "needs": 5, "yes": False}
    rng = Rolls(0.0, 0.5)
    rng.choice = lambda seq: "t2" if "t2" in seq else seq[0]
    refused = session.plan(s, "t0", None, rng)
    assert refused["kind"] == "refused" and refused["target"] == "Bit"
    assert "smokes it himself" in session.note(refused)


def test_written_session_plays_step_by_step_and_everyone_remembers(monkeypatch):
    s = circle(monkeypatch, "Snoop", "Çamur")
    use_owner(monkeypatch, "t0")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Çamur", "Snoop"], "ts": time.time()})
    bad = session.start("t0", [{"name": "Çamur", "emote": "joint", "line": "x"}])
    assert "order" in bad
    steps = [{"name": "Snoop", "emote": "joint", "line": "puff puff, smooth"},
             {"name": "Çamur", "emote": "joint", "line": "bro what if the couch is high too"},
             {"name": "Snoop", "emote": "joint", "line": "then we all family, man"}]
    assert session.start("t0", steps) is None
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"] + session.ROLL_S          # after rolling it
    spans = session.durations(state.load()["session"]["steps"])
    at = lambda owner, dt: session.view(state.load(), owner, t0 + dt)
    assert at("t0", 1)[1] == "1› puff puff, smooth" and at("t0", 1)[2] == "t1"
    assert at("t1", 1) == ("chill", session.WAITING, "t0", True)
    assert at("t1", spans[0] + 0.5)[1] == "2› bro what if the couch is high too"
    assert at("t0", spans[0] + 0.5)[1] == "1› puff puff, smooth"                   # waiting, last line kept
    assert at("t0", sum(spans) + session.LINGER_S + 1) is None                  # everyone closes together
    memory = state.memories(state.load(), "Çamur")[-1]
    assert memory["with"] == ["Snoop"] and len(memory["session"]) == 3
    assert "joint session with Snoop" in banter.recall(state.load(), "Çamur", time.time())


def test_session_ends_for_everyone_when_one_moves_on(monkeypatch):
    s = circle(monkeypatch, "Snoop", "Çamur")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Çamur"], "ts": time.time()})
    session.start("t0", [{"name": "Snoop", "emote": "joint", "line": "a"}, {"name": "Çamur", "emote": "joint", "line": "b"}])
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    assert session.view(state.load(), "t1", t0 + 1)
    state.add_event("t1", {"kind": "code", "file": "/x.py"})
    assert session.view(state.load(), "t0", t0 + 1) is None


def test_session_tool_needs_a_plan(monkeypatch):
    circle(monkeypatch, "Snoop", "Çamur")
    use_owner(monkeypatch, "t0")
    out = mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "kuf_session", "arguments": {"steps": [{"name": "Snoop", "line": "yo"}]}}})[0]["result"]
    assert out["isError"] and "no joint session" in out["content"][0]["text"]


@pytest.mark.parametrize("name", sorted(looks.MODULES))
def test_every_goblin_has_at_least_five_moves_of_his_own(name):
    own = looks.signatures(name)
    assert len(own) >= looks.MIN_SIGNATURES
    slug = looks.SLUG_OF[name]
    assert all(e.startswith(f"{slug}-") for e in own)
    assert all(e in looks.habits(name) for e in own)


@pytest.mark.parametrize("emote", sorted(looks.SIGNATURES))
def test_signature_moves_are_real_four_frame_loops(emote):
    spec = looks.SIGNATURES[emote]
    assert len(spec["frames"]) == 4
    for rows, masks in zip(spec["frames"], spec["masks"]):
        assert len(rows) == 4
        assert [len(m) for m in masks] == [render.width(r) for r in rows]
        assert all(render.width(r) <= render.SPRITE_COLS for r in rows)
    assert len({tuple(f) for f in spec["frames"]}) >= 3, "barely moves"


# ── picking your goblin ────────────────────────────────────────────────────────

@pytest.mark.parametrize("typed,name", [("snoop", "Snoop"), ("camur", "Çamur"), ("LES", "Leş"),
                                        ("sumuk", "Sümük"), ("kuf", "Küf"), ("nobody", None), ("", None)])
def test_goblin_names_resolve_without_turkish_letters(typed, name):
    assert buddies.resolve(typed) == name


def test_kuf_goblin_env_picks_him_at_start(monkeypatch):
    monkeypatch.setenv("KUF_GOBLIN", "snoop")
    assert state.register("term-a") == "Snoop"


def test_claiming_a_taken_goblin_moves_the_other_terminal(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    monkeypatch.delenv("KUF_GOBLIN", raising=False)
    first = state.register("term-a")
    state.register("term-b")
    assert state.claim("term-b", first) == first
    names = {o: b["name"] for o, b in state.load()["buddies"].items()}
    assert names["term-b"] == first and names["term-a"] != first
    assert len(set(names.values())) == 2


def test_kuf_be_command(monkeypatch, capsys):
    monkeypatch.delenv("KUF_GOBLIN", raising=False)
    cli.main(["be", "camur"])
    assert "Çamur" in capsys.readouterr().out
    assert state.load()["buddies"]["term-a"]["name"] == "Çamur"
    cli.main(["be"])
    assert "this terminal: Çamur" in capsys.readouterr().out
    cli.main(["be", "gandalf"])
    assert "no goblin called" in capsys.readouterr().out


def test_refusal_is_a_back_and_forth_and_the_refuser_says_nope(monkeypatch):
    s = circle(monkeypatch, "Snoop", "Bit")
    rng = Rolls(0.0, 0.5)
    rng.choice = lambda seq: seq[0]
    planned = session.plan(s, "t0", None, rng)
    assert planned["kind"] == "refused" and planned["order"] == ["Snoop", "Bit", "Snoop", "Bit", "Snoop"]
    assert "kuf_session" in session.note(planned)
    session.save_plan("t0", planned)
    steps = [{"name": n, "emote": "joint", "line": f"line {i}"} for i, n in enumerate(planned["order"])]
    assert session.start("t0", steps) is None
    written = state.load()["session"]["steps"]
    assert [w["emote"] for w in written] == ["joint", "nope", "joint", "nope", "joint"]


def test_forced_joint_skips_the_dice_and_can_pick_who(monkeypatch):
    s = circle(monkeypatch, "Snoop", "Çamur", "Küf")
    session.force("t0", "Küf")
    s = state.load()
    planned = session.plan(s, "t0", set(), Rolls(0.99, 0.0))        # would normally skip, nobody visible
    assert planned and "Küf" in planned["order"]
    session.save_plan("t0", planned)
    assert "t0" not in state.load()["force_joint"]                    # used up


def test_kuf_joint_command(monkeypatch, capsys):
    monkeypatch.delenv("KUF_GOBLIN", raising=False)
    cli.main(["be", "kir"])
    cli.main(["joint"])
    assert "only Snoop" in capsys.readouterr().out
    cli.main(["be", "snoop"])
    cli.main(["joint", "camur"])
    assert "nobody around yet" in capsys.readouterr().out          # Çamur isn't open
    assert state.load()["force_joint"]["term-a"]["target"] == "Çamur"


def test_everyone_in_the_circle_glows_even_on_the_last_step(monkeypatch):
    circle(monkeypatch, "Snoop", "Bit")
    session.save_plan("t0", {"kind": "refused", "host": "t0", "target": "Bit", "why": "",
                             "order": ["Snoop", "Bit", "Snoop"], "ts": time.time()})
    session.start("t0", [{"name": n, "emote": "joint", "line": f"l{i}"} for i, n in enumerate(["Snoop", "Bit", "Snoop"])])
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    spans = session.durations(state.load()["session"]["steps"])
    last = t0 + sum(spans[:2]) + 0.5
    assert session.view(state.load(), "t0", last)[2] == "t1"          # faces Bit -> glows
    assert session.view(state.load(), "t1", last)[2] == "t0"


def test_banter_rolls_thirty_percent_and_either_side_can_open(monkeypatch):
    s = circle(monkeypatch, "Kir", "Leke")
    assert session.plan_banter(s, "t0", None, Rolls(0.31)) is None
    opened_by_me = session.plan_banter(s, "t0", None, Rolls(0.1, 0.2))
    assert opened_by_me["order"] == ["Kir", "Leke", "Kir", "Leke"]
    opened_by_them = session.plan_banter(s, "t0", None, Rolls(0.1, 0.9))
    assert opened_by_them["order"] == ["Leke", "Kir", "Leke", "Kir"]
    assert "Leke opens" in session.note(opened_by_them)
    assert session.plan_banter(s, "t0", set(), Rolls(0.0)) is None             # nobody on screen


def test_a_neighbor_who_called_you_out_always_gets_an_answer(monkeypatch):
    circle(monkeypatch, "Kir", "Leke")
    state.set_reaction("t1", "roast", "kir you fraud", source="claude", to="Kir")
    planned = session.plan_banter(state.load(), "t0", None, Rolls(0.99))
    assert planned and planned["order"][0] == "Kir"


def test_banter_plays_like_a_session_with_chill_by_default(monkeypatch):
    circle(monkeypatch, "Kir", "Leke")
    use_owner(monkeypatch, "t0")
    session.save_plan("t0", session.plan_banter(state.load(), "t0", None, Rolls(0.1, 0.2)))
    out = mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "kuf_session", "arguments": {
        "steps": [{"name": "Kir", "line": "a"}, {"name": "Leke", "emote": "leke-faint", "line": "b"},
                  {"name": "Kir", "emote": "leke-faint", "line": "c"}, {"name": "Leke", "line": "d"}]}}})[0]["result"]
    assert not out["isError"]
    emotes_used = [w["emote"] for w in state.load()["session"]["steps"]]
    assert emotes_used == ["chill", "leke-faint", "chill", "chill"]          # Kir can't borrow Leke's move


def test_forced_joint_reaches_off_screen_goblins_when_nobody_is_visible(monkeypatch):
    circle(monkeypatch, "Snoop", "Kabuk")
    session.force("t0")
    planned = session.plan(state.load(), "t0", {"t0"}, Rolls(0.99, 0.0))
    assert planned and "Kabuk" in planned["order"]


def test_daemon_session_is_found_through_its_attach_client(monkeypatch):
    windows = [{"id": 175, "pid": 50, "workspace_id": 1, "layout": {"pos_in_scrolling_layout": [2, 1]}}]
    tree = {"777": 1, "501": 50}                      # 777 = daemon worker, 501 = `claude attach` in kitty
    monkeypatch.setattr(screen, "parent_and_name", lambda pid: (tree.get(str(pid), 1), "claude"))
    monkeypatch.setattr(screen, "attach_client", lambda owner: 501 if owner == "777" else None)
    assert screen.window_of("777", windows)["id"] == 175


def test_claudes_own_commands_in_the_writing_turn_dont_cut_the_session(monkeypatch):
    circle(monkeypatch, "Snoop", "Kabuk")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Kabuk"], "ts": time.time()})
    session.start("t0", [{"name": "Snoop", "line": "a"}, {"name": "Kabuk", "line": "b"}])
    state.add_event("t0", {"kind": "win", "cmd": "pytest"})      # same turn, before it ends
    time.sleep(0.01)
    session.anchor("t0")                                          # turn ends, playback starts
    t0 = state.load()["session"]["anchor"]
    assert session.view(state.load(), "t1", t0 + 1)
    time.sleep(0.01)
    state.add_event("t1", {"kind": "code", "file": "/x.py"})     # after it started: that cuts
    assert session.view(state.load(), "t1", t0 + 1) is None


def test_session_lines_glow_face_each_other_and_stack(monkeypatch):
    circle(monkeypatch, "Snoop", "Kabuk")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Kabuk", "Snoop", "Kabuk"], "ts": time.time()})
    session.start("t0", [{"name": n, "line": l} for n, l in
                         [("Snoop", "one"), ("Kabuk", "two"), ("Snoop", "three"), ("Kabuk", "four")]])
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"] + session.ROLL_S
    spans = session.durations(state.load()["session"]["steps"])
    third = t0 + sum(spans[:2]) + 0.5
    view = cli.current_view(state.load(), "t0", "Snoop", third)
    assert view.toward == "t1"                        # glows and faces Kabuk
    assert view.line == "1› one\n3› three"                  # his lines stacked, like a jab + last word
    kabuk = cli.current_view(state.load(), "t1", "Kabuk", third)
    assert kabuk.toward == "t0" and kabuk.line == "2› two"



def test_joint_command_rolls_right_away_and_the_plan_waits_for_claude(monkeypatch, capsys):
    circle(monkeypatch, "Snoop", "Kabuk")
    use_owner(monkeypatch, "t0")
    monkeypatch.setattr(cli, "visible_owners", lambda owners: None)
    cli.main(["joint", "kabuk"])
    out = capsys.readouterr().out
    assert "rolled: Snoop → Kabuk" in out and "Snoop › Kabuk" in out and "kuf_session" not in out
    planned = state.load()["plans"]["t0"]
    assert session.pending(state.load(), "t0") == planned
    monkeypatch.setattr(session, "plan", lambda *a, **k: None)     # the hook doesn't re-roll it away
    monkeypatch.setattr(cli, "context_for_claude", lambda owner: "ctx")
    cli.hook_prompt({})
    assert "Snoop -> Kabuk" in capsys.readouterr().out


@pytest.mark.parametrize("facing", ["right", "left"])
def test_status_lines_never_start_with_bare_spaces(facing):
    """Claude Code strips leading spaces, which would slide tall bubbles out of line."""
    out = render.compose("joint", "one line that is long enough to wrap around twice for sure\nsecond line", 0,
                         name="Kabuk", facing=facing)
    for row in out.splitlines():
        assert not row.startswith(" "), repr(row)



def test_snoop_rolls_it_first_while_the_others_watch_without_glowing(monkeypatch):
    circle(monkeypatch, "Snoop", "Çamur")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Çamur"], "ts": time.time()})
    session.start("t0", [{"name": "Snoop", "line": "lit"}, {"name": "Çamur", "line": "bro"}])
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    snoop = cli.current_view(state.load(), "t0", "Snoop", t0 + 2)
    camur = cli.current_view(state.load(), "t1", "Çamur", t0 + 2)
    assert (snoop.emote, snoop.line, snoop.glow) == ("snoop-roll", session.ROLLING, False)
    assert camur.toward == "t0" and camur.glow is False            # turned to watch him roll
    lit = cli.current_view(state.load(), "t0", "Snoop", t0 + session.ROLL_S + 0.5)
    assert lit.line == "1› lit" and lit.glow is True


def test_banter_skips_the_rolling(monkeypatch):
    circle(monkeypatch, "Kir", "Leke")
    session.save_plan("t0", {"kind": "banter", "host": "t0", "with": "Leke", "opener": "Kir",
                             "order": ["Kir", "Leke"], "ts": time.time()})
    session.start("t0", [{"name": "Kir", "line": "sup"}, {"name": "Leke", "line": "darling"}])
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    assert session.view(state.load(), "t0", t0 + 0.5)[1] == "1› sup"



def test_no_new_roll_while_a_session_is_still_playing(monkeypatch):
    circle(monkeypatch, "Snoop", "Çamur")
    session.save_plan("t0", {"kind": "session", "host": "t0", "order": ["Snoop", "Çamur"], "ts": time.time()})
    session.start("t0", [{"name": "Snoop", "line": "a"}, {"name": "Çamur", "line": "b"}])
    assert session.busy(state.load(), time.time())                   # written, not played yet
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    assert session.busy(state.load(), t0 + 3)
    assert not session.busy(state.load(), t0 + 600)
    session.save_plan("t0", {"kind": "banter", "host": "t0", "order": ["Snoop", "Çamur"], "ts": time.time()})
    assert session.pending(state.load(), "t0") is None                 # only rolled joints wait around



def test_turned_down_snoop_smokes_it_himself(monkeypatch):
    circle(monkeypatch, "Snoop", "Bit")
    session.save_plan("t0", {"kind": "refused", "host": "t0", "target": "Bit", "why": "",
                             "order": ["Snoop", "Bit", "Snoop"], "ts": time.time()})
    session.start("t0", [{"name": "Snoop", "emote": "flex", "line": "a"},
                         {"name": "Bit", "emote": "bit-tinfoil", "line": "b"},
                         {"name": "Snoop", "emote": "snoop-rings", "line": "c"}])
    assert [w["emote"] for w in state.load()["session"]["steps"]] == ["joint", "bit-tinfoil", "snoop-rings"]
    assert session.ROLL_S == 8.0


def test_state_keeps_keys_and_memories_it_does_not_know(monkeypatch):
    state.update(lambda s: {**s, "from_the_future": {"x": 1},
                            "history": {"Zort": [{"ts": time.time(), "said": "hi"}]}})
    state.update(lambda s: s)
    loaded = state.load()
    assert loaded["from_the_future"] == {"x": 1}
    assert loaded["history"]["Zort"][0]["said"] == "hi"


def test_mcp_server_hands_a_request_to_the_new_code_when_kuf_changes(monkeypatch):
    from kuf import mcp_server
    stamps = iter([1.0, 1.0, 2.0])                       # start, before msg 1, before msg 2 (updated)
    monkeypatch.setattr(mcp_server, "code_stamp", lambda: next(stamps))
    handed = []
    msgs = [json.dumps({"jsonrpc": "2.0", "id": i, "method": "ping"}) + "\n" for i in (1, 2)]
    stdout = io.StringIO()
    mcp_server.serve(io.StringIO("".join(msgs)), stdout, restart=handed.append)
    assert len(stdout.getvalue().splitlines()) == 1        # old code answered only the first
    assert handed == [msgs[1]]                              # the second goes to the new process


def test_new_process_answers_the_handed_over_request_first(monkeypatch):
    from kuf import mcp_server
    monkeypatch.setenv(mcp_server.PENDING, json.dumps({"jsonrpc": "2.0", "id": 7, "method": "ping"}) + "\n")
    stdout = io.StringIO()
    mcp_server.serve(io.StringIO(""), stdout, restart=lambda raw: None)
    assert json.loads(stdout.getvalue().splitlines()[0])["id"] == 7


def test_resumed_server_tells_the_client_tools_changed(monkeypatch):
    from kuf import mcp_server
    monkeypatch.setenv(mcp_server.RESUMED, "1")
    stdout = io.StringIO()
    mcp_server.serve(io.StringIO(""), stdout, restart=lambda raw: None)
    assert "notifications/tools/list_changed" in stdout.getvalue()
    assert mcp_server.RESUMED not in os.environ


def test_unbuffered_reader_reads_real_fds(tmp_path):
    from kuf import mcp_server
    path = tmp_path / "in"
    path.write_text('{"a": 1}\n{"b": 2}\n')
    with open(path) as handle:
        assert list(mcp_server._lines(handle)) == ['{"a": 1}\n', '{"b": 2}\n']


# ── relationships ──────────────────────────────────────────────────────────────

from kuf import relations  # noqa: E402


def test_relationships_grow_with_vibes_and_shared_joints():
    s = state.load()
    assert relations.stage(relations.get(s, "Snoop", "Çamur"))[0] == "strangers"
    for _ in range(3):
        s = relations.record(s, ["Snoop", "Çamur", "Snoop"], "session", "warm", "the couch is a nation", host="Snoop")
    rel = relations.get(s, "Çamur", "Snoop")                      # order doesn't matter
    assert rel["score"] == 3 * (6 + 8) and rel["talks"] == 3 and rel["joints"] == 3
    assert rel["jokes"] == ["the couch is a nation"]                # no duplicates
    assert relations.stage(rel) == ("buddies", "♥")
    assert "buddies" in relations.describe(s, "Snoop", "Çamur") and "couch is a nation" in relations.describe(s, "Snoop", "Çamur")


def test_hostility_makes_rivals_and_scores_are_capped():
    s = state.load()
    for _ in range(30):
        s = relations.record(s, ["Kir", "Balgam"], "banter", "hostile", None)
    rel = relations.get(s, "Kir", "Balgam")
    assert rel["score"] == -100 and relations.stage(rel) == ("enemies", "⚔")


def test_refusing_stings_only_the_host_pair():
    s = relations.record(state.load(), ["Snoop", "Bit", "Snoop"], "refused", "tense", None, host="Snoop")
    assert relations.get(s, "Snoop", "Bit")["score"] == -3 - 4


def test_friends_take_the_joint_more_often():
    s = relations.record(state.load(), ["Snoop", "Bit"], "banter", None, None)
    s = {**s, "relations": {relations.key("Snoop", "Bit"): {**relations.get(s, "Snoop", "Bit"), "score": 80}}}
    assert relations.joint_odds(s, "Snoop", "Bit", 0.0) == pytest.approx(0.4)
    assert relations.joint_odds(state.load(), "Snoop", "Bit", 0.0) == 0.0


def test_session_tool_records_vibe_and_joke(monkeypatch):
    circle(monkeypatch, "Snoop", "Çamur")
    use_owner(monkeypatch, "t0")
    session.save_plan("t0", {"kind": "banter", "host": "t0", "with": "Çamur", "opener": "Snoop",
                             "order": ["Snoop", "Çamur"], "ts": time.time()})
    mcp({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "kuf_session", "arguments": {
        "steps": [{"name": "Snoop", "line": "a"}, {"name": "Çamur", "line": "b"}],
        "vibe": "teasing", "joke": "vibes-as-a-service"}}})
    rel = relations.get(state.load(), "Snoop", "Çamur")
    assert rel["score"] == 3 and rel["jokes"] == ["vibes-as-a-service"]


def test_bubble_shows_the_relationship_marker():
    out = ANSI.sub("", render.compose("chill", "yo", 0, name="Snoop", marker="♥"))
    assert "─ Snoop ♥ " in out


# ── crowd moments ──────────────────────────────────────────────────────────────

from kuf import crowd  # noqa: E402


def test_every_goblin_has_crowd_reactions_that_exist():
    assert set(crowd.REACTIONS) == set(buddies.VARIANTS)
    for moves in crowd.REACTIONS.values():
        for kind in ("win", "fail"):
            emote, line = moves[kind]
            assert emote in EMOTES and line
            owner_name = looks.OWNER.get(emote)
            assert owner_name is None or moves is crowd.REACTIONS[owner_name]      # only their own moves


def test_passing_tests_make_everyone_react_at_once(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    a, b = state.register("term-a"), state.register("term-b")
    cli.hook_post({"tool_name": "Bash", "tool_input": {"command": "pytest -q"}})
    now = time.time()
    va = cli.current_view(state.load(), "term-a", a, now + 1)
    vb = cli.current_view(state.load(), "term-b", b, now + 1)
    assert (va.emote, va.line) == crowd.REACTIONS[a]["win"]
    assert (vb.emote, vb.line) == crowd.REACTIONS[b]["win"]
    assert crowd.view(state.load(), a, now + crowd.CROWD_S + 1) is None


def test_crowd_moments_have_a_cooldown_and_failures_count_too():
    assert crowd.trigger("fail", "x", now=1000.0)
    assert not crowd.trigger("win", "x", now=1000.0 + 30)
    assert crowd.trigger("win", "x", now=1000.0 + crowd.COOLDOWN_S + 1)


def test_a_failed_non_test_command_is_not_a_crowd_moment():
    cli.hook_fail({"tool_name": "Bash", "tool_input": {"command": "ls /nope"}})
    assert state.load().get("crowd") is None


# ── spotlight moments ──────────────────────────────────────────────────────────

from kuf import spotlight  # noqa: E402


@pytest.mark.parametrize("command,hour,kind", [
    ("git push origin main", 14, "push"), ("git push -f", 14, "force-push"),
    ("git push --force-with-lease", 14, "force-push"), ("git commit -m x", 14, "commit"),
    ("git commit -m x", 3, "night-commit"), ("git reset --hard HEAD~1", 14, "reset"),
    ("git rebase main", 14, "merge"), ("rm -rf build", 14, "rm"), ("rm -fr x", 14, "rm"),
    ("npm install react", 14, "install"), ("pip install requests", 14, "install"),
    ("git status", 14, None), ("rm file.txt", 14, None),
])
def test_commands_find_their_spotlight(command, hour, kind):
    assert spotlight.classify(command, hour) == kind


def test_every_star_uses_his_own_or_shared_moves():
    for kind, (star, emote, line) in spotlight.STARS.items():
        assert star in buddies.VARIANTS and emote in EMOTES and line
        assert looks.OWNER.get(emote, star) == star
        assert spotlight.STAND_IN[kind][0] in EMOTES


def test_the_star_reacts_wherever_he_is_else_the_local_goblin(monkeypatch):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    circle(monkeypatch, "Pas", "Snoop")
    assert spotlight.trigger("push", "t1")
    now = time.time()
    s = state.load()
    assert spotlight.view(s, "t0", "Pas", now + 1)[1].startswith("PUSHED")
    assert spotlight.view(s, "t1", "Snoop", now + 1) is None            # Pas has it covered
    assert spotlight.trigger("reset", "t1", now=now + 1)                # Leş isn't open
    s = state.load()
    assert spotlight.view(s, "t1", "Snoop", now + 2) == spotlight.STAND_IN["reset"]
    assert not spotlight.trigger("reset", "t1", now=now + 5)            # cooldown


def test_post_hook_fires_the_spotlight(monkeypatch):
    monkeypatch.setattr(spotlight, "classify", lambda cmd, hour=None: "push")
    cli.hook_post({"tool_name": "Bash", "tool_input": {"command": "git push"}})
    assert state.load()["spotlight"]["kind"] == "push"


# ── stats ──────────────────────────────────────────────────────────────────────

from kuf import stats  # noqa: E402


def test_stats_count_every_kind_of_conversation():
    s = state.load()
    s = stats.after_session(s, "session", ["Snoop", "Çamur", "Snoop"], "Snoop")
    s = stats.after_session(s, "refused", ["Snoop", "Bit", "Snoop"], "Snoop")
    s = stats.after_session(s, "banter", ["Kir", "Leke"], "Kir")
    assert s["stats"]["Snoop"] == {"joints": 1, "turned_down": 1}
    assert s["stats"]["Bit"] == {"refused": 1} and s["stats"]["Kir"] == {"chats": 1}
    s = relations.record(s, ["Snoop", "Çamur"], "session", "warm", "every puff is a signature", host="Snoop")
    out = stats.report(s, "Snoop")
    assert "Snoop (this terminal): 1 joint · 0 chats · got turned down 1×" in out
    assert "Bit: 0 joints · 0 chats · said no 1×" in out
    assert 'Çamur: friendly +14 · 1 hangout · 1 joint · "every puff is a signature"' in out
    assert "top smoker: Çamur, Snoop (1)" in out and "most likely to say no: Bit (1)" in out


def test_empty_stats_point_to_the_joint():
    assert "!joint" in stats.report(state.load())


def test_goblin_stats_shortcut(monkeypatch, capsys):
    cli.main(["be", "stats"])
    assert "couch stats" in capsys.readouterr().out


def test_spotlight_credits_the_star(monkeypatch):
    circle(monkeypatch, "Pas", "Snoop")
    spotlight.trigger("push", "t1")
    assert state.load()["stats"]["Pas"]["spotlights"] == 1


def test_a_participants_own_new_line_only_interrupts_him_for_a_moment(monkeypatch):
    circle(monkeypatch, "Snoop", "Çamur")
    session.save_plan("t0", {"kind": "banter", "host": "t0", "with": "Çamur", "opener": "Snoop",
                             "order": ["Snoop", "Çamur", "Snoop", "Çamur"], "ts": time.time()})
    session.start("t0", [{"name": n, "line": f"l{i}"} for i, n in enumerate(["Snoop", "Çamur", "Snoop", "Çamur"])])
    session.anchor("t0")
    time.sleep(0.01)
    state.set_reaction("t1", "chill", "working over here", source="claude")   # Çamur's own Claude
    said = state.load()["reactions"]["t1"]["ts"]
    s = state.load()
    assert session.view(s, "t1", said + 1) is None                             # his own line shows
    assert session.view(s, "t0", said + 1) is not None                          # Snoop keeps going
    assert session.view(s, "t1", said + session.INTERRUPT_S + 1) is not None   # and he's back


def test_goblin_rnd_picks_someone_else_free_first(monkeypatch, capsys):
    monkeypatch.setattr(state, "is_alive", lambda owner: True)
    monkeypatch.delenv("KUF_GOBLIN", raising=False)
    cli.main(["be", "snoop"])
    state.register("term-b")
    other = state.load()["buddies"]["term-b"]["name"]
    for _ in range(20):
        picked = cli.random_goblin("term-a")
        assert picked not in ("Snoop", other)
    cli.main(["be", "rnd"])
    now = state.load()["buddies"]["term-a"]["name"]
    assert now != "Snoop" and f"this terminal is now {now}" in capsys.readouterr().out



def test_every_character_has_a_real_chance_either_way():
    for name in buddies.VARIANTS:
        if name != session.HOST:
            assert 0.0 < looks.accepts_joint(name) < 1.0, name
    assert looks.accepts_joint("Çamur") > looks.accepts_joint("Kir") > looks.accepts_joint("Bit")


def test_dice_line_shows_each_roll():
    line = session.dice_line({"dice": {"Kir": {"roll": 34, "needs": 30, "yes": False},
                                       "Çamur": {"roll": 12, "needs": 95, "yes": True}}})
    assert line == "🎲 Kir 34 (needs ≤30) → no · Çamur 12 (needs ≤95) → takes it"


# ── clock & seasons ────────────────────────────────────────────────────────────

from datetime import datetime as _dt  # noqa: E402

from kuf import clock  # noqa: E402


@pytest.mark.parametrize("when,expected", [
    (_dt(2026, 1, 5, 8), ["monday", "morning", "winter"]),          # a Monday morning in January
    (_dt(2026, 7, 11, 20), ["weekend", "evening", "summer"]),       # a Saturday evening in July
    (_dt(2026, 10, 14, 14), ["autumn"]),                            # a Wednesday afternoon in October
    (_dt(2026, 4, 1, 3), ["spring"]),                               # night: just the season
])
def test_the_moment_picks_its_pools(when, expected):
    assert clock.pools(clock.moment(when)) == expected


def test_clock_lines_format_and_use_real_emotes():
    for lines in clock.POOLS.values():
        for emote, template in lines:
            assert emote in EMOTES and "{" not in template.format(user="ege")
    assert "Monday morning in winter" in clock.describe(clock.moment(_dt(2026, 1, 5, 8)))


def test_a_borrowed_clock_move_falls_back_for_others():
    template = next(t for e, t in clock.POOLS["winter"] if e == "kuf-burrito")
    assert cli.idle_emote(template, "comfy", "1", "Küf") == "kuf-burrito"
    assert cli.idle_emote(template, "comfy", "1", "Snoop") != "kuf-burrito"


# ── break reminders ────────────────────────────────────────────────────────────

from kuf import breaks  # noqa: E402


def test_break_reminder_after_two_hours_nonstop_then_quiet_for_a_while():
    t = 1_000_000.0
    for minute in range(0, 120, 10):                        # prompts every 10 min for 2 hours
        assert not breaks.on_prompt("term-a", now=t + minute * 60)
    assert breaks.on_prompt("term-a", now=t + 120 * 60)    # 2h mark: nag
    for minute in range(130, 170, 10):                      # keeps going, no pause
        assert not breaks.on_prompt("term-a", now=t + minute * 60)   # not again so soon
    assert breaks.on_prompt("term-a", now=t + 170 * 60)    # 50 min after the last nag


def test_a_real_pause_resets_the_streak():
    t = 2_000_000.0
    for minute in range(0, 110, 10):
        breaks.on_prompt("term-a", now=t + minute * 60)
    assert not breaks.on_prompt("term-a", now=t + 130 * 60)     # 20 min gap: that was a break
    assert breaks.streak(state.load(), t + 130 * 60) == 0.0


def test_the_nag_shows_in_that_terminal_in_his_voice(monkeypatch):
    name = state.register("term-a")
    t = time.time()
    state.update(lambda s: {**s, "nag": {"by": "term-a", "ts": t}})
    view = cli.current_view(state.load(), "term-a", name, t + 5)
    assert (view.emote, view.line) == breaks.NAG[name]
    assert breaks.view(state.load(), "term-a", name, t + breaks.SHOW_S + 1) is None
    assert all(e in EMOTES for e, _ in breaks.NAG.values())
    assert set(breaks.NAG) == set(buddies.VARIANTS)


def test_too_long_lines_are_sent_back_not_cut():
    state.register("term-a")
    long_line = "it's all shipped, boss... the whole couch universe, one commit. i'd light one to celebrate but you're sick, so i'll smoke yours"
    out = react(long_line)
    assert out["isError"] and "too long" in out["content"][0]["text"]
    assert "term-a" not in state.load()["reactions"]
    assert not react("it's all shipped, boss. one commit. i'll smoke yours since you're sick")["isError"]


def test_host_never_wears_his_neighbors_opening_line(monkeypatch):
    circle(monkeypatch, "Snoop", "Kir")
    session.save_plan("t0", {"kind": "banter", "host": "t0", "with": "Kir", "opener": "Kir",
                             "order": ["Kir", "Snoop", "Kir", "Snoop"], "ts": time.time()})
    session.start("t0", [{"name": "Kir", "emote": "kir-10x", "line": "kir opens"},
                         {"name": "Snoop", "emote": "snoop-roll", "line": "snoop answers"},
                         {"name": "Kir", "line": "k2"}, {"name": "Snoop", "line": "s2"}])
    mine = state.load()["reactions"]["t0"]
    assert (mine["emote"], mine["line"]) == ("snoop-roll", "snoop answers")
    session.anchor("t0")
    t0 = state.load()["session"]["anchor"]
    assert session.view(state.load(), "t0", t0 + 1)[1] == "*listening*"     # no joint in a chat



def test_camur_and_kuf_roll_their_own_now_and_then(monkeypatch):
    s = circle(monkeypatch, "Çamur", "Kir")
    planned = session.plan(s, "t0", None, Rolls(0.01, 0.0))
    assert planned["host_name"] == "Çamur" and planned["order"][0] == "Çamur"
    assert "Çamur sparks one up" in session.note(planned)
    refused = session.plan(s, "t0", None, Rolls(0.01, 0.99))
    assert refused["order"] == ["Çamur", "Kir", "Çamur", "Kir", "Çamur"]
    session.save_plan("t0", refused)
    session.start("t0", [{"name": n, "emote": "joint", "line": f"l{i}"} for i, n in enumerate(refused["order"])])
    emotes_used = [w["emote"] for w in state.load()["session"]["steps"]]
    assert emotes_used == ["joint", "nope", "joint", "nope", "joint"]          # Çamur smokes it alone
    assert session.HOSTS["Snoop"] > session.HOSTS["Çamur"] > session.HOSTS["Küf"]


def test_joint_command_works_for_every_roller(monkeypatch, capsys):
    monkeypatch.delenv("KUF_GOBLIN", raising=False)
    cli.main(["be", "kir"])
    cli.main(["joint"])
    assert "only Snoop, Çamur, Küf roll one" in capsys.readouterr().out
    cli.main(["be", "camur"])
    cli.main(["joint"])
    assert "Çamur passes it" in capsys.readouterr().out
