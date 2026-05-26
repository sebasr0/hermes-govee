"""Preset ambience settings for Govee lights.

Each ambience is a ``PresetAmbience`` dataclass with a color, brightness, and optional Kelvin temperature.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from hermes_govee.presets.colors import (
    COOL_WHITE,
    DIM_RED,
    MAGENTA,
    SOFT_BLUE,
    WARM_ORANGE,
    WARM_WHITE,
    YELLOW,
)


@dataclass(frozen=True)
class PresetAmbience:
    """A preset ambience: color + brightness + optional Kelvin temperature."""

    color: Tuple[int, int, int]
    brightness: int
    kelvin: Optional[int] = None


# --- Ambiences ---

FOCUS = PresetAmbience(color=COOL_WHITE, brightness=100, kelvin=6500)
"""Cool white at full brightness — ideal for work and study."""

RELAX = PresetAmbience(color=WARM_WHITE, brightness=40, kelvin=2700)
"""Warm dim light for evening rest."""

PARTY = PresetAmbience(color=MAGENTA, brightness=80, kelvin=None)
"""Vibrant magenta for social occasions."""

NIGHT = PresetAmbience(color=WARM_ORANGE, brightness=10, kelvin=2200)
"""Very dim warm orange for winding down and sleep."""

READING = PresetAmbience(color=WARM_WHITE, brightness=75, kelvin=4000)
"""Warm white at reading brightness."""

ENERGY = PresetAmbience(color=YELLOW, brightness=100, kelvin=5500)
"""Bright yellow — energizing morning light."""

MOVIE = PresetAmbience(color=DIM_RED, brightness=25, kelvin=None)
"""Dim red for cinema-style viewing."""

MEDITATION = PresetAmbience(color=SOFT_BLUE, brightness=30, kelvin=3000)
"""Soft blue calm for meditation."""

__all__ = [
    "PresetAmbience",
    "FOCUS",
    "RELAX",
    "PARTY",
    "NIGHT",
    "READING",
    "ENERGY",
    "MOVIE",
    "MEDITATION",
]
