import base64
import logging
import urllib.parse as urlparse
from collections import OrderedDict
from typing import Type
from urllib.parse import parse_qs

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509

from .config import settings

_logger = logging.getLogger(__name__)


class GpwebpayClient:
    def __init__(self):
        self.data = None

    def _create_payment_data(self, order_number: str = "", amount: int = 0, description: str | None = None) -> None:
        """To create the DIGEST we need to keep the order of the params"""
        self.data = OrderedDict()
        self.data["MERCHANTNUMBER"] = settings.merchant_id
        self.data["OPERATION"] = "CREATE_ORDER"
        self.data["ORDERNUMBER"] = order_number
        self.data["AMOUNT"] = str(amount)
        self.data["CURRENCY"] = settings.currency
        self.data["DEPOSITFLAG"] = settings.deposit_flag
        self.data["URL"] = str(settings.merchant_callback_url)
        if description is not None:
            self.data["DESCRIPTION"] = description

    def _create_message(self, data: dict, is_digest_1: bool = False) -> bytes:
        # Create message according to GPWebPay documentation (4.1.1)
        message = "|".join(data.values())

        if is_digest_1:  # Add the MERCHANT_ID
            message += "|" + settings.merchant_id

        return message.encode("utf-8")

    def _sign_message(self, message: bytes, key: bytes) -> None:
        """Sign the message according to GPWebPay documentation"""
        private_key = serialization.load_pem_private_key(
            key,
            password=settings.merchant_private_key_passphrase.encode(
                "UTF-8"
            ),
            backend=default_backend(),
        )

        # Apply RSASSA-PKCS1-V1_5-SIGN and SHA1 algorithm on the digest
        signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

        # Encode with BASE64
        digest = base64.b64encode(signature)

        # Put the digest in the data
        self.data["DIGEST"] = digest

    def _create_callback_data(self, url: str) -> dict:
        # All the data is in the querystring
        parsed = urlparse.urlparse(url)
        query_string = parse_qs(parsed.query)
        data = {key: value[0] for key, value in query_string.items()}
        return data

    def request_payment(
        self, order_number: str = None, amount: int = 0, key: bytes = None
    ) -> Type[requests.Response]:
        self._create_payment_data(order_number=order_number, amount=amount)
        message = self._create_message(self.data)
        self._sign_message(message, key=key)

        # Send the request
        # TODO: check if we need all these headers
        headers = {
            "accept-charset": "UTF-8",
            "accept-encoding": "UTF-8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            settings.url, data=self.data, headers=headers
        )

        return response

    def _is_callback_valid(
        self, data: dict, digest: str, digest1: str, key: bytes = None
    ) -> bool:
        """Verify the validity of the response from GPWebPay

        The response can be a request when the merchant's callback is used.
        """
        # Create the messages. One for DIGEST and another for DIGEST1
        message = self._create_message(data)
        message1 = self._create_message(data, is_digest_1=True)

        # Decode the DIGESTs using base64
        signature = base64.b64decode(digest)
        signature1 = base64.b64decode(digest1)

        # Load the public key
        public_key = x509.load_pem_x509_certificate(
            key, backend=default_backend()
        ).public_key()

        # Verify the messages
        try:
            public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA1())
            public_key.verify(signature1, message1, padding.PKCS1v15(), hashes.SHA1())
            return True
        except InvalidSignature:
            return False

    def get_payment_result(self, url: str, key: bytes = None) -> dict:
        """Returns the result of the payment from the callback request"""
        data = self._create_callback_data(url)
        digest = data.pop("DIGEST")  # Remove the DIGEST
        digest1 = data.pop("DIGEST1")  # Remove the DIGEST1

        if self._is_callback_valid(data, digest, digest1, key=key):
            return data

        return {"RESULT": "The payment communication was compromised."}
