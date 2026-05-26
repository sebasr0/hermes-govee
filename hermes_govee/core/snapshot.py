"""LightSnapshot dataclass for capturing device state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from hermes_govee.core.models import Color


@dataclass
class LightSnapshot:
    """Immutable capture of a light's state at a point in time.

    Used for saving/restoring scenes and for ``GoveeLight.snapshot()``.
    """

    power: str  # "on" | "off"
    brightness: int
    color: Optional[Color] = None
    color_temperature: Optional[int] = None
    scene: Optional[str] = None
