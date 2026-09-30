"""User settings in ~/.claude/kuf/config.json (e.g. what the goblins call you)."""

import json

from .state import state_dir

DEFAULTS = {"name": "boss"}


def config_file():
    return state_dir() / "config.json"


def load() -> dict:
    try:
        data = json.loads(config_file().read_text())
    except (OSError, ValueError):
        return dict(DEFAULTS)
    return {**DEFAULTS, **data} if isinstance(data, dict) else dict(DEFAULTS)


def set_value(key: str, value: str) -> dict:
    updated = {**load(), key: value}
    state_dir().mkdir(parents=True, exist_ok=True)
    config_file().write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n")
    return updated


LANGS = ("en", "tr")


def lang() -> str:
    """Which language the goblins speak: `kuf config lang tr` for Turkish."""
    chosen = str(load().get("lang", "en")).lower()
    return chosen if chosen in LANGS else "en"


def turkish() -> bool:
    return lang() == "tr"


def user_name() -> str:
    """What the goblins call you; the default "boss" becomes "patron" in Turkish."""
    name = load()["name"]
    return "patron" if name == DEFAULTS["name"] and turkish() else name
