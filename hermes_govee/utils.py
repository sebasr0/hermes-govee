"""Color utility helpers."""

from typing import Tuple


def rgb_to_tuple(value: Tuple[int, int, int] | dict) -> Tuple[int, int, int]:
    """Normalize an RGB value to a (r, g, b) tuple."""
    if isinstance(value, tuple):
        return value
    if isinstance(value, dict):
        return (int(value["r"]), int(value["g"]), int(value["b"]))
    raise ValueError(f"Invalid color value: {value}")
