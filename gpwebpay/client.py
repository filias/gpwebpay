"""High-level client for the GPWebPay payment gateway."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import httpx

from gpwebpay import signing
from gpwebpay.exceptions import InvalidCallbackError, InvalidSignatureError

# Default test environment for the gateway.
DEFAULT_GATEWAY_URL = "https://test.3dsecure.gpwebpay.com/pgw/order.do"


class GpwebpayClient:
    """A client for sending payment requests to GPWebPay and verifying callbacks.

    Args:
        merchant_id: Your merchant ID issued by GPWebPay.
        private_key: PEM-encoded RSA private key bytes used to sign requests.
        gateway_public_key: PEM-encoded x509 certificate from GPWebPay used
            to verify callback signatures.
        callback_url: The URL on your site that GPWebPay will redirect users
            back to after a payment attempt.
        gateway_url: The GPWebPay endpoint URL. Defaults to the test gateway.
        private_key_password: Optional passphrase for the private key.
        currency: ISO 4217 numeric currency code as a string. Defaults to EUR.
        deposit_flag: GPWebPay deposit flag ("1" requests instant payment).
    """

    def __init__(
        self,
        *,
        merchant_id: str,
        private_key: bytes,
        gateway_public_key: bytes,
        callback_url: str,
        gateway_url: str = DEFAULT_GATEWAY_URL,
        private_key_password: str | None = None,
        currency: str = "978",
        deposit_flag: str = "1",
    ) -> None:
        self.merchant_id = merchant_id
        self.private_key = private_key
        self.private_key_password = private_key_password
        self.gateway_public_key = gateway_public_key
        self.callback_url = callback_url
        self.gateway_url = gateway_url
        self.currency = currency
        self.deposit_flag = deposit_flag

    def build_payment_data(self, order_number: str, amount: int) -> dict[str, str]:
        """Build the signed payload for a payment request.

        The order of keys is significant: GPWebPay computes the digest by
        joining the values with `|` in this exact order.
        """
        data = {
            "MERCHANTNUMBER": self.merchant_id,
            "OPERATION": "CREATE_ORDER",
            "ORDERNUMBER": order_number,
            "AMOUNT": str(amount),
            "CURRENCY": self.currency,
            "DEPOSITFLAG": self.deposit_flag,
            "URL": self.callback_url,
        }
        message = _build_message(data)
        data["DIGEST"] = signing.sign(
            message, self.private_key, self.private_key_password
        ).decode("ascii")
        return data

    def request_payment(self, order_number: str, amount: int) -> httpx.Response:
        """Send a signed payment request to the gateway.

        Returns the raw httpx Response. Typically the caller will redirect
        the user's browser to ``response.url``.
        """
        data = self.build_payment_data(order_number=order_number, amount=amount)
        return httpx.post(
            self.gateway_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def parse_callback(self, callback_url: str) -> dict[str, str]:
        """Parse and verify a callback URL from GPWebPay.

        Returns the callback fields (without DIGEST/DIGEST1) on success.
        Raises InvalidSignatureError if either signature is invalid, or
        InvalidCallbackError if the URL is malformed.
        """
        query = parse_qs(urlparse(callback_url).query)
        data = {key: values[0] for key, values in query.items()}

        try:
            digest = data.pop("DIGEST").encode("ascii")
            digest1 = data.pop("DIGEST1").encode("ascii")
        except KeyError as exc:
            raise InvalidCallbackError(
                f"Callback URL is missing required field: {exc.args[0]}"
            ) from exc

        message = _build_message(data)
        message1 = message + b"|" + self.merchant_id.encode("utf-8")

        if not signing.verify(message, digest, self.gateway_public_key):
            raise InvalidSignatureError("DIGEST verification failed")
        if not signing.verify(message1, digest1, self.gateway_public_key):
            raise InvalidSignatureError("DIGEST1 verification failed")

        return data


def _build_message(data: dict[str, str]) -> bytes:
    """Join data values with `|` to form the digest input."""
    return "|".join(data.values()).encode("utf-8")
