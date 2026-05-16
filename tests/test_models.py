import pytest
from pydantic import ValidationError

from hermes_govee.core.models import ApiResponse, Color, DeviceInfo, LightState, Scene


class TestDeviceInfo:
    def test_valid_device_info(self) -> None:
        d = DeviceInfo(
            device_id="H1234",
            name="Living Room",
            type="light",
            model="H6008",
            online=True,
        )
        assert d.device_id == "H1234"
        assert d.name == "Living Room"
        assert d.type == "light"
        assert d.online is True

    def test_invalid_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DeviceInfo(
                device_id="H1234",
                name="X",
                type="invalid",
                model="H6008",
                online=True,
            )


class TestColor:
    def test_valid_color(self) -> None:
        c = Color(r=255, g=100, b=0)
        assert c.to_tuple() == (255, 100, 0)

    def test_rgb_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Color(r=300, g=0, b=0)
        with pytest.raises(ValidationError):
            Color(r=-1, g=0, b=0)


class TestScene:
    def test_scene_with_optional_id(self) -> None:
        s = Scene(name="Sunrise")
        assert s.scene_id is None
        s2 = Scene(name="Sunrise", scene_id="sun-01")
        assert s2.scene_id == "sun-01"


class TestApiResponse:
    def test_api_response(self) -> None:
        r = ApiResponse(code=200, message="ok", data={"foo": "bar"})
        assert r.code == 200
        assert r.data == {"foo": "bar"}

    def test_api_response_data_optional(self) -> None:
        r = ApiResponse(code=400, message="bad")
        assert r.data is None


class TestLightState:
    def test_valid_light_state(self) -> None:
        s = LightState(power="on", brightness=75)
        assert s.power == "on"
        assert s.brightness == 75

    def test_brightness_bounds(self) -> None:
        with pytest.raises(ValidationError):
            LightState(power="on", brightness=101)
        with pytest.raises(ValidationError):
            LightState(power="on", brightness=-1)

    def test_invalid_power_rejected(self) -> None:
        with pytest.raises(ValidationError):
            LightState(power="maybe", brightness=50)
