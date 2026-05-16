import pytest

from hermes_govee.core.exceptions import (
    DeviceOfflineError,
    GoveeAPIError,
    GoveeAuthError,
    GoveeError,
    UnknownDeviceError,
    UnsupportedCapabilityError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_govee_error(self) -> None:
        assert issubclass(GoveeAuthError, GoveeError)
        assert issubclass(GoveeAPIError, GoveeError)
        assert issubclass(DeviceOfflineError, GoveeError)
        assert issubclass(UnknownDeviceError, GoveeError)
        assert issubclass(UnsupportedCapabilityError, GoveeError)

    def test_govee_api_error_stores_status_and_api_code(self) -> None:
        err = GoveeAPIError("bad request", status_code=400, api_code=1001)
        assert str(err) == "bad request"
        assert err.status_code == 400
        assert err.api_code == 1001

    def test_govee_api_error_optional_codes(self) -> None:
        err = GoveeAPIError("something went wrong")
        assert err.status_code is None
        assert err.api_code is None
