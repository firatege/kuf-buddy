"""Which Claude Code instance (= which terminal) are we running under?

Every Claude Code process spawns its own MCP server, hooks and status line, so the
PID of the nearest `claude` ancestor is a key they all agree on — and it keeps each
terminal's Küf separate.
"""

import os
import subprocess
from functools import lru_cache
from pathlib import Path

MAX_DEPTH = 12


def parent_and_name(pid: int) -> tuple[int, str] | None:
    stat = Path(f"/proc/{pid}/stat")
    if stat.exists():
        try:
            raw = stat.read_text()
        except OSError:
            return None
        # "pid (comm) state ppid ..." — comm may contain spaces, so split on the last ')'
        name = raw[raw.index("(") + 1: raw.rindex(")")]
        ppid = int(raw[raw.rindex(")") + 2:].split()[1])
        return ppid, name
    try:  # macOS / BSD
        out = subprocess.run(["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=2).stdout.split(None, 1)
    except (OSError, subprocess.SubprocessError):
        return None
    return (int(out[0]), os.path.basename(out[1].strip())) if len(out) == 2 else None


def _looks_like_claude(pid: int, name: str) -> bool:
    if name == "claude":
        return True
    try:
        return "/claude/versions/" in os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return False


@lru_cache(maxsize=1)
def owner_id() -> str:
    for var in ("KUF_OWNER", "CLAUDE_PID"):
        if os.environ.get(var):
            return os.environ[var]
    pid = os.getppid()
    for _ in range(MAX_DEPTH):
        if pid <= 1:
            break
        found = parent_and_name(pid)
        if found is None:
            break
        ppid, name = found
        if _looks_like_claude(pid, name):
            return str(pid)
        pid = ppid
    return "global"


def is_alive(owner: str) -> bool:
    if not owner.isdigit():
        return True
    try:
        os.kill(int(owner), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
