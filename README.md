# hermes-govee

[![CI](https://github.com/sebasr0/hermes-govee/actions/workflows/ci.yml/badge.svg)](https://github.com/sebasr0/hermes-govee/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Python SDK for Govee Home smart devices with a full Hermes AI agent skill.

**v0.3.0** — Router API support, presets, animations, DeviceGroup, fully tested.

## Installation

```bash
pip install git+https://github.com/sebasr0/hermes-govee.git
```

Or local:
```bash
git clone https://github.com/sebasr0/hermes-govee.git
cd hermes-govee
pip install -e .
```

## Quick Start

```python
from hermes_govee import GoveeClient, FOCUS

client = GoveeClient()  # reads GOVEE_API_KEY from environment

# Discover devices
for d in client.devices():
    print(f"{d.name} — {d.model} — {d.device_id}")

# Control all lights at once
group = client.all_lights()
group.turn_on()
group.apply_ambience(FOCUS)

client.close()
```

## Features

- ✅ **Device discovery** — auto-detects Router API vs legacy Simple v1
- ✅ **Power control** — on, off, toggle
- ✅ **Brightness** — 0–100
- ✅ **RGB color** — tuple `(R, G, B)` with automatic Router packed-integer packing
- ✅ **Color temperature** — 2000–9000 K
- ✅ **Native dynamic scenes** — `lightScene` support per-device-model
- ✅ **14 preset colors** — `RED`, `BLUE`, `FOCUS`, `RELAX`, `PARTY`, etc.
- ✅ **8 preset ambiences** — `FOCUS`, `RELAX`, `MOVIE`, `NIGHT`, `READING`, `ENERGY`, `MEDITATION`, `PARTY`
- ✅ **DeviceGroup** — control all or a subset of lights atomically
- ✅ **LightSnapshot** — capture/restore device state
- ✅ **Software animations** — `cycle_colors`, `pulse`, `fade`, `strobe`
- ✅ **Full async API** — every method has an `_async` variant
- ✅ **Context managers** — `with GoveeClient()` and `async with AsyncGoveeClient()`
- ✅ **Hermes skill** — `SKILL.md` for AI agent integration
- ✅ **33 tests** — full Router API coverage

## Authentication

Get your API key from the **Govee Home app** → Profile → API Key.

```bash
export GOVEE_API_KEY="your-key-here"
```

Or pass explicitly:
```python
client = GoveeClient(api_key="sk_...")
```

## Usage Examples

### Single light

```python
from hermes_govee import GoveeClient, BLUE

with GoveeClient() as client:
    light = client.device("A6:CF:D3:2D:41:46:57:2E")
    light.turn_on()
    light.set_brightness(75)
    light.set_color(BLUE)
    light.set_scene("Sunrise")

    state = light.snapshot()
    print(state)  # LightSnapshot(power='on', brightness=75, ...)
```

### All lights with presets

```python
from hermes_govee import GoveeClient, RED, FOCUS, RELAX, MOVIE, MEDITATION

client = GoveeClient()
group = client.all_lights()

group.apply_ambience(FOCUS)       # Work mode: 6500K, 100%
group.apply_ambience(RELAX)       # Evening: 2700K, 40%
group.apply_ambience(MOVIE)       # Cinema: dim red, 25%
group.apply_ambience(MEDITATION)  # Calm: soft blue, 30%
group.apply_ambience(NIGHT)       # Sleep: 2200K, 10%

client.close()
```

### Animations

```python
from hermes_govee import GoveeClient, cycle_colors, pulse, fade, strobe
from hermes_govee.presets.colors import RED, GREEN, BLUE, WHITE

client = GoveeClient()
light = client.all_lights().lights[0]

# Cycle through colors
cycle_colors(light, [RED, GREEN, BLUE], interval_sec=1.0, cycles=3)

# Breathing effect
pulse(light, min_brightness=10, max_brightness=100, cycles=10)

# Smooth fade
fade(light, RED, BLUE, steps=30, interval_sec=0.05)

# Strobe
strobe(light, color=WHITE, cycles=15)

client.close()
```

### Async

```python
import asyncio
from hermes_govee import AsyncGoveeClient, BLUE, FOCUS

async def main():
    async with AsyncGoveeClient() as client:
        light = await client.device("A6:CF:D3:2D:41:46:57:2E")
        await light.turn_on_async()
        await light.apply_preset_color_async(BLUE)
        await light.apply_ambience_async(FOCUS)

asyncio.run(main())
```

## Preset Colors

| Constant | RGB |
|----------|-----|
| `RED` | (255, 0, 0) |
| `GREEN` | (0, 255, 0) |
| `BLUE` | (0, 0, 255) |
| `YELLOW` | (255, 255, 0) |
| `CYAN` | (0, 255, 255) |
| `MAGENTA` | (255, 0, 255) |
| `WHITE` | (255, 255, 255) |
| `WARM_WHITE` | (255, 223, 186) |
| `COOL_WHITE` | (240, 247, 255) |
| `ORANGE` | (255, 165, 0) |
| `PINK` | (255, 105, 180) |
| `PURPLE` | (128, 0, 128) |

## Preset Ambiences

| Constant | Color | Brightness | Kelvin |
|----------|-------|-----------|--------|
| `FOCUS` | Cool white | 100% | 6500K |
| `RELAX` | Warm white | 40% | 2700K |
| `READING` | Warm white | 75% | 4000K |
| `ENERGY` | Yellow | 100% | 5500K |
| `PARTY` | Magenta | 80% | — |
| `MOVIE` | Dim red | 25% | — |
| `MEDITATION` | Soft blue | 30% | 3000K |
| `NIGHT` | Warm orange | 10% | 2200K |

## Error Handling

| Exception | When |
|-----------|------|
| `GoveeAuthError` | Missing or invalid API key |
| `DeviceOfflineError` | Device is unreachable |
| `UnknownDeviceError` | Device ID not found in account |
| `UnsupportedCapabilityError` | Command not supported by device |
| `GoveeAPIError` | General API error (base class) |

## Hermes Skill

The included `SKILL.md` teaches Hermes and other AI agents how to:
- Discover and list Govee devices
- Turn lights on/off and adjust brightness
- Set colors and activate scenes
- Apply presets and ambiences
- Run software animations
- Handle errors gracefully

## Architecture

```
hermes_govee/
├── client.py           # GoveeClient + AsyncGoveeClient
├── core/
│   ├── transport.py    # Router API HTTP (BaseTransport + AsyncBaseTransport)
│   ├── models.py       # Pydantic models (DeviceInfo, Color, ApiResponse, LightState)
│   ├── exceptions.py   # Error hierarchy
│   └── snapshot.py     # LightSnapshot dataclass
├── devices/
│   ├── base.py         # GoveeDevice base class
│   ├── light.py        # GoveeLight with full control + presets
│   └── group.py        # DeviceGroup for multi-light orchestration
├── presets/
│   ├── colors.py       # 14 preset RGB color constants
│   └── ambiences.py    # 8 PresetAmbience objects
└── animations.py       # cycle_colors, pulse, fade, strobe
```

**Transport layer:** Uses Govee Router API (`openapi.api.govee.com`) by default. Commands are translated from legacy cmd dicts to Router capability objects. Color packing (`(R<<16) + (G<<8) + B`) and response normalization (`msg` → `message`, `payload` → `data`) happen transparently.

## Development

```bash
git clone https://github.com/sebasr0/hermes-govee.git
cd hermes-govee
pip install -e ".[dev]"
pytest -q   # 33 tests
```

## License

MIT
