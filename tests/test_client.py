"""Tests for the GoveeClient and AsyncGoveeClient."""

import httpx
import pytest
import respx

from hermes_govee import GoveeClient, AsyncGoveeClient
from hermes_govee.core.exceptions import GoveeAuthError, UnknownDeviceError


class TestGoveeClient:
    @respx.mock
    def test_devices_returns_parsed_list(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
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
                                "type": "devices.types.light",
                                "online": True,
                            }
                        ]
                    },
                },
            )
        )
        client = GoveeClient(api_key="test-key")
        devices = client.devices()
        assert len(devices) == 1
        assert devices[0].device_id == "H1234"
        assert devices[0].name == "Lamp"
        assert devices[0].type == "light"
        client.close()

    @respx.mock
    def test_device_by_id_returns_light(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
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
                                "type": "devices.types.light",
                                "online": True,
                            }
                        ]
                    },
                },
            )
        )
        client = GoveeClient(api_key="test-key")
        light = client.device("H1234")
        assert light.device_id == "H1234"
        assert light.name == "Lamp"
        client.close()

    @respx.mock
    def test_device_not_found_raises(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "message": "success",
                    "data": {"devices": []},
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
        respx.get("https://openapi.api.govee.com/v1/devices").mock(
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
                                "type": "devices.types.light",
                                "online": True,
                            }
                        ]
                    },
                },
            )
        )
        async with AsyncGoveeClient(api_key="test-key") as client:
            devices = await client.devices()
            assert len(devices) == 1
            assert devices[0].device_id == "H1234"
