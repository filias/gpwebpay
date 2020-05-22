import base64
import logging
import os
import requests
from collections import OrderedDict

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .config import configuration


_logger = logging.getLogger(__name__)


class PaymentGateway:
    data = OrderedDict()  # Parameters need to be in the right order
    payment = None

    def _create_data(self, order_number=""):
        """To create the DIGEST we need to keep the order of the params"""
        self.data = OrderedDict()
        self.data["MERCHANTNUMBER"] = configuration.GPWEBPAY_MERCHANT_ID
        self.data["OPERATION"] = "CREATE_ORDER"
        self.data["ORDERNUMBER"] = order_number
        self.data["AMOUNT"] = "10"  # Fixed for now
        self.data["CURRENCY"] = configuration.GPWEBPAY_CURRENCY
        self.data["DEPOSITFLAG"] = configuration.GPWEBPAY_DEPOSIT_FLAG
        self.data["URL"] = configuration.GPWEBPAY_RESPONSE_URL

    def _sign_data(self):
        # Create message according to GPWebPay documentation (4.1.1)
        message = "|".join(self.data.values())
        message_bytes = message.encode("utf-8")

        # Sign the message according to GPWebPay documentation (4.1.3)
        # b) Apply EMSA-PKCS1-v1_5-ENCODE
        # TODO: fix this path (also for public key)
        pk_file = os.path.join(os.getcwd(), configuration.GPWEBPAY_PRIVATE_KEY_NAME)
        with open(pk_file, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=configuration.GPWEBPAY_PASSPHRASE.encode("UTF-8"),
                backend=default_backend(),
            )

        # c) Apply RSASSA-PKCS1-V1_5-SIGN and a) Apply SHA1 algorithm on the digest
        signature = private_key.sign(message_bytes, padding.PKCS1v15(), hashes.SHA1())

        # d) Encode c) with BASE64
        digest = base64.b64encode(signature)

        # Put the digest in the data
        self.data["DIGEST"] = digest

    def request_payment(self, order_number=""):
        self._create_data(order_number=order_number)
        self._sign_data()

        # Send the request
        headers = {
            "accept-charset": "UTF-8",
            "accept-encoding": "UTF-8",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            configuration.GPWEBPAY_TEST_URL, data=self.data, headers=headers
        )
        return response


class PaymentCallback:
    data = OrderedDict()
    payment = None

    def _create_data(self, request):
        # To create the DIGEST we need to keep the order of the params
        self.data = OrderedDict()
        self.data["OPERATION"] = "CREATE_ORDER"
        for key in (
            "ORDERNUMBER",
            "MERORDERNUM",
            "MD",
            "PRCODE",
            "SRCODE",
            "RESULTTEXT",
            "USERPARAM1",
            "ADDINFO",
        ):
            value = request.GET.get(key)
            # Only use existing params
            if value:
                self.data[key] = value
        digest = "|".join(self.data.values()).encode("utf-8")
        return digest

    def _is_data_verified(self, request, digest):
        # Decode the DIGEST using base64
        signature = request.GET.get("DIGEST")
        signature = base64.b64decode(signature)

        # Initialize RSA key
        pubk_file = os.path.join(os.getcwd(), configuration.GPWEBPAY_PUBLIC_KEY_NAME)
        with open(pubk_file, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )

        # Verify the message
        try:
            public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA1(),
            )
            return True
        except InvalidSignature:
            return False

    def callback(self, request):
        # Make DIGEST based on the request params
        digest = self._create_data(request)

        # Verify the data authenticity
        data_is_verified = self._is_data_verified(request, digest)

        if data_is_verified:
            # Update the payment
            pass
        else:
            # The message received was corrupted - bad signature
            return "Data not verified."
