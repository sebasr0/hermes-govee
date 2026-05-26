"""HTTP transport layer for the Govee OpenAPI."""

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

_BASE_URL_ROUTER = "https://openapi.api.govee.com"
_BASE_URL_SIMPLE = "https://developer-api.govee.com"


def _resolve_api_key(api_key: str | None) -> str:
    key = api_key or os.getenv("GOVEE_API_KEY")
    if not key:
        raise GoveeAuthError(
            "No API key provided. Set GOVEE_API_KEY env var or pass api_key=..."
        )
    return key


def _map_http_error(status: int, body: dict) -> GoveeAPIError:
    msg = body.get("message", f"HTTP {status}")
    api_code = body.get("code")
    if status == 401 or status == 403:
        return GoveeAuthError(msg)
    if status == 404:
        return UnknownDeviceError(msg)
    if status == 400 and "offline" in msg.lower():
        return DeviceOfflineError(msg)
    if status == 400 and "unsupported" in msg.lower():
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
    """Synchronous HTTP transport supporting both Simple v1 and Router v1 APIs."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._base_url = base_url or _BASE_URL_ROUTER
        self._client = httpx.Client(base_url=self._base_url, timeout=30.0)

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

    def get_devices(self) -> ApiResponse:
        return self._request("GET", "/v1/devices")

    def get_state(self, device_id: str) -> ApiResponse:
        return self._request("GET", f"/v1/devices/state?device={device_id}")

    def send_command(self, device_id: str, model: str, cmd: dict) -> ApiResponse:
        payload: Dict[str, Any] = {
            "device": device_id,
            "model": model,
            "cmd": cmd,
        }
        return self._request("PUT", "/v1/devices/control", json=payload)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BaseTransport:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncBaseTransport:
    """Asynchronous HTTP transport supporting both Simple v1 and Router v1 APIs."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = _resolve_api_key(api_key)
        self._base_url = base_url or _BASE_URL_ROUTER
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

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

    async def get_devices(self) -> ApiResponse:
        return await self._request("GET", "/v1/devices")

    async def get_state(self, device_id: str) -> ApiResponse:
        return await self._request("GET", f"/v1/devices/state?device={device_id}")

    async def send_command(self, device_id: str, model: str, cmd: dict) -> ApiResponse:
        payload: Dict[str, Any] = {
            "device": device_id,
            "model": model,
            "cmd": cmd,
        }
        return await self._request("PUT", "/v1/devices/control", json=payload)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncBaseTransport:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
