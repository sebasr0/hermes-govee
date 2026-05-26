"""Sync and async client entrypoints for hermes-govee."""

from __future__ import annotations

import os
from typing import List

from hermes_govee.core.exceptions import GoveeAuthError, UnknownDeviceError
from hermes_govee.core.models import DeviceInfo
from hermes_govee.core.transport import AsyncBaseTransport, BaseTransport
from hermes_govee.devices.group import DeviceGroup
from hermes_govee.devices.light import GoveeLight


def _resolve_api_key(api_key: str | None) -> str:
    key = api_key or os.getenv("GOVEE_API_KEY")
    if not key:
        raise GoveeAuthError(
            "No API key provided. Set GOVEE_API_KEY env var or pass api_key=..."
        )
    return key


def _parse_devices(api_data: dict) -> List[DeviceInfo]:
    raw_devices = api_data.get("devices", [])
    result: List[DeviceInfo] = []
    for raw in raw_devices:
        # Govee API returns device fields as "device", "deviceName", "type", etc.
        device_type = "light" if "light" in raw.get("type", "").lower() else "appliance"
        info = DeviceInfo(
            device_id=raw.get("device", ""),
            name=raw.get("deviceName", ""),
            type=device_type,
            model=raw.get("model", ""),
            online=raw.get("online", True),
        )
        result.append(info)
    return result


class GoveeClient:
    """Synchronous client for Govee Home devices.

    Defaults to **Simple v1** (`developer-api.govee.com`) because most consumer
    devices respond there with flat REST payloads.  Override ``base_url`` to
    switch to Router v1 (`openapi.api.govee.com`) if needed.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._transport = BaseTransport(api_key=self.api_key, base_url=base_url)

    def devices(self) -> List[DeviceInfo]:
        """List all devices in the account."""
        resp = self._transport.get_devices()
        return _parse_devices(resp.data or {})

    def device(self, device_id: str) -> GoveeLight:
        """Get a specific device by ID."""
        # Query the device list and find the matching one
        all_devices = self.devices()
        for info in all_devices:
            if info.device_id == device_id:
                if info.type == "light":
                    return GoveeLight(info, self._transport)
                raise UnknownDeviceError(
                    f"Device {device_id} is not a light (type={info.type})"
                )
        raise UnknownDeviceError(f"Device {device_id} not found")

    def devices_by_type(self, device_type: str) -> List[GoveeLight]:
        """Get all devices of a given type."""
        return [
            GoveeLight(info, self._transport)
            for info in self.devices()
            if info.type == device_type
        ]

    def all_lights(self) -> DeviceGroup:
        """Return a DeviceGroup containing all lights in the account."""
        lights = self.devices_by_type("light")
        return DeviceGroup(lights)

    def create_group(self, devices: List[GoveeLight]) -> DeviceGroup:
        """Wrap a list of GoveeLight objects into a DeviceGroup."""
        return DeviceGroup(devices)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> GoveeClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncGoveeClient:
    """Asynchronous client for Govee Home devices.

    Defaults to **Simple v1** (`developer-api.govee.com`).  Override ``base_url``
    to switch to Router v1 (`openapi.api.govee.com`) if needed.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._transport = AsyncBaseTransport(api_key=self.api_key, base_url=base_url)

    async def devices(self) -> List[DeviceInfo]:
        resp = await self._transport.get_devices()
        return _parse_devices(resp.data or {})

    async def device(self, device_id: str) -> GoveeLight:
        all_devices = await self.devices()
        for info in all_devices:
            if info.device_id == device_id:
                if info.type == "light":
                    return GoveeLight(info, self._transport)
                raise UnknownDeviceError(
                    f"Device {device_id} is not a light (type={info.type})"
                )
        raise UnknownDeviceError(f"Device {device_id} not found")

    async def devices_by_type(self, device_type: str) -> List[GoveeLight]:
        return [
            GoveeLight(info, self._transport)
            for info in await self.devices()
            if info.type == device_type
        ]

    async def all_lights(self) -> DeviceGroup:
        """Return a DeviceGroup containing all lights in the account (async)."""
        lights = await self.devices_by_type("light")
        return DeviceGroup(lights)

    async def create_group(self, devices: List[GoveeLight]) -> DeviceGroup:
        """Wrap a list of GoveeLight objects into a DeviceGroup (async)."""
        return DeviceGroup(devices)

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> AsyncGoveeClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
