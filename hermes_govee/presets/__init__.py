"""Presets for Govee lights — colors and ambiences."""

from hermes_govee.presets.ambiences import (
    ENERGY,
    FOCUS,
    MEDITATION,
    MOVIE,
    NIGHT,
    PARTY,
    PresetAmbience,
    READING,
    RELAX,
)
from hermes_govee.presets.colors import (
    BLUE,
    COOL_WHITE,
    CYAN,
    DIM_RED,
    GREEN,
    MAGENTA,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    SOFT_BLUE,
    WARM_ORANGE,
    WARM_WHITE,
    WHITE,
    YELLOW,
)

__all__ = [
    # Colors
    "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA",
    "WHITE", "WARM_WHITE", "COOL_WHITE", "ORANGE", "PINK", "PURPLE",
    "WARM_ORANGE", "DIM_RED", "SOFT_BLUE",
    # Ambiences
    "PresetAmbience",
    "FOCUS", "RELAX", "PARTY", "NIGHT", "READING",
    "ENERGY", "MOVIE", "MEDITATION",
]
