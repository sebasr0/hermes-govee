# hermes-govee

Python SDK for Govee Home smart devices.

## Installation

```bash
pip install hermes-govee
```

## Quick Start

```python
from hermes_govee import GoveeClient

client = GoveeClient()  # uses GOVEE_API_KEY env var
light = client.device("H1234")
light.turn_on()
light.set_brightness(75)
light.set_color((255, 100, 0))
```

See the full documentation in the package docstrings.
