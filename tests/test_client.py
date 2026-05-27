"""Tests for the GoveeClient and AsyncGoveeClient (Router API)."""

import httpx
import pytest
import respx

from hermes_govee import GoveeClient, AsyncGoveeClient
from hermes_govee.core.exceptions import GoveeAuthError, UnknownDeviceError


class TestGoveeClient:
    @respx.mock
    def test_devices_returns_parsed_list(self) -> None:
        respx.get("https://openapi.api.govee.com/router/api/v1/user/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [
                        {
                            "device": "A6:CF:D3:2D:41:46:57:2E",
                            "sku": "H6099",
                            "deviceName": "TV Backlight 3 Lite",
                            "type": "devices.types.light",
                            "online": True,
                            "capabilities": [],
                        }
                    ],
                },
            )
        )
        client = GoveeClient(api_key="test-key")
        devices = client.devices()
        assert len(devices) == 1
        assert devices[0].device_id == "A6:CF:D3:2D:41:46:57:2E"
        assert devices[0].name == "TV Backlight 3 Lite"
        assert devices[0].model == "H6099"
        assert devices[0].type == "light"
        client.close()

    @respx.mock
    def test_device_by_id_returns_light(self) -> None:
        respx.get("https://openapi.api.govee.com/router/api/v1/user/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [
                        {
                            "device": "A6:CF:D3:2D:41:46:57:2E",
                            "sku": "H6099",
                            "deviceName": "TV Backlight",
                            "type": "devices.types.light",
                            "online": True,
                            "capabilities": [],
                        }
                    ],
                },
            )
        )
        client = GoveeClient(api_key="test-key")
        light = client.device("A6:CF:D3:2D:41:46:57:2E")
        assert light.device_id == "A6:CF:D3:2D:41:46:57:2E"
        assert light.model == "H6099"
        client.close()

    @respx.mock
    def test_device_not_found_raises(self) -> None:
        respx.get("https://openapi.api.govee.com/router/api/v1/user/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [],
                },
            )
        )
        client = GoveeClient(api_key="test-key")
        with pytest.raises(UnknownDeviceError):
            client.device("H9999")
        client.close()

    def test_missing_api_key_raises(self, monkeypatch) -> None:
        monkeypatch.delenv("GOVEE_API_KEY", raising=False)
        with pytest.raises(GoveeAuthError):
            GoveeClient()


class TestAsyncGoveeClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_devices_returns_parsed_list(self) -> None:
        respx.get("https://openapi.api.govee.com/router/api/v1/user/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": [
                        {
                            "device": "A6:CF:D3:2D:41:46:57:2E",
                            "sku": "H6099",
                            "deviceName": "TV Backlight",
                            "type": "devices.types.light",
                            "online": True,
                            "capabilities": [],
                        }
                    ],
                },
            )
        )
        async with AsyncGoveeClient(api_key="test-key") as client:
            devices = await client.devices()
            assert len(devices) == 1
            assert devices[0].device_id == "A6:CF:D3:2D:41:46:57:2E"
