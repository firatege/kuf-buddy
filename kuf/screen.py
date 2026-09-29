"""Where is each terminal on screen? Uses niri's IPC when available, so a buddy can
say "the dude on the right" about the split next to it. Everything degrades to
project names when niri isn't running."""

import json
import os
import shutil
import subprocess
from pathlib import Path

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


def window_of(owner: str, windows: list[dict]) -> dict | None:
    """The niri window whose process is an ancestor of the Claude process `owner`."""
    if not owner.isdigit():
        return None
    by_pid = {w.get("pid"): w for w in windows}
    pid = int(owner)
    for _ in range(MAX_DEPTH):
        if pid in by_pid:
            return by_pid[pid]
        found = parent_and_name(pid)
        if found is None or found[0] <= 1:
            return None
        pid = found[0]
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
