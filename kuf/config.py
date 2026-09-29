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


def user_name() -> str:
    return load()["name"]
