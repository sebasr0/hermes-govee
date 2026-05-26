"""Software animations for Govee lights.

These send sequential API commands with ``time.sleep()`` delays.
For smooth continuous effects, prefer native ``lightScene`` when available.
"""

from __future__ import annotations

import time
from typing import List, Tuple

from hermes_govee.devices.light import GoveeLight
from hermes_govee.presets.colors import WHITE


def cycle_colors(
    light: GoveeLight,
    colors: List[Tuple[int, int, int]],
    interval_sec: float = 2.0,
    cycles: int = 10,
) -> None:
    """Cycle through a list of colors, repeating ``cycles`` times.

    Args:
        light: The GoveeLight to animate.
        colors: List of RGB tuples to cycle through.
        interval_sec: Seconds between color changes.
        cycles: Number of full passes through the color list.
    """
    for _ in range(cycles):
        for color in colors:
            light.set_color(color)
            time.sleep(interval_sec)


def pulse(
    light: GoveeLight,
    min_brightness: int = 10,
    max_brightness: int = 100,
    interval_sec: float = 1.5,
    cycles: int = 20,
) -> None:
    """Pulse brightness up and down (breathing effect).

    Args:
        light: The GoveeLight to animate.
        min_brightness: Lowest brightness level.
        max_brightness: Highest brightness level.
        interval_sec: Seconds between brightness steps.
        cycles: Number of full up/down pulses.
    """
    for _ in range(cycles):
        # Fade up
        for level in range(min_brightness, max_brightness + 1, 10):
            light.set_brightness(level)
            time.sleep(interval_sec / ((max_brightness - min_brightness) / 10 + 1))
        # Fade down
        for level in range(max_brightness, min_brightness - 1, -10):
            light.set_brightness(level)
            time.sleep(interval_sec / ((max_brightness - min_brightness) / 10 + 1))


def fade(
    light: GoveeLight,
    from_color: Tuple[int, int, int],
    to_color: Tuple[int, int, int],
    steps: int = 30,
    interval_sec: float = 0.1,
) -> None:
    """Smoothly fade between two colors.

    Args:
        light: The GoveeLight to animate.
        from_color: Starting RGB tuple.
        to_color: Ending RGB tuple.
        steps: Number of intermediate color steps.
        interval_sec: Seconds between steps.
    """
    for i in range(steps):
        t = i / max(1, steps - 1)
        r = int(from_color[0] + (to_color[0] - from_color[0]) * t)
        g = int(from_color[1] + (to_color[1] - from_color[1]) * t)
        b = int(from_color[2] + (to_color[2] - from_color[2]) * t)
        light.set_color((r, g, b))
        time.sleep(interval_sec)


def strobe(
    light: GoveeLight,
    color: Tuple[int, int, int] = WHITE,
    flash_duration_sec: float = 0.1,
    interval_sec: float = 0.5,
    cycles: int = 30,
) -> None:
    """Strobe flash effect — rapidly toggle brightness between 100 and 0.

    Args:
        light: The GoveeLight to animate.
        color: RGB color to flash.
        flash_duration_sec: How long the light stays bright per flash.
        interval_sec: Seconds between flash starts.
        cycles: Number of flashes.
    """
    light.set_color(color)
    for _ in range(cycles):
        light.set_brightness(100)
        time.sleep(flash_duration_sec)
        light.set_brightness(0)
        time.sleep(interval_sec)
