"""hermes-govee: Python SDK for Govee Home smart devices."""

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
from hermes_govee.devices.light import GoveeLight

__all__ = [
    "AsyncGoveeClient",
    "GoveeClient",
    "GoveeLight",
    "DeviceInfo",
    "LightState",
    "Color",
    "Scene",
    "ApiResponse",
    "GoveeError",
    "GoveeAuthError",
    "GoveeAPIError",
    "DeviceOfflineError",
    "UnknownDeviceError",
    "UnsupportedCapabilityError",
]
