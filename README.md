# hermes-govee

[![CI](https://github.com/hermes-tools/hermes-govee/actions/workflows/ci.yml/badge.svg)](https://github.com/hermes-tools/hermes-govee/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hermes-govee.svg)](https://pypi.org/project/hermes-govee/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Python SDK for Govee Home smart devices with Hermes skill support.

## Installation

```bash
pip install hermes-govee
```

## Quick Start

```python
from hermes_govee import GoveeClient

with GoveeClient() as client:  # reads GOVEE_API_KEY env var
    light = client.device("H1234")
    light.turn_on()
    light.set_brightness(75)
    light.set_color((255, 100, 0))
```

## Async Usage

```python
import asyncio
from hermes_govee import AsyncGoveeClient

async def main():
    async with AsyncGoveeClient() as client:
        light = await client.device("H1234")
        await light.turn_on_async()
        await light.set_brightness_async(75)

asyncio.run(main())
```

## Authentication

Get your API key from the **Govee Home app** → Profile → API Key, then:

```bash
export GOVEE_API_KEY="your-key-here"
```

## Features

- ✅ List and control Govee lights
- ✅ Power, brightness, RGB color, color temperature, scenes
- ✅ Sync and async APIs via `httpx`
- ✅ Pydantic models for type safety
- ✅ Comprehensive error handling
- ✅ Hermes agent skill included

## Supported Devices

- **Lights**: LED strips, bulbs, lamps (power, brightness, color, scenes)
- **Extensible**: Architecture supports appliances and sensors for future releases

## Hermes Skill

This package includes a `SKILL.md` for Hermes and other AI agents. When loaded, agents can:

- Discover and list Govee devices
- Turn lights on/off and adjust brightness
- Set colors and activate scenes
- Handle errors gracefully

## Error Handling

| Exception | Cause |
|-----------|-------|
| `GoveeAuthError` | Missing or invalid API key |
| `DeviceOfflineError` | Device is unreachable |
| `UnknownDeviceError` | Device ID not found |
| `UnsupportedCapabilityError` | Feature not available on device |

## Development

```bash
git clone https://github.com/hermes-tools/hermes-govee.git
cd hermes-govee
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
