import base64
import logging
import urllib.parse as urlparse
from collections import OrderedDict
from urllib.parse import parse_qs

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509

from .config import configuration
from .return_codes import PRCODE, SRCODE

_logger = logging.getLogger(__name__)


class GpwebpayClient:
    def __init__(self):
        self.data = None

    def _create_payment_data(self, order_number="", amount=0):
        """To create the DIGEST we need to keep the order of the params"""
        self.data = OrderedDict()
        self.data["MERCHANTNUMBER"] = configuration.GPWEBPAY_MERCHANT_ID
        self.data["OPERATION"] = "CREATE_ORDER"
        self.data["ORDERNUMBER"] = order_number
        self.data["AMOUNT"] = str(amount)
        self.data["CURRENCY"] = configuration.GPWEBPAY_CURRENCY
        self.data["DEPOSITFLAG"] = configuration.GPWEBPAY_DEPOSIT_FLAG
        self.data["URL"] = configuration.GPWEBPAY_MERCHANT_CALLBACK_URL

    def _create_message(self, data, is_digest_1=False):
        # Create message according to GPWebPay documentation (4.1.1)
        message = "|".join(data.values())

        if is_digest_1:  # Add the MERCHANT_ID
            message += "|" + configuration.GPWEBPAY_MERCHANT_ID

        return message.encode("utf-8")

    def _sign_message(self, message_bytes, key_bytes):
        # Sign the message according to GPWebPay documentation (4.1.3)
        # b) Apply EMSA-PKCS1-v1_5-ENCODE
        private_key = serialization.load_pem_private_key(
            key_bytes,
            password=configuration.GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE.encode(
                "UTF-8"
            ),
            backend=default_backend(),
        )

        # c) Apply RSASSA-PKCS1-V1_5-SIGN and a) Apply SHA1 algorithm on the digest
        signature = private_key.sign(message_bytes, padding.PKCS1v15(), hashes.SHA1())

        # d) Encode c) with BASE64
        digest = base64.b64encode(signature)

        # Put the digest in the data
        self.data["DIGEST"] = digest

    def _create_callback_data(self, url):
        # All the data is in the querystring
        parsed = urlparse.urlparse(url)
        query_string = parse_qs(parsed.query)
        data = {key: value[0] for key, value in query_string.items()}
        return data

    def request_payment(self, order_number=None, amount=0, key_bytes=None):
        self._create_payment_data(order_number=order_number, amount=amount)
        message = self._create_message(self.data)
        self._sign_message(message, key_bytes=key_bytes)

        # Send the request
        # TODO: check if we need all these headers
        headers = {
            "accept-charset": "UTF-8",
            "accept-encoding": "UTF-8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            configuration.GPWEBPAY_URL, data=self.data, headers=headers
        )

        return response

    def _is_callback_valid(self, url, key_bytes=None):
        """Verify the validity of the response from GPWebPay

        The response can be a request when the merchant's callback is used.
        """
        data = self._create_callback_data(url)
        digest = data.pop("DIGEST")  # Remove the DIGEST
        digest1 = data.pop("DIGEST1")  # Remove the DIGEST1

        # Create the messages. One for DIGEST and another for DIGEST1
        message = self._create_message(data)
        message1 = self._create_message(data, is_digest_1=True)

        # Decode the DIGESTs using base64
        signature = base64.b64decode(digest)
        signature1 = base64.b64decode(digest1)

        # Load the public key
        public_key = x509.load_pem_x509_certificate(
            key_bytes, backend=default_backend(),
        ).public_key()

        # Verify the messages
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA1())
        public_key.verify(signature1, message1, padding.PKCS1v15(), hashes.SHA1())
        return data

    def _process_data(self, data):
        """Processes the data from GPWebPay, making it readable"""
        result_text = data.get("RESULTTEXT")
        if result_text != "OK":
            primary_code = PRCODE[data.get("PRCODE")]
            secondary_code = SRCODE[data.get("SRCODE")]
            return f"{primary_code} {secondary_code}"

        return result_text

    def get_payment_result(self, url, key_bytes=None):
        """Returns the result of the payment from the callback request"""
        try:
            data = self._is_callback_valid(url, key_bytes=key_bytes)
            return self._process_data(data)
        except InvalidSignature:
            return "The payment communication was compromised."
