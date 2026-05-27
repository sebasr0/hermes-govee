"""Core Pydantic models for hermes-govee.

Handles normalization between the Govee Router API (``msg``/``payload``)
and the legacy Simple v1 API (``message``/``data``).
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, model_validator


class DeviceInfo(BaseModel):
    """Basic device metadata from Govee API."""

    device_id: str
    name: str
    type: Literal["light", "appliance", "sensor"]
    model: str
    online: bool = True
    capabilities: List[Dict[str, Any]] = Field(default_factory=list)


class Color(BaseModel):
    """RGB color representation."""

    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def pack(self) -> int:
        """Pack RGB into Govee Router packed integer (r<<16 | g<<8 | b)."""
        return (self.r << 16) + (self.g << 8) + self.b

    @classmethod
    def unpack(cls, packed: int) -> Color:
        """Unpack a Govee Router packed color integer into a Color."""
        return cls(r=(packed >> 16) & 0xFF, g=(packed >> 8) & 0xFF, b=packed & 0xFF)


class Scene(BaseModel):
    """A Govee light scene."""

    name: str
    scene_id: Optional[str] = None


class ApiResponse(BaseModel):
    """Standard Govee API envelope.

    Normalizes Router API (``msg``, ``payload``) and Simple v1
    (``message``, ``data``) into a consistent shape.
    """

    code: int = 0
    message: str = ""
    data: Optional[dict] = None
    _raw: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_envelope(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        # Create a mutable copy
        result = dict(values)

        # Normalize msg -> message
        if "msg" in result and not result.get("message"):
            result["message"] = str(result["msg"])

        # Normalize payload -> data, wrap list payloads
        if "payload" in result:
            raw_payload = result["payload"]
            if isinstance(raw_payload, list):
                result["data"] = {"devices": raw_payload}
            elif isinstance(raw_payload, dict):
                result["data"] = raw_payload
            result.pop("payload", None)

        # Wrap bare list data (Router API device list)
        if isinstance(result.get("data"), list):
            result["data"] = {"devices": result["data"]}

        return result


class LightState(BaseModel):
    """Current state of a light device."""

    power: Literal["on", "off"]
    brightness: int = Field(ge=0, le=100)
    color: Optional[Color] = None
    color_temperature: Optional[int] = None
    scene: Optional[str] = None
