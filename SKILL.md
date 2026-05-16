---
name: govee-home
description: |
  Control Govee Home smart lights and devices via the Govee OpenAPI. Use when:
  (1) listing or discovering Govee devices, (2) turning lights on/off, (3) adjusting
  brightness or color, (4) activating scenes, (5) querying device state.
  Requires GOVEE_API_KEY environment variable.
---

# Govee Home Smart Device Control

**Package:** `hermes-govee`
**API Docs:** [Govee OpenAPI](https://openapi.api.govee.com)
**GitHub:** [hermes-tools/hermes-govee](https://github.com/hermes-tools/hermes-govee)

---

## Authentication

Set `GOVEE_API_KEY` in your environment or `.env` file:

```bash
export GOVEE_API_KEY="your-key-here"
```

Get your API key from the **Govee Home app** → Profile → API Key.

---

## Quick Reference

| Task | Sync | Async |
|------|------|-------|
| List devices | `client.devices()` | `await client.devices()` |
| Turn on light | `client.device("ID").turn_on()` | `await client.device("ID").turn_on_async()` |
| Set brightness | `client.device("ID").set_brightness(75)` | `await client.device("ID").set_brightness_async(75)` |
| Set color | `client.device("ID").set_color((255, 100, 0))` | `await client.device("ID").set_color_async((255, 100, 0))` |
| Set scene | `client.device("ID").set_scene("Sunrise")` | `await client.device("ID").set_scene_async("Sunrise")` |
| Read state | `client.device("ID").state()` | `await client.device("ID").state_async()` |

---

## Device Types & Capabilities

- **Lights**: power, brightness (0–100), RGB color, color temperature (Kelvin), scenes
- **Appliances**: (future) modes, timers, sensor readings
- **Sensors**: (future) read-only telemetry

---

## Error Handling

| Exception | When | Recovery |
|-----------|------|----------|
| `GoveeAuthError` | Bad/missing API key | Check `GOVEE_API_KEY` env var |
| `DeviceOfflineError` | Device unreachable | Skip or retry later |
| `UnknownDeviceError` | ID not in account | Re-list devices |
| `UnsupportedCapabilityError` | Feature not on device | Query capabilities, offer alternative |

**Always catch `GoveeError` first** as the base exception.

---

## Color Values

- **RGB tuple**: `(255, 100, 0)` for orange
- **Kelvin**: `2000`–`9000` for warm-to-cool white

---

## Scenes

Scene names are case-insensitive but must match Govee app names exactly.

Common scenes: `Reading`, `Sunrise`, `Sunset`, `Rainbow`, `Ocean`, `Candlelight`.

---

## Code Examples

### Sync Usage

```python
from hermes_govee import GoveeClient

with GoveeClient() as client:
    # List devices
    for dev in client.devices():
        print(f"{dev.name}: {dev.device_id} ({dev.type})")

    # Control a light
    light = client.device("H1234")
    light.turn_on()
    light.set_brightness(75)
    light.set_color((255, 100, 0))
    light.set_scene("Sunrise")

    # Read state
    state = light.state()
    print(f"Power: {state.power}, Brightness: {state.brightness}")
```

### Async Usage

```python
import asyncio
from hermes_govee import AsyncGoveeClient

async def main():
    async with AsyncGoveeClient() as client:
        light = await client.device("H1234")
        await light.turn_on_async()
        await light.set_brightness_async(75)
        state = await light.state_async()
        print(state)

asyncio.run(main())
```

### Multiple Devices

```python
with GoveeClient() as client:
    lights = client.devices_by_type("light")
    for light in lights:
        light.turn_on()
        light.set_brightness(50)
```

---

## Installation

```bash
pip install hermes-govee
```

---

## Rules

1. **Always validate `GOVEE_API_KEY`** before making API calls — the client raises `GoveeAuthError` if missing.
2. **Catch device-specific errors** — `DeviceOfflineError` and `UnknownDeviceError` are common in real homes.
3. **Brightness is 0–100** — the Govee API expects this range. The client validates via Pydantic.
4. **Scene names must match exactly** — they are case-insensitive but must correspond to scenes in the Govee app.
5. **Use context managers** — `with GoveeClient()` or `async with AsyncGoveeClient()` ensures connections are closed cleanly.
