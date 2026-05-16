"""Tests for the HTTP transport layer."""

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


class TestBaseTransportSync:
    @respx.mock
    def test_get_devices_success(self) -> None:
        route = respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "message": "success",
                    "data": {
                        "devices": [
                            {
                                "device": "H1234",
                                "model": "H6008",
                                "deviceName": "Lamp",
                            }
                        ]
                    },
                },
            )
        )
        transport = BaseTransport(api_key="test-key")
        resp = transport.get_devices()
        assert route.called
        assert resp.code == 200
        assert resp.data is not None
        transport.close()

    @respx.mock
    def test_request_includes_api_key_header(self) -> None:
        route = respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                200, json={"code": 200, "message": "success", "data": {}}
            )
        )
        transport = BaseTransport(api_key="my-secret")
        transport.get_devices()
        assert route.calls.last.request.headers["Govee-API-Key"] == "my-secret"
        transport.close()

    @respx.mock
    def test_401_raises_govee_auth_error(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                401, json={"code": 401, "message": "unauthorized"}
            )
        )
        transport = BaseTransport(api_key="bad-key")
        with pytest.raises(GoveeAuthError):
            transport.get_devices()
        transport.close()

    @respx.mock
    def test_404_raises_unknown_device_error(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices/state").mock(
            return_value=httpx.Response(
                404, json={"code": 404, "message": "not found"}
            )
        )
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(UnknownDeviceError):
            transport.get_state("H1234")
        transport.close()

    @respx.mock
    def test_500_raises_govee_api_error_with_status(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                500, json={"code": 500, "message": "server error"}
            )
        )
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(GoveeAPIError) as exc_info:
            transport.get_devices()
        assert exc_info.value.status_code == 500
        transport.close()

    @respx.mock
    def test_network_error_wrapped_in_govee_error(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
            side_effect=httpx.ConnectError("Failed")
        )
        transport = BaseTransport(api_key="test-key")
        with pytest.raises(GoveeAPIError):
            transport.get_devices()
        transport.close()


class TestAsyncBaseTransport:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_devices_success(self) -> None:
        route = respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "message": "success",
                    "data": {"devices": []},
                },
            )
        )
        async with AsyncBaseTransport(api_key="test-key") as transport:
            resp = await transport.get_devices()
            assert route.called
            assert resp.code == 200
