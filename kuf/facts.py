"""Cheap facts about what the user is up to, fed to Claude so the goblins can talk
about it.

Everything is best-effort: missing tools or files just mean fewer facts. From the
window manager only app names are read, plus the Discord window title (it names the
DM or channel open). Facts go into Claude's context, so they leave the machine with
the prompt.
"""

import json
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from .screen import niri_windows

CACHE_S = 15           # the status line runs every second; sensors don't need to
BROWSERS = {"brave-browser", "firefox", "chromium", "google-chrome"}
BROWSER_SUFFIX = re.compile(r" [-—] (Brave|Mozilla Firefox|Chromium|Google Chrome)$")
YOUTUBE = re.compile(r"^(?:\(\d+\) )?(.+?) - YouTube$")
UNREAD = re.compile(r"^\((\d+)\) WhatsApp$")
# Only these sites are recognized; other tab titles are never read.
SITES = {"WhatsApp": "whatsapp", "Sim Companies": "sim companies", "GitHub": "github",
         "Reddit": "reddit", "Twitch": "twitch", "Gmail": "gmail", "ChatGPT": "chatgpt"}
GITHUB_REPO = re.compile(r"^[\w.-]+/[\w.-]+(: |$)|^Your Stars$")

GOSSIP_APPS = {"steam": "steam", "discord": "discord", "vesktop": "discord", "spotify": "spotify",
               "brave-browser": "brave", "firefox": "firefox", "chromium": "chrome",
               "libreoffice-writer": "libreoffice", "org.telegram.desktop": "telegram",
               "obsidian": "obsidian", "code": "vs code", "zed": "zed"}


def _read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


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
    """What Spotify is playing (browser players are YouTube's business, see tabs())."""
    if not shutil.which("playerctl"):
        return {}
    try:
        out = subprocess.run(["playerctl", "-p", "spotify", "metadata", "--format",
                              "{{status}}|{{artist}}|{{title}}"],
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


DISCORD_SUFFIX = " - Discord"
DISCORD_IDLE = {"Discord", "Friends", "Friends - Discord", ""}


def discord_chat(title: str) -> str | None:
    """"@Piroz - Discord" -> "@Piroz"; "#general | KAINAT - Discord" -> "KAINAT".

    For a server only its name is kept: the open channel says nothing about where
    the user actually is (e.g. which voice room)."""
    chat = title.removesuffix(DISCORD_SUFFIX).strip()
    if chat in DISCORD_IDLE or chat == title.strip():
        return None
    channel, _, server = chat.partition(" | ")
    return server or channel


def discord() -> dict:
    for w in niri_windows():
        if GOSSIP_APPS.get(w.get("app_id", "")) == "discord":
            chat = discord_chat(w.get("title") or "")
            if chat:
                return {"discord_chat": chat}
    return {}


def site_of(title: str) -> dict:
    """Facts from one browser tab title; unknown sites give nothing."""
    tab = BROWSER_SUFFIX.sub("", title).strip()
    video = YOUTUBE.match(tab)
    if video:
        return {"youtube": video.group(1)}
    unread = UNREAD.match(tab)
    if unread:
        return {"site": "whatsapp", "whatsapp_unread": int(unread.group(1))}
    if GITHUB_REPO.match(tab):
        return {"site": "github"}
    return next(({"site": name} for key, name in SITES.items() if key in tab), {})


def tabs() -> dict:
    found: dict = {"sites": []}
    for w in niri_windows():
        if w.get("app_id") in BROWSERS:
            info = site_of(w.get("title") or "")
            site = info.pop("site", None)
            found = {**found, **info, "sites": found["sites"] + ([site] if site else [])}
    sites = sorted(set(found.pop("sites")))
    return {**found, "sites": sites} if sites else found


def clock() -> dict:
    now = datetime.now()
    return {"hour": now.hour, "weekday": now.strftime("%A")}


def collect() -> dict:
    facts: dict = {}
    for source in (clock, uptime, memory, music, apps, discord, tabs):
        try:
            facts = {**facts, **source()}
        except Exception:  # one broken sensor shouldn't kill the rest
            continue
    return facts


def cached(path: Path, now: float | None = None) -> dict:
    """collect(), at most once per CACHE_S across all terminals."""
    now = time.time() if now is None else now
    try:
        saved = json.loads(path.read_text())
        if now - saved["ts"] < CACHE_S:
            return saved["facts"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    fresh = collect()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"ts": now, "facts": fresh}, ensure_ascii=False))
        tmp.replace(path)
    except OSError:
        pass
    return fresh


def describe(facts: dict) -> str:
    """One line of what the user is up to, for Claude."""
    parts = []
    if facts.get("song"):
        parts.append(f"listening to {facts['song']}")
    if facts.get("discord_chat"):
        chat = facts["discord_chat"]
        parts.append(f"on discord with {chat}" if chat.startswith("@")
                     else f"hanging out on the {chat} discord server")
    if facts.get("youtube"):
        parts.append(f"watching \"{facts['youtube']}\" on youtube")
    if facts.get("sites"):
        unread = facts.get("whatsapp_unread")
        extra = f" ({unread} unread on whatsapp)" if unread else ""
        parts.append(f"browser tabs: {', '.join(facts['sites'])}{extra}")
    if facts.get("apps"):
        parts.append(f"open apps: {', '.join(facts['apps'])}")
    if "hour" in facts:
        parts.append(f"it's {facts['weekday']} {facts['hour']:02d}:00")
    if facts.get("ram"):
        parts.append(f"ram {facts['ram']}%")
    if facts.get("uptime"):
        parts.append(f"up {facts['uptime']}")
    return "; ".join(parts)
