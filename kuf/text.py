"""Terminal column math shared by the renderer and the art kit."""

import unicodedata
from functools import lru_cache


@lru_cache(maxsize=None)
def char_width(ch: str) -> int:
    """0 for combining marks, 2 for wide/fullwidth characters, else 1."""
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def width(text: str) -> int:
    return sum(char_width(ch) for ch in text)


def graphemes(text: str) -> list[str]:
    """Split into base characters with their combining marks attached."""
    clusters: list[str] = []
    for ch in text:
        if clusters and char_width(ch) == 0:
            clusters[-1] += ch
        else:
            clusters.append(ch)
    return clusters
