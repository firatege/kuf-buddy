"""Where is each terminal on screen? Uses niri's IPC when available, so a buddy can
say "the dude on the right" about the split next to it. Everything degrades to
project names when niri isn't running."""

import json
import os
import shutil
import subprocess
from pathlib import Path

from . import state
from .owner import parent_and_name

MAX_DEPTH = 8


WIDTH_SLACK = 24   # gaps between columns aren't in tile sizes


def _niri(what: str):
    if not os.environ.get("NIRI_SOCKET") or not shutil.which("niri"):
        return None
    try:
        out = subprocess.run(["niri", "msg", "-j", what], capture_output=True,
                             text=True, timeout=1).stdout
        return json.loads(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def niri_windows() -> list[dict]:
    windows = _niri("windows")
    return windows if isinstance(windows, list) else []


def visible_window_ids(windows: list[dict], workspaces: list[dict], outputs: dict) -> set[int]:
    """Best guess at which windows are actually on screen.

    niri doesn't report the view offset, so for every workspace that's showing on a
    monitor, start at its active window's column and grow left/right while the
    columns still fit in the monitor's width.
    """
    visible: set[int] = set()
    for ws in workspaces:
        if not ws.get("is_active"):
            continue
        width = ((outputs.get(ws.get("output")) or {}).get("logical") or {}).get("width", 0)
        on_ws = [w for w in windows if w.get("workspace_id") == ws.get("id")
                 and (w.get("layout") or {}).get("pos_in_scrolling_layout")]
        if not on_ws or not width:
            continue
        columns: dict[int, list[dict]] = {}
        for w in on_ws:
            columns.setdefault(w["layout"]["pos_in_scrolling_layout"][0], []).append(w)
        col_width = {c: max(w["layout"]["tile_size"][0] for w in ws_) for c, ws_ in columns.items()}
        anchor = next((w for w in on_ws if w.get("id") == ws.get("active_window_id")), on_ws[0])
        left = right = anchor["layout"]["pos_in_scrolling_layout"][0]
        used = col_width[left]
        grew = True
        while grew:
            grew = False
            for candidate in (right + 1, left - 1):
                if candidate in col_width and used + col_width[candidate] <= width + WIDTH_SLACK:
                    used += col_width[candidate]
                    left, right = min(left, candidate), max(right, candidate)
                    grew = True
        visible |= {w["id"] for c in range(left, right + 1) for w in columns.get(c, [])}
    return visible


def visible_owners(owners: list[str]) -> set[str] | None:
    """Owners whose terminal is on screen right now; None when we can't tell."""
    windows, workspaces, outputs = niri_windows(), _niri("workspaces"), _niri("outputs")
    if not windows or not isinstance(workspaces, list) or not isinstance(outputs, dict):
        return None
    shown = visible_window_ids(windows, workspaces, outputs)
    return {o for o in owners if (window_of(o, windows) or {}).get("id") in shown}


def window_of(owner: str, windows: list[dict], via: str | None = None) -> dict | None:
    """The niri window whose process is an ancestor of the Claude process `owner`
    (or of the process it adopted the window from, see adopt_window)."""
    start = via or state.load()["buddies"].get(owner, {}).get("via") or owner
    if not start.isdigit():
        return None
    by_pid = {w.get("pid"): w for w in windows}
    found = _walk_up(int(start), by_pid)
    if found or via:
        return found
    client = attach_client(owner)
    return _walk_up(client, by_pid) if client else None


def _walk_up(pid: int, by_pid: dict) -> dict | None:
    for _ in range(MAX_DEPTH):
        if pid in by_pid:
            return by_pid[pid]
        found = parent_and_name(pid)
        if found is None or found[0] <= 1:
            return None
        pid = found[0]
    return None


def _socket_inodes(pid: str) -> set[str]:
    inodes = set()
    try:
        for fd in Path(f"/proc/{pid}/fd").iterdir():
            try:
                target = os.readlink(fd)
            except OSError:
                continue
            if target.startswith("socket:["):
                inodes.add(target[8:-1])
    except OSError:
        pass
    return inodes


def attach_client(owner: str) -> int | None:
    """A session living in Claude Code's background daemon is drawn by a
    `claude attach <id>` process in some terminal; <id> is the name of the daemon
    session's rv/<id>.sock. Find that terminal-side process."""
    if not owner.isdigit():
        return None
    inodes = _socket_inodes(owner)
    session_id = None
    try:
        for line in Path("/proc/net/unix").read_text().splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 8 and parts[6] in inodes and "/rv/" in parts[7]:
                session_id = Path(parts[7]).stem
                break
    except OSError:
        return None
    if not session_id:
        return None
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            args = (proc / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if b"attach" in args and session_id.encode() in args:
            return int(proc.name)
    return None


def project_of(owner: str) -> str:
    try:
        cwd = Path(os.readlink(f"/proc/{owner}/cwd"))
    except (OSError, ValueError):
        return "somewhere"
    return "~" if cwd == Path.home() else cwd.name


def direction(mine: dict | None, theirs: dict | None) -> str:
    """Human description of where `theirs` sits relative to `mine`."""
    if not mine or not theirs:
        return ""
    if mine.get("workspace_id") != theirs.get("workspace_id"):
        return "on another workspace"
    try:
        my_col, my_row = mine["layout"]["pos_in_scrolling_layout"]
        their_col, their_row = theirs["layout"]["pos_in_scrolling_layout"]
    except (KeyError, TypeError, ValueError):
        return "on this screen"
    gap = their_col - my_col
    if gap == 0:
        return "right above you" if their_row < my_row else "right below you"
    side = "right" if gap > 0 else "left"
    return f"on the {side}" if abs(gap) == 1 else f"way off to the {side}"


def describe_neighbors(me: str, others: list[str]) -> dict[str, str]:
    """owner -> 'on the right (ced-demo)' style labels."""
    windows = niri_windows()
    mine = window_of(me, windows)
    on_screen = visible_owners(others)
    labels = {}
    for other in others:
        where = direction(mine, window_of(other, windows))
        project = project_of(other)
        label = f"{where} ({project})" if where else f"in {project}"
        if on_screen is not None and other not in on_screen:
            label += ", off screen"
        labels[other] = label
    return labels


def side_of(me: str, other: str) -> str | None:
    """'left' or 'right': which way to turn to face `other`. None if we can't tell."""
    windows = niri_windows()
    mine, theirs = window_of(me, windows), window_of(other, windows)
    if not mine or not theirs or mine.get("workspace_id") != theirs.get("workspace_id"):
        return None
    try:
        gap = (theirs["layout"]["pos_in_scrolling_layout"][0]
               - mine["layout"]["pos_in_scrolling_layout"][0])
    except (KeyError, TypeError, IndexError):
        return None
    return None if gap == 0 else ("right" if gap > 0 else "left")


def adopt_window(owner: str) -> str | None:
    """A background-daemon session has no window of its own. Its terminal still holds
    the old client process, which went ghost when the daemon took over drawing; hand
    that window to the windowless session. Returns the adopted ghost, if any."""
    windows = niri_windows()
    if not windows or window_of(owner, windows):
        return None
    s = state.load()
    taken = {w["id"] for o, b in s["buddies"].items()
             if o != owner and not state.is_ghost(b) and (w := window_of(o, windows))}
    ghosts = sorted(((state.last_seen(b), o) for o, b in s["buddies"].items()
                     if o != owner and state.is_ghost(b)), reverse=True)
    for _, ghost in ghosts:
        window = window_of(ghost, windows, via=ghost)
        if window and window["id"] not in taken:
            state.adopt(owner, ghost)
            return ghost
    return None
