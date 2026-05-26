"""hermes-govee: Python SDK for Govee Home smart devices."""

from hermes_govee.animations import cycle_colors, fade, pulse, strobe
from hermes_govee.client import AsyncGoveeClient, GoveeClient
from hermes_govee.core.exceptions import (
    DeviceOfflineError,
    GoveeAPIError,
    GoveeAuthError,
    GoveeError,
    UnknownDeviceError,
    UnsupportedCapabilityError,
)
from hermes_govee.core.models import ApiResponse, Color, DeviceInfo, LightState, Scene
from hermes_govee.core.snapshot import LightSnapshot
from hermes_govee.devices.base import GoveeDevice
from hermes_govee.devices.group import DeviceGroup
from hermes_govee.devices.light import GoveeLight
from hermes_govee.presets import (
    BLUE,
    COOL_WHITE,
    CYAN,
    DIM_RED,
    ENERGY,
    FOCUS,
    GREEN,
    MAGENTA,
    MEDITATION,
    MOVIE,
    NIGHT,
    ORANGE,
    PARTY,
    PINK,
    PresetAmbience,
    PURPLE,
    READING,
    RED,
    RELAX,
    SOFT_BLUE,
    WARM_ORANGE,
    WARM_WHITE,
    WHITE,
    YELLOW,
)

__all__ = [
    # Clients
    "GoveeClient",
    "AsyncGoveeClient",
    # Devices
    "GoveeLight",
    "GoveeDevice",
    "DeviceGroup",
    # Models
    "DeviceInfo",
    "LightState",
    "Color",
    "Scene",
    "ApiResponse",
    "LightSnapshot",
    # Exceptions
    "GoveeError",
    "GoveeAuthError",
    "GoveeAPIError",
    "DeviceOfflineError",
    "UnknownDeviceError",
    "UnsupportedCapabilityError",
    # Preset Colors
    "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA",
    "WHITE", "WARM_WHITE", "COOL_WHITE", "ORANGE", "PINK", "PURPLE",
    "WARM_ORANGE", "DIM_RED", "SOFT_BLUE",
    # Preset Ambiences
    "PresetAmbience",
    "FOCUS", "RELAX", "PARTY", "NIGHT", "READING",
    "ENERGY", "MOVIE", "MEDITATION",
    # Animations
    "cycle_colors", "pulse", "fade", "strobe",
]
