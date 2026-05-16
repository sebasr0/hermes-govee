"""Govee light device with power, brightness, color, and scene control."""

from typing import Tuple

from hermes_govee.core.models import Color, DeviceInfo, LightState
from hermes_govee.devices.base import GoveeDevice
from hermes_govee.utils import rgb_to_tuple


class GoveeLight(GoveeDevice):
    """A Govee light device (bulb, strip, lamp)."""

    def _send(self, name: str, value) -> None:
        """Send a command to this device."""
        cmd = self._command(name, value)
        self._transport.send_command(self.device_id, self.model, cmd)

    async def _send_async(self, name: str, value) -> None:
        cmd = self._command(name, value)
        await self._transport.send_command(self.device_id, self.model, cmd)

    # --- Sync API ---

    def turn_on(self) -> None:
        """Turn the light on."""
        self._send("turn", "on")

    def turn_off(self) -> None:
        """Turn the light off."""
        self._send("turn", "off")

    def set_brightness(self, level: int) -> None:
        """Set brightness (0–100)."""
        self._send("brightness", level)

    def set_color(self, rgb: Tuple[int, int, int]) -> None:
        """Set RGB color."""
        r, g, b = rgb
        self._send("color", {"r": r, "g": g, "b": b})

    def set_color_temperature(self, kelvin: int) -> None:
        """Set color temperature in Kelvin (2000–9000)."""
        self._send("colorTem", kelvin)

    def set_scene(self, name: str) -> None:
        """Activate a scene by name."""
        self._send("scene", name)

    def state(self) -> LightState:
        """Query current state from the API."""
        resp = self._transport.get_state(self.device_id)
        data = resp.data or {}
        properties = data.get("properties", {})
        color_data = properties.get("color", {})
        color = (
            Color(r=color_data["r"], g=color_data["g"], b=color_data["b"])
            if color_data
            else None
        )
        return LightState(
            power=properties.get("power", "off"),
            brightness=properties.get("brightness", 0),
            color=color,
            color_temperature=properties.get("colorTem"),
            scene=properties.get("scene"),
        )

    # --- Async API ---

    async def turn_on_async(self) -> None:
        await self._send_async("turn", "on")

    async def turn_off_async(self) -> None:
        await self._send_async("turn", "off")

    async def set_brightness_async(self, level: int) -> None:
        await self._send_async("brightness", level)

    async def set_color_async(self, rgb: Tuple[int, int, int]) -> None:
        r, g, b = rgb
        await self._send_async("color", {"r": r, "g": g, "b": b})

    async def set_color_temperature_async(self, kelvin: int) -> None:
        await self._send_async("colorTem", kelvin)

    async def set_scene_async(self, name: str) -> None:
        await self._send_async("scene", name)

    async def state_async(self) -> LightState:
        resp = await self._transport.get_state(self.device_id)
        data = resp.data or {}
        properties = data.get("properties", {})
        color_data = properties.get("color", {})
        color = (
            Color(r=color_data["r"], g=color_data["g"], b=color_data["b"])
            if color_data
            else None
        )
        return LightState(
            power=properties.get("power", "off"),
            brightness=properties.get("brightness", 0),
            color=color,
            color_temperature=properties.get("colorTem"),
            scene=properties.get("scene"),
        )
