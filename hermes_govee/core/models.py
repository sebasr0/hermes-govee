"""Core Pydantic models for hermes-govee."""

from typing import Literal, Optional, Tuple

from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    """Basic device metadata from Govee API."""

    device_id: str
    name: str
    type: Literal["light", "appliance", "sensor"]
    model: str
    online: bool


class Color(BaseModel):
    """RGB color representation."""

    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)


class Scene(BaseModel):
    """A Govee light scene."""

    name: str
    scene_id: Optional[str] = None


class ApiResponse(BaseModel):
    """Standard Govee API envelope."""

    code: int
    message: str
    data: Optional[dict] = None


class LightState(BaseModel):
    """Current state of a light device."""

    power: Literal["on", "off"]
    brightness: int = Field(ge=0, le=100)
    color: Optional[Color] = None
    color_temperature: Optional[int] = None
    scene: Optional[str] = None
