"""Tests for the HTTP transport layer (Router API)."""

import json

import httpx
import pytest
import respx

from hermes_govee.core.exceptions import (
    DeviceOfflineError,
    GoveeAPIError,
    GoveeAuthError,
    UnknownDeviceError,
)
from hermes_govee.core.transport import AsyncBaseTransport, BaseTransport

ROUTER_DEVICES = "https://openapi.api.govee.com/router/api/v1/user/devices"
ROUTER_STATE = "https://openapi.api.govee.com/router/api/v1/device/state"
ROUTER_CONTROL = "https://openapi.api.govee.com/router/api/v1/device/control"
SIMPLE_DEVICES = "https://openapi.api.govee.com/v1/devices"


class TestBaseTransportSync:
    @respx.mock
    def test_get_devices_router_success(self) -> None:
        """get_devices hits Router first, returns parsed payload."""
        respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [
                        {
                            "device": "AA:BB:CC",
                            "sku": "H6099",
                            "deviceName": "TV Light",
                            "type": "devices.types.light",
                        }
                    ],
                },
            )
        )
        transport = BaseTransport(api_key="test-key")
        resp = transport.get_devices()
        assert resp.code == 200
        assert resp.data is not None
        assert resp.data["devices"][0]["device"] == "AA:BB:CC"
        transport.close()

    @respx.mock
    def test_get_devices_fallback_to_simple(self) -> None:
        """When Router returns empty payload, Simple v1 is tried."""
        respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                200, json={"code": 200, "msg": "success", "payload": []}
            )
        )
        simp = respx.get(SIMPLE_DEVICES).mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "message": "success",
                    "data": {
                        "devices": [
                            {"device": "H1234", "model": "H6008", "deviceName": "Lamp"}
                        ]
                    },
                },
            )
        )
        transport = BaseTransport(api_key="test-key")
        resp = transport.get_devices()
        assert simp.called
        assert resp.data is not None
        transport.close()

    @respx.mock
    def test_get_state_posts_to_router(self) -> None:
        """get_state sends a POST with sku + device in body."""
        route = respx.post(ROUTER_STATE).mock(
            return_value=httpx.Response(
                200, json={"code": 200, "msg": "success", "payload": {}}
            )
        )
        transport = BaseTransport(api_key="test-key")
        transport.get_state("H6099", "AA:BB:CC")
        assert route.called
        body = json.loads(route.calls.last.request.content)
        assert body["payload"]["sku"] == "H6099"
        assert body["payload"]["device"] == "AA:BB:CC"
        transport.close()

    @respx.mock
    def test_send_command_posts_capability(self) -> None:
        """send_command translates legacy cmd to Router capability."""
        route = respx.post(ROUTER_CONTROL).mock(
            return_value=httpx.Response(
                200, json={"code": 200, "msg": "success", "payload": {}}
            )
        )
        transport = BaseTransport(api_key="test-key")
        transport.send_command("H6099", "AA:BB:CC", {"name": "turn", "value": "on"})
        assert route.called
        body = json.loads(route.calls.last.request.content)
        cap = body["payload"]["capability"]
        assert cap["type"] == "devices.capabilities.on_off"
        assert cap["instance"] == "powerSwitch"
        assert cap["value"] == 1
        transport.close()

    @respx.mock
    def test_send_command_color_packs_rgb(self) -> None:
        """Color command packs RGB into Router integer."""
        route = respx.post(ROUTER_CONTROL).mock(
            return_value=httpx.Response(200, json={"code": 200, "msg": "success"})
        )
        transport = BaseTransport(api_key="test-key")
        transport.send_command(
            "H6099", "AA:BB:CC",
            {"name": "color", "value": {"r": 255, "g": 100, "b": 0}},
        )
        body = json.loads(route.calls.last.request.content)
        assert body["payload"]["capability"]["value"] == (255 << 16) + (100 << 8)
        transport.close()

    @respx.mock
    def test_request_includes_api_key_header(self) -> None:
        route = respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                200, json={"code": 200, "msg": "success", "payload": []}
            )
        )
        transport = BaseTransport(api_key="my-secret")
        transport.get_devices()
        assert route.calls.last.request.headers["Govee-API-Key"] == "my-secret"
        transport.close()

    @respx.mock
    def test_401_raises_govee_auth_error(self) -> None:
        respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                401, json={"code": 401, "msg": "unauthorized"}
            )
        )
        transport = BaseTransport(api_key="bad-key")
        with pytest.raises(GoveeAuthError):
            transport.get_devices()
        transport.close()

    @respx.mock
    def test_404_raises_unknown_device_error(self) -> None:
        respx.post(ROUTER_STATE).mock(
            return_value=httpx.Response(
                404, json={"code": 404, "msg": "not found"}
            )
        )
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(UnknownDeviceError):
            transport.get_state("H6099", "AA:BB:CC")
        transport.close()

    @respx.mock
    def test_500_raises_govee_api_error_with_status(self) -> None:
        respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                500, json={"code": 500, "msg": "server error"}
            )
        )
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(GoveeAPIError) as exc_info:
            transport.get_devices()
        assert exc_info.value.status_code == 500
        transport.close()

    @respx.mock
    def test_network_error_wrapped_in_govee_error(self) -> None:
        respx.get(ROUTER_DEVICES).mock(side_effect=httpx.ConnectError("Failed"))
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(GoveeAPIError):
            transport.get_devices()
        transport.close()


class TestAsyncBaseTransport:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_devices_success(self) -> None:
        respx.get(ROUTER_DEVICES).mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [],
                },
            )
        )
        async with AsyncBaseTransport(api_key="test-key") as transport:
            resp = await transport.get_devices()
            assert resp.code == 200
