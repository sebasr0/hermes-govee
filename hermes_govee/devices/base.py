"""Base device abstraction for hermes-govee."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hermes_govee.core.exceptions import UnsupportedCapabilityError
from hermes_govee.core.models import DeviceInfo

if TYPE_CHECKING:
    from hermes_govee.core.transport import AsyncBaseTransport, BaseTransport


class GoveeDevice:
    """Base class for all Govee devices."""

    def __init__(
        self, info: DeviceInfo, transport: BaseTransport | AsyncBaseTransport
    ) -> None:
        self.info = info
        self._transport = transport

    @property
    def device_id(self) -> str:
        return self.info.device_id

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def model(self) -> str:
        return self.info.model

    @property
    def online(self) -> bool:
        return self.info.online

    def _raise_unsupported(self, capability: str) -> None:
        raise UnsupportedCapabilityError(
            f"{self.__class__.__name__} ({self.device_id}) does not support '{capability}'"
        )

    def _command(self, name: str, value: Any) -> dict:
        return {"name": name, "value": value}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"device_id={self.device_id!r}, name={self.name!r}, online={self.online}"
            f")"
        )
