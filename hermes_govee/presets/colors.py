"""Preset color constants for Govee lights."""

from typing import Tuple

# Primary / pure colors
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 0)
CYAN: Tuple[int, int, int] = (0, 255, 255)
MAGENTA: Tuple[int, int, int] = (255, 0, 255)
WHITE: Tuple[int, int, int] = (255, 255, 255)

# White variants
WARM_WHITE: Tuple[int, int, int] = (255, 223, 186)
COOL_WHITE: Tuple[int, int, int] = (240, 247, 255)

# Tinted colors
ORANGE: Tuple[int, int, int] = (255, 165, 0)
PINK: Tuple[int, int, int] = (255, 105, 180)
PURPLE: Tuple[int, int, int] = (128, 0, 128)

# Ambience support colors
WARM_ORANGE: Tuple[int, int, int] = (255, 200, 100)
DIM_RED: Tuple[int, int, int] = (80, 0, 0)
SOFT_BLUE: Tuple[int, int, int] = (100, 150, 255)

__all__ = [
    "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE",
    "WARM_WHITE", "COOL_WHITE", "ORANGE", "PINK", "PURPLE",
    "WARM_ORANGE", "DIM_RED", "SOFT_BLUE",
]
