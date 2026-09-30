"""Per-goblin looks: each goblin's own animations, habits and how he takes a joint.

One module per goblin. Signature emotes are named "<slug>-<move>" and belong to
that goblin only; the shared ones live in `shared`.
"""

from importlib import import_module

from . import shared

SLUGS = ["kuf", "pas", "les", "sumuk", "kir", "camur", "balgam", "bit", "leke", "kabuk", "snoop"]
MIN_SIGNATURES = 5

MODULES = {m.NAME: m for m in (import_module(f".{slug}", __name__) for slug in SLUGS)}
SLUG_OF = {m.NAME: slug for slug, m in zip(SLUGS, MODULES.values())}

SIGNATURES: dict[str, dict] = {k: v for m in MODULES.values() for k, v in m.EMOTES.items()}
OWNER: dict[str, str] = {k: m.NAME for m in MODULES.values() for k in m.EMOTES}


def habits(name: str) -> list[str]:
    """What he does when nobody's talking to him: his own moves twice as often as shared ones."""
    module = MODULES.get(name)
    if module is None:
        return []
    own = list(module.EMOTES)
    return module.HABITS + own * 2


def signatures(name: str) -> list[str]:
    module = MODULES.get(name)
    return sorted(module.EMOTES) if module else []


def accepts_joint(name: str) -> float:
    module = MODULES.get(name)
    return module.ACCEPTS_JOINT if module else 0.0


def refusal(name: str) -> str:
    module = MODULES.get(name)
    return module.REFUSAL if module else ""


def can_use(name: str, emote: str) -> bool:
    """Shared emotes are for everyone; a signature only for its owner."""
    return emote not in OWNER or OWNER[emote] == name
