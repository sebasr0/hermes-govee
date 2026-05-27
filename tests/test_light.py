"""Tests for the GoveeLight device class (Router API)."""

import json

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
            "https://openapi.api.govee.com/router/api/v1/device/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "msg": "success"}))

        info = DeviceInfo(
            device_id="A6:CF:D3:2D:41:46:57:2E", name="TV Backlight",
            type="light", model="H6099", online=True,
        )
        transport = BaseTransport(api_key="test-key")
        light = GoveeLight(info, transport)
        light.turn_on()

        assert route.called
        payload = json.loads(route.calls.last.request.content)
        assert payload["payload"]["capability"]["instance"] == "powerSwitch"
        assert payload["payload"]["capability"]["value"] == 1
        transport.close()

    @respx.mock
    def test_set_color_sends_rgb_command(self) -> None:
        route = respx.post(
            "https://openapi.api.govee.com/router/api/v1/device/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "msg": "success"}))

        info = DeviceInfo(
            device_id="A6:CF:D3:2D:41:46:57:2E", name="TV Backlight",
            type="light", model="H6099", online=True,
        )
        transport = BaseTransport(api_key="test-key")
        light = GoveeLight(info, transport)
        light.set_color((255, 100, 0))

        assert route.called
        payload = json.loads(route.calls.last.request.content)
        cap = payload["payload"]["capability"]
        assert cap["instance"] == "colorRgb"
        # 255 << 16 | 100 << 8 | 0 = 16716800 + 25600 + 0 = 16737280
        assert cap["value"] == (255 << 16) + (100 << 8)
        transport.close()

    @respx.mock
    def test_state_returns_parsed_light_state(self) -> None:
        respx.post(
            "https://openapi.api.govee.com/router/api/v1/device/state"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "code": 200,
                    "msg": "success",
                    "payload": {
                        "sku": "H6099",
                        "device": "A6:CF:D3:2D:41:46:57:2E",
                        "capabilities": [
                            {"type": "devices.capabilities.on_off", "instance": "powerSwitch", "state": {"value": 1}},
                            {"type": "devices.capabilities.range", "instance": "brightness", "state": {"value": 75}},
                            {"type": "devices.capabilities.color_setting", "instance": "colorRgb", "state": {"value": 16737280}},
                        ],
                    },
                },
            )
        )
        info = DeviceInfo(
            device_id="A6:CF:D3:2D:41:46:57:2E", name="TV Backlight",
            type="light", model="H6099", online=True,
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
            "https://openapi.api.govee.com/router/api/v1/device/control"
        ).mock(return_value=httpx.Response(200, json={"code": 200, "msg": "success"}))

        info = DeviceInfo(
            device_id="A6:CF:D3:2D:41:46:57:2E", name="TV Backlight",
            type="light", model="H6099", online=True,
        )
        async with AsyncBaseTransport(api_key="test-key") as transport:
            light = GoveeLight(info, transport)
            await light.turn_on_async()

            assert route.called
            payload = json.loads(route.calls.last.request.content)
            assert payload["payload"]["capability"]["instance"] == "powerSwitch"
