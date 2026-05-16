"""Exception hierarchy for hermes-govee."""


class GoveeError(Exception):
    """Base exception for all hermes-govee errors."""


class GoveeAuthError(GoveeError):
    """Invalid or missing API key."""


class GoveeAPIError(GoveeError):
    """API returned a non-2xx status or error code in JSON body."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.api_code = api_code


class DeviceOfflineError(GoveeError):
    """Device is reported as offline."""


class UnknownDeviceError(GoveeError):
    """Device ID not found in account."""


class UnsupportedCapabilityError(GoveeError):
    """Device does not support the requested capability."""
