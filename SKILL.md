---
name: govee-home
description: |
  Control Govee Home smart lights and devices via the Govee Router OpenAPI. Use when:
  (1) listing or discovering Govee devices, (2) turning lights on/off, (3) adjusting
  brightness or color, (4) activating scenes, (5) querying device state.
  Requires GOVEE_API_KEY environment variable.
---

# Govee Home Smart Device Control

**Package:** `hermes-govee` v0.3.0
**API Docs:** [Govee OpenAPI](https://openapi.api.govee.com)
**GitHub:** [sebasr0/hermes-govee](https://github.com/sebasr0/hermes-govee)

---

## Authentication

Get your API key from the **Govee Home app** → Profile → API Key, then:

```bash
export GOVEE_API_KEY="your-key-here"
```

The SDK also accepts `api_key=` explicitly: `GoveeClient(api_key="sk_...")`.

**Key validity check:**
```bash
python3 -c "
import os, httpx
key = os.getenv('GOVEE_API_KEY')
resp = httpx.get('https://openapi.api.govee.com/router/api/v1/user/devices',
                  headers={'Govee-API-Key': key})
print(resp.status_code, resp.json())
"
```

---

## Quick Start

```python
from hermes_govee import GoveeClient, BLUE, FOCUS

client = GoveeClient()  # reads GOVEE_API_KEY from env

# Discover devices
devices = client.devices()
for d in devices:
    print(f"  {d.name} — {d.device_id} (sku={d.model})")

# Control all lights at once
group = client.all_lights()
group.turn_on()
group.apply_ambience(FOCUS)  # cool white, 100%, 6500K

client.close()
```

---

## Installation

```bash
# From GitHub
pip install git+https://github.com/sebasr0/hermes-govee.git

# Or local editable
cd /opt/data/hermes-govee
pip install -e .
```

Verify:
```bash
python3 -c "from hermes_govee import GoveeClient, RED, BLUE, FOCUS, RELAX; print('OK')"
```

---

## Core Operations

### Device Listing

The SDK uses the **Router API** (`openapi.api.govee.com`) by default and auto-falls back to the legacy Simple v1 endpoint if needed.

```python
client = GoveeClient()
devices = client.devices()   # Returns list[DeviceInfo]

# Each DeviceInfo has: device_id, name, model (sku), type, online, capabilities
for d in devices:
    print(f"{d.name} ({d.model}): {d.device_id}")
```

### Single Light Control

```python
light = client.device("A6:CF:D3:2D:41:46:57:2E")

# Power
light.turn_on()
light.turn_off()
light.toggle()

# Settings
light.set_brightness(75)            # 0-100
light.set_color((255, 100, 50))     # RGB tuple
light.set_color_temperature(4000)   # Kelvin, 2000-9000
light.set_scene("Sunrise")          # Native dynamic scene

# Preset helpers
light.apply_preset_color(RED)       # full brightness + color + on
light.apply_preset_color(BLUE)
light.apply_ambience(FOCUS)         # 6500K, 100%, cool white
light.apply_ambience(RELAX)         # 2700K, 40%, warm
light.apply_ambience(MOVIE)         # dim red, 25%
light.apply_ambience(NIGHT)         # 2200K, 10%, warm orange

# State snapshot
snap = light.snapshot()             # LightSnapshot(power, brightness, color, ...)
```

### Multi-Device Orchestration (DeviceGroup)

```python
# All lights
group = client.all_lights()

# Custom subset
group = client.create_group([client.device(id1), client.device(id2)])

# Bulk operations
group.turn_on()
group.turn_off()
group.set_brightness(50)
group.set_color((0, 255, 255))
group.set_color_temperature(4000)
group.apply_preset_color(RED)
group.apply_ambience(FOCUS)

# Sync first light's state to the rest
group.sync()

# Toggle all
group.toggle_all()

# Access underlying lights
for light in group.lights:
    print(light.name)
```

### Async API

All methods have `_async` variants:

```python
import asyncio
from hermes_govee import AsyncGoveeClient, BLUE, FOCUS

async def main():
    async with AsyncGoveeClient() as client:
        light = await client.device("A6:CF:D3:2D:41:46:57:2E")
        await light.turn_on_async()
        await light.set_brightness_async(75)
        await light.apply_preset_color_async(BLUE)
        await light.apply_ambience_async(FOCUS)
        state = await light.state_async()

asyncio.run(main())
```

---

## Preset Colors

Import from `hermes_govee`. All are `(R, G, B)` tuples.

| `RED` | `GREEN` | `BLUE` | `YELLOW` | `CYAN` | `MAGENTA` |
|-------|---------|--------|----------|--------|-----------|
| (255,0,0) | (0,255,0) | (0,0,255) | (255,255,0) | (0,255,255) | (255,0,255) |

| `WHITE` | `WARM_WHITE` | `COOL_WHITE` | `ORANGE` | `PINK` | `PURPLE` |
|---------|-------------|-------------|---------|-------|----------|
| (255,255,255) | (255,223,186) | (240,247,255) | (255,165,0) | (255,105,180) | (128,0,128) |

Support colors: `WARM_ORANGE` (255,200,100), `DIM_RED` (80,0,0), `SOFT_BLUE` (100,150,255).

---

## Preset Ambiences

`PresetAmbience` objects with `color`, `brightness`, and optional `kelvin`.

| Constant | Color | Brightness | Kelvin | Use |
|----------|-------|-----------|--------|-----|
| `FOCUS` | Cool white | 100% | 6500K | Work, study |
| `RELAX` | Warm white | 40% | 2700K | Evening rest |
| `READING` | Warm white | 75% | 4000K | Reading |
| `ENERGY` | Yellow | 100% | 5500K | Morning boost |
| `PARTY` | Magenta | 80% | — | Social |
| `MOVIE` | Dim red | 25% | — | Cinema |
| `MEDITATION` | Soft blue | 30% | 3000K | Calm |
| `NIGHT` | Warm orange | 10% | 2200K | Sleep |

---

## Software Animations

Import from `hermes_govee.animations` (or top-level `hermes_govee`).

```python
from hermes_govee import cycle_colors, pulse, fade, strobe
from hermes_govee.presets.colors import RED, GREEN, BLUE, WHITE

# Cycle through colors
cycle_colors(light, [RED, GREEN, BLUE, WHITE], interval_sec=2.0, cycles=10)

# Breathing effect
pulse(light, min_brightness=10, max_brightness=100, interval_sec=1.5, cycles=20)

# Smooth fade
fade(light, RED, BLUE, steps=30, interval_sec=0.1)

# Strobe flash
strobe(light, color=WHITE, flash_duration_sec=0.1, interval_sec=0.5, cycles=30)
```

**Note:** Animations use `time.sleep()` between API calls. Rate-limit to ~1 command/sec to avoid throttling. For smooth RGBIC effects, prefer native `lightScene` if available.

---

## Scene Management (lightScene)

Native dynamic scenes are model-specific. Query available scenes:

```python
devices = client.devices()
for cap in devices[0].capabilities:
    if cap.get("instance") == "lightScene":
        options = cap.get("parameters", {}).get("options", [])
        print([o["name"] for o in options])

light.set_scene("Sunrise")
light.set_scene("Ocean")
```

---

## API Reference

### GoveeClient

| Method | Returns | Description |
|--------|---------|-------------|
| `devices()` | `list[DeviceInfo]` | List all devices |
| `device(id)` | `GoveeLight` | Get device by ID |
| `devices_by_type(type)` | `list[GoveeLight]` | Filter by type |
| `all_lights()` | `DeviceGroup` | All lights as a group |
| `create_group(lights)` | `DeviceGroup` | Custom light group |
| `close()` | — | Close HTTP client |

`AsyncGoveeClient` mirrors all methods with `await`.

### GoveeLight

| Method | Description |
|--------|-------------|
| `turn_on()` / `turn_off()` | Power control |
| `toggle()` | Flip power based on current state |
| `set_brightness(0-100)` | Brightness |
| `set_color((r,g,b))` | RGB color |
| `set_color_temperature(2000-9000)` | White temperature |
| `set_scene("name")` | Native dynamic scene |
| `state()` → `LightState` | Query current state |
| `snapshot()` → `LightSnapshot` | Immutable state capture |
| `apply_preset_color(color)` | 100% brightness + color + on |
| `apply_ambience(ambience)` | Ambience preset |

All methods have `_async` variants (`turn_on_async()`, etc.).

### DeviceGroup

| Method | Description |
|--------|-------------|
| `turn_on()` / `turn_off()` | Bulk power |
| `set_brightness(level)` | Bulk brightness |
| `set_color(rgb)` | Bulk color |
| `set_color_temperature(k)` | Bulk temperature |
| `apply_preset_color(c)` | Bulk preset |
| `apply_ambience(a)` | Bulk ambience |
| `sync()` | Copy first light's state to all |
| `toggle_all()` | Toggle each light |

All have `_async` variants. Access lights via `.lights` property.

---

## Error Handling

| Exception | Cause | Recovery |
|-----------|-------|----------|
| `GoveeAuthError` | Missing/invalid API key | Check `GOVEE_API_KEY` |
| `DeviceOfflineError` | Device unreachable | Retry later |
| `UnknownDeviceError` | ID not found | Re-list devices |
| `UnsupportedCapabilityError` | Feature not on device | Check capabilities, use fallback |
| `GoveeAPIError` | General API error | Check status_code, message |

Always catch `GoveeError` first (base class).

---

## Pitfalls

1. **GOVEE_API_KEY is shared** between app and developer portal — one key works for both.
2. **Router API is default.** The SDK uses `openapi.api.govee.com` (Router) and auto-falls back to `developer-api.govee.com` (Simple v1) only if Router returns empty.
3. **`colorRgb` is a packed integer** in the Router API: `(r << 16) + (g << 8) + b`. The transport handles packing/unpacking automatically — `set_color((255,100,0))` is all you need.
4. **Scene names are model-specific.** `set_scene("Sunrise")` works on some models but not all. Query device capabilities to discover available scenes.
5. **Animations are software-driven.** They send sequential API commands with `time.sleep()`. Keep interval ≥0.5s to avoid rate limiting.

---

## Development

```bash
git clone https://github.com/sebasr0/hermes-govee.git
cd hermes-govee
pip install -e ".[dev]"
pytest -q   # 33 tests
```

---

## Rules

1. Always verify `GOVEE_API_KEY` is present before making API calls.
2. Use `DeviceGroup` / `all_lights()` for multi-device operations rather than iterating manually.
3. Prefer native `lightScene` scenes over software animations for smooth continuous effects.
4. Catch `GoveeError` first as the base exception class.
5. Use context managers: `with GoveeClient() as client:` or `async with AsyncGoveeClient() as client:`.
