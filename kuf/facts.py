"""Cheap facts about the user's machine and day, for the goblins to gossip about.

Everything is best-effort and local: missing tools or files just mean fewer facts.
Only app names are read from the window manager, never window titles.
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .screen import niri_windows

GOSSIP_APPS = {"steam": "steam", "discord": "discord", "spotify": "spotify",
               "brave-browser": "brave", "firefox": "firefox", "chromium": "chrome",
               "libreoffice-writer": "libreoffice", "org.telegram.desktop": "telegram",
               "obsidian": "obsidian", "code": "vs code", "zed": "zed"}


def _read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def battery() -> dict:
    for bat in sorted(Path("/sys/class/power_supply").glob("BAT*")):
        level = _read(bat / "capacity")
        if level.isdigit():
            return {"battery": int(level), "charging": _read(bat / "status") == "Charging"}
    return {}


def temperature() -> dict:
    temps = [int(t) // 1000 for z in Path("/sys/class/thermal").glob("thermal_zone*")
             if (t := _read(z / "temp")).lstrip("-").isdigit()]
    return {"temp": max(temps)} if temps else {}


def uptime() -> dict:
    raw = _read(Path("/proc/uptime")).split()
    if not raw:
        return {}
    hours = int(float(raw[0]) // 3600)
    return {"uptime": f"{hours // 24} days" if hours >= 48 else f"{hours} hours"}


def memory() -> dict:
    info = {}
    for line in _read(Path("/proc/meminfo")).splitlines():
        key, _, value = line.partition(":")
        info[key] = int(value.split()[0]) if value.split() else 0
    if not info.get("MemTotal"):
        return {}
    return {"ram": round(100 * (1 - info.get("MemAvailable", 0) / info["MemTotal"]))}


def music() -> dict:
    if not shutil.which("playerctl"):
        return {}
    try:
        out = subprocess.run(["playerctl", "metadata", "--format", "{{status}}|{{artist}}|{{title}}"],
                             capture_output=True, text=True, timeout=1).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return {}
    status, _, rest = out.partition("|")
    artist, _, title = rest.partition("|")
    if status != "Playing" or not title:
        return {}
    return {"song": f"{artist} - {title}" if artist else title}


def apps() -> dict:
    found = sorted({GOSSIP_APPS[w.get("app_id", "")] for w in niri_windows()
                    if w.get("app_id") in GOSSIP_APPS})
    return {"apps": found} if found else {}


def clock() -> dict:
    now = datetime.now()
    return {"hour": now.hour, "weekday": now.strftime("%A")}


def collect() -> dict:
    facts: dict = {}
    for source in (clock, battery, temperature, uptime, memory, music, apps):
        try:
            facts = {**facts, **source()}
        except Exception:  # one broken sensor shouldn't kill the gossip
            continue
    return facts
