"""DeviceGroup for orchestrating multiple Govee lights at once."""

from __future__ import annotations

from typing import List, Optional, Tuple

from hermes_govee.devices.light import GoveeLight
from hermes_govee.presets.ambiences import PresetAmbience


class DeviceGroup:
    """A group of GoveeLights that can be controlled in unison."""

    def __init__(self, lights: List[GoveeLight]) -> None:
        self.lights = lights

    # --- Sync bulk operations ---

    def turn_on(self) -> None:
        """Turn on all lights in the group."""
        for light in self.lights:
            light.turn_on()

    def turn_off(self) -> None:
        """Turn off all lights in the group."""
        for light in self.lights:
            light.turn_off()

    def set_brightness(self, level: int) -> None:
        """Set brightness (0–100) on all lights."""
        for light in self.lights:
            light.set_brightness(level)

    def set_color(self, rgb: Tuple[int, int, int]) -> None:
        """Set RGB color on all lights."""
        for light in self.lights:
            light.set_color(rgb)

    def set_color_temperature(self, kelvin: int) -> None:
        """Set color temperature (2000–9000 K) on all lights."""
        for light in self.lights:
            light.set_color_temperature(kelvin)

    def apply_preset_color(self, color: Tuple[int, int, int]) -> None:
        """Apply a preset color at full brightness on all lights."""
        for light in self.lights:
            light.apply_preset_color(color)

    def apply_ambience(self, ambience: PresetAmbience) -> None:
        """Apply a preset ambience on all lights."""
        for light in self.lights:
            light.apply_ambience(ambience)

    def sync(self) -> None:
        """Read state from the first light and apply it to all others."""
        if not self.lights:
            return
        state = self.lights[0].snapshot()
        for light in self.lights[1:]:
            if state.power == "on":
                light.turn_on()
            else:
                light.turn_off()
            light.set_brightness(state.brightness)
            if state.color is not None:
                light.set_color(state.color.to_tuple())
            if state.color_temperature is not None:
                light.set_color_temperature(state.color_temperature)

    def toggle_all(self) -> None:
        """Toggle each light in the group on/off."""
        for light in self.lights:
            light.toggle()

    # --- Async bulk operations ---

    async def turn_on_async(self) -> None:
        """Turn on all lights in the group (async)."""
        for light in self.lights:
            await light.turn_on_async()

    async def turn_off_async(self) -> None:
        """Turn off all lights in the group (async)."""
        for light in self.lights:
            await light.turn_off_async()

    async def set_brightness_async(self, level: int) -> None:
        """Set brightness on all lights (async)."""
        for light in self.lights:
            await light.set_brightness_async(level)

    async def set_color_async(self, rgb: Tuple[int, int, int]) -> None:
        """Set RGB color on all lights (async)."""
        for light in self.lights:
            await light.set_color_async(rgb)

    async def set_color_temperature_async(self, kelvin: int) -> None:
        """Set color temperature on all lights (async)."""
        for light in self.lights:
            await light.set_color_temperature_async(kelvin)

    async def apply_preset_color_async(self, color: Tuple[int, int, int]) -> None:
        """Apply a preset color on all lights (async)."""
        for light in self.lights:
            await light.apply_preset_color_async(color)

    async def apply_ambience_async(self, ambience: PresetAmbience) -> None:
        """Apply a preset ambience on all lights (async)."""
        for light in self.lights:
            await light.apply_ambience_async(ambience)

    async def sync_async(self) -> None:
        """Read state from the first light and apply to all others (async)."""
        if not self.lights:
            return
        state = self.lights[0].snapshot()
        for light in self.lights[1:]:
            if state.power == "on":
                await light.turn_on_async()
            else:
                await light.turn_off_async()
            await light.set_brightness_async(state.brightness)
            if state.color is not None:
                await light.set_color_async(state.color.to_tuple())
            if state.color_temperature is not None:
                await light.set_color_temperature_async(state.color_temperature)

    async def toggle_all_async(self) -> None:
        """Toggle each light in the group on/off (async)."""
        for light in self.lights:
            await light.toggle_async()

    def __repr__(self) -> str:
        ids = ", ".join(light.device_id for light in self.lights)
        return f"DeviceGroup({ids})"
