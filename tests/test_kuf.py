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
    monkeypatch.setattr(owner, "_parent_and_name", lambda pid: tree.get(pid))
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
