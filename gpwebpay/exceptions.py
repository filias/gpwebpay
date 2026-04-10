"""Exceptions raised by the gpwebpay client."""


class GpwebpayError(Exception):
    """Base class for all gpwebpay errors."""


class InvalidSignatureError(GpwebpayError):
    """Raised when a signature on a callback URL cannot be verified."""


class InvalidCallbackError(GpwebpayError):
    """Raised when a callback URL is malformed or missing required fields."""
