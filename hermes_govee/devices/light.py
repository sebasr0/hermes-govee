"""Govee light device with power, brightness, color, and scene control."""

from __future__ import annotations

from typing import Optional, Tuple

from hermes_govee.core.models import Color, DeviceInfo, LightState
from hermes_govee.core.snapshot import LightSnapshot
from hermes_govee.devices.base import GoveeDevice
from hermes_govee.presets.ambiences import PresetAmbience
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

    # --- Preset helpers (sync) ---

    def apply_preset_color(self, color: Tuple[int, int, int]) -> None:
        """Set brightness to 100, apply color, and turn on."""
        self.set_brightness(100)
        self.set_color(color)
        self.turn_on()

    def apply_ambience(self, ambience: PresetAmbience) -> None:
        """Apply a preset ambience: color + brightness + optional Kelvin."""
        if ambience.kelvin is not None:
            self.set_color_temperature(ambience.kelvin)
        else:
            self.set_color(ambience.color)
        self.set_brightness(ambience.brightness)
        self.turn_on()

    def toggle(self) -> None:
        """Toggle the light on/off based on current state."""
        current = self.state()
        if current.power == "on":
            self.turn_off()
        else:
            self.turn_on()

    def snapshot(self) -> LightSnapshot:
        """Capture the current light state as an immutable snapshot."""
        current = self.state()
        return LightSnapshot(
            power=current.power,
            brightness=current.brightness,
            color=current.color,
            color_temperature=current.color_temperature,
            scene=current.scene,
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

    # --- Preset helpers (async) ---

    async def apply_preset_color_async(self, color: Tuple[int, int, int]) -> None:
        """Set brightness to 100, apply color, and turn on (async)."""
        await self.set_brightness_async(100)
        await self.set_color_async(color)
        await self.turn_on_async()

    async def apply_ambience_async(self, ambience: PresetAmbience) -> None:
        """Apply a preset ambience (async)."""
        if ambience.kelvin is not None:
            await self.set_color_temperature_async(ambience.kelvin)
        else:
            await self.set_color_async(ambience.color)
        await self.set_brightness_async(ambience.brightness)
        await self.turn_on_async()

    async def toggle_async(self) -> None:
        """Toggle the light on/off based on current state (async)."""
        current = await self.state_async()
        if current.power == "on":
            await self.turn_off_async()
        else:
            await self.turn_on_async()

    async def snapshot_async(self) -> LightSnapshot:
        """Capture the current light state as an immutable snapshot (async)."""
        current = await self.state_async()
        return LightSnapshot(
            power=current.power,
            brightness=current.brightness,
            color=current.color,
            color_temperature=current.color_temperature,
            scene=current.scene,
        )
