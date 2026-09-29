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


def niri_windows() -> list[dict]:
    if not os.environ.get("NIRI_SOCKET") or not shutil.which("niri"):
        return []
    try:
        out = subprocess.run(["niri", "msg", "-j", "windows"], capture_output=True,
                             text=True, timeout=1).stdout
        windows = json.loads(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return []
    return windows if isinstance(windows, list) else []


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
    labels = {}
    for other in others:
        where = direction(mine, window_of(other, windows))
        project = project_of(other)
        labels[other] = f"{where} ({project})" if where else f"in {project}"
    return labels
