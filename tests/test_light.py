"""Tests for the GoveeLight device class."""

import httpx
import pytest
import respx

from hermes_govee.core.models import DeviceInfo, LightState
from hermes_govee.core.transport import AsyncBaseTransport, BaseTransport
from hermes_govee.devices.light import GoveeLight


class TestGoveeLightSync:
    @respx.mock
    def test_turn_on_sends_correct_command(self) -> None:
        route = respx.post(
            "https://openapi.api.govee.com/v1/devices/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "message": "success"}))
        info = DeviceInfo(
            device_id="H1234", name="Lamp", type="light", model="H6008", online=True
        )
        transport = BaseTransport(api_key="test-key")
        light = GoveeLight(info, transport)
        light.turn_on()
        assert route.called
        payload = route.calls.last.request.content
        assert b"turn" in payload
        transport.close()

    @respx.mock
    def test_set_color_sends_rgb_command(self) -> None:
        route = respx.post(
            "https://openapi.api.govee.com/v1/devices/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "message": "success"}))
        info = DeviceInfo(
            device_id="H1234", name="Lamp", type="light", model="H6008", online=True
        )
        transport = BaseTransport(api_key="test-key")
        light = GoveeLight(info, transport)
        light.set_color((255, 100, 0))
        assert route.called
        payload = route.calls.last.request.content
        assert b"255" in payload
        transport.close()

    @respx.mock
    def test_state_returns_parsed_light_state(self) -> None:
        respx.get("https://openapi.api.govee.com/v1/devices/state?device=H1234").mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "message": "success",
                    "data": {
                        "device": "H1234",
                        "model": "H6008",
                        "properties": {
                            "power": "on",
                            "brightness": 75,
                            "color": {"r": 255, "g": 100, "b": 0},
                        },
                    },
                },
            )
        )
        info = DeviceInfo(
            device_id="H1234", name="Lamp", type="light", model="H6008", online=True
        )
        transport = BaseTransport(api_key="test-key")
        light = GoveeLight(info, transport)
        state = light.state()
        assert isinstance(state, LightState)
        assert state.power == "on"
        assert state.brightness == 75
        assert state.color is not None
        assert state.color.to_tuple() == (255, 100, 0)
        transport.close()


class TestGoveeLightAsync:
    @respx.mock
    @pytest.mark.asyncio
    async def test_turn_on_async_sends_correct_command(self) -> None:
        route = respx.post(
            "https://openapi.api.govee.com/v1/devices/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "message": "success"}))
        info = DeviceInfo(
            device_id="H1234", name="Lamp", type="light", model="H6008", online=True
        )
        async with AsyncBaseTransport(api_key="test-key") as transport:
            light = GoveeLight(info, transport)
            await light.turn_on_async()
            assert route.called
            payload = route.calls.last.request.content
            assert b"turn" in payload
