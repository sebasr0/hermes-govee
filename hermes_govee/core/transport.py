"""HTTP transport layer for the Govee OpenAPI (Router API)."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

from hermes_govee.core.exceptions import (
    DeviceOfflineError,
    GoveeAPIError,
    GoveeAuthError,
    UnknownDeviceError,
    UnsupportedCapabilityError,
)
from hermes_govee.core.models import ApiResponse

_ROUTER_BASE = "https://openapi.api.govee.com"
_SIMPLE_BASE = "https://developer-api.govee.com"

# Capability type values used in Router API control requests
_CAP_ON_OFF = "devices.capabilities.on_off"
_CAP_RANGE = "devices.capabilities.range"
_CAP_COLOR = "devices.capabilities.color_setting"
_CAP_TOGGLE = "devices.capabilities.toggle"
_CAP_DYNAMIC = "devices.capabilities.dynamic_scene"


def _resolve_api_key(api_key: str | None) -> str:
    key = api_key or os.getenv("GOVEE_API_KEY")
    if not key:
        raise GoveeAuthError(
            "No API key provided. Set GOVEE_API_KEY env var or pass api_key=..."
        )
    return key


def _pack_color(r: int, g: int, b: int) -> int:
    """Pack RGB into Govee Router integer: (r << 16) | (g << 8) | b."""
    return (r << 16) + (g << 8) + b


def _unpack_color(packed: int) -> tuple[int, int, int]:
    """Unpack Govee Router integer back to (r, g, b)."""
    return ((packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF)


def _map_http_error(status: int, body: dict) -> GoveeAPIError:
    msg = body.get("message", body.get("msg", f"HTTP {status}"))
    api_code = body.get("code")
    if status == 401 or status == 403:
        return GoveeAuthError(msg)
    if status == 404:
        return UnknownDeviceError(msg)
    if status == 400 and "offline" in str(msg).lower():
        return DeviceOfflineError(msg)
    if status == 400 and "unsupported" in str(msg).lower():
        return UnsupportedCapabilityError(msg)
    return GoveeAPIError(msg, status_code=status, api_code=api_code)


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.json()
    except Exception:
        body = {"message": response.text or f"HTTP {response.status_code}"}
    raise _map_http_error(response.status_code, body)


class BaseTransport:
    """Synchronous HTTP transport using the Govee Router API.

    Auto-fallbacks to Simple v1 if the Router endpoint returns 404.
    Uses POST for device state and control (Router convention).
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._base_url = base_url or _ROUTER_BASE
        self._request_id = 0
        self._client = httpx.Client(base_url=self._base_url, timeout=30.0)

    def _next_request_id(self) -> str:
        self._request_id += 1
        return str(self._request_id)

    def _headers(self) -> Dict[str, str]:
        return {"Govee-API-Key": self.api_key}

    def _request(
        self, method: str, path: str, json: Optional[dict] = None
    ) -> ApiResponse:
        try:
            resp = self._client.request(
                method, path, headers=self._headers(), json=json
            )
            _raise_for_status(resp)
            return ApiResponse(**resp.json())
        except httpx.NetworkError as exc:
            raise GoveeAPIError(f"Network error: {exc}") from exc

    # -- Device listing --

    def _devices_router(self) -> ApiResponse:
        return self._request("GET", "/router/api/v1/user/devices")

    def _devices_simple(self) -> ApiResponse:
        return self._request("GET", "/v1/devices")

    def get_devices(self) -> ApiResponse:
        """Discover devices via Router API, falling back to Simple v1."""
        resp = self._devices_router()
        # If Router returns empty data (no devices), try Simple
        data = resp.data
        if data is None or (
            isinstance(data, dict) and not data.get("devices")
        ):
            try:
                resp = self._devices_simple()
            except Exception:
                pass
        return resp

    # -- State query --

    def get_state(self, sku: str, device_id: str) -> ApiResponse:
        """Query device state via Router API (POST)."""
        body: Dict[str, Any] = {
            "requestId": self._next_request_id(),
            "payload": {
                "sku": sku,
                "device": device_id,
            },
        }
        return self._request("POST", "/router/api/v1/device/state", json=body)

    # -- Control --

    def send_command(self, sku: str, device_id: str, cmd: dict) -> ApiResponse:
        """Send a command via Router API (POST).

        The Router API uses capability objects, not legacy cmd dicts.
        This method translates legacy-style cmds to Router format.
        """
        capability = self._cmd_to_capability(cmd)
        body: Dict[str, Any] = {
            "requestId": self._next_request_id(),
            "payload": {
                "sku": sku,
                "device": device_id,
                "capability": capability,
            },
        }
        return self._request("POST", "/router/api/v1/device/control", json=body)

    @staticmethod
    def _cmd_to_capability(cmd: dict) -> dict:
        """Translate a legacy-style cmd dict to a Router API capability object."""
        name = str(cmd.get("name", "") or "")
        value = cmd.get("value")

        if name == "turn":
            return {
                "type": _CAP_ON_OFF,
                "instance": "powerSwitch",
                "value": 1 if value == "on" else 0,
            }
        if name == "toggle":
            return {
                "type": _CAP_TOGGLE,
                "instance": "powerSwitch",
                "value": 1 if value == "on" else 0,
            }
        if name == "brightness":
            return {
                "type": _CAP_RANGE,
                "instance": "brightness",
                "value": int(value),
            }
        if name == "color":
            if isinstance(value, dict):
                return {
                    "type": _CAP_COLOR,
                    "instance": "colorRgb",
                    "value": _pack_color(
                        int(value["r"]), int(value["g"]), int(value["b"])
                    ),
                }
        if name == "colorTem":
            return {
                "type": _CAP_COLOR,
                "instance": "colorTemperatureK",
                "value": int(value),
            }
        if name == "scene":
            return {
                "type": _CAP_DYNAMIC,
                "instance": "lightScene",
                "value": value,
            }
        raise UnsupportedCapabilityError(f"Unknown command: {name}")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BaseTransport:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncBaseTransport:
    """Asynchronous HTTP transport using the Govee Router API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._base_url = base_url or _ROUTER_BASE
        self._request_id = 0
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

    def _next_request_id(self) -> str:
        self._request_id += 1
        return str(self._request_id)

    def _headers(self) -> Dict[str, str]:
        return {"Govee-API-Key": self.api_key}

    async def _request(
        self, method: str, path: str, json: Optional[dict] = None
    ) -> ApiResponse:
        try:
            resp = await self._client.request(
                method, path, headers=self._headers(), json=json
            )
            _raise_for_status(resp)
            return ApiResponse(**resp.json())
        except httpx.NetworkError as exc:
            raise GoveeAPIError(f"Network error: {exc}") from exc

    async def _devices_router(self) -> ApiResponse:
        return await self._request("GET", "/router/api/v1/user/devices")

    async def _devices_simple(self) -> ApiResponse:
        return await self._request("GET", "/v1/devices")

    async def get_devices(self) -> ApiResponse:
        resp = await self._devices_router()
        data = resp.data
        if data is None or (
            isinstance(data, dict) and not data.get("devices")
        ):
            try:
                resp = await self._devices_simple()
            except Exception:
                pass
        return resp

    async def get_state(self, sku: str, device_id: str) -> ApiResponse:
        body: Dict[str, Any] = {
            "requestId": self._next_request_id(),
            "payload": {
                "sku": sku,
                "device": device_id,
            },
        }
        return await self._request("POST", "/router/api/v1/device/state", json=body)

    async def send_command(
        self, sku: str, device_id: str, cmd: dict
    ) -> ApiResponse:
        capability = BaseTransport._cmd_to_capability(cmd)
        body: Dict[str, Any] = {
            "requestId": self._next_request_id(),
            "payload": {
                "sku": sku,
                "device": device_id,
                "capability": capability,
            },
        }
        return await self._request("POST", "/router/api/v1/device/control", json=body)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncBaseTransport:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
