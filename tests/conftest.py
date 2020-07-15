import base64

import pytest

from gpwebpay.config import configuration
from gpwebpay.gpwebpay import PaymentGateway


@pytest.fixture()
def payment_gateway():
    return PaymentGateway()


@pytest.fixture()
def private_key_bytes():
    return base64.b64decode(configuration.GPWEBPAY_MERCHANT_PRIVATE_KEY)


@pytest.fixture()
def public_key_bytes():
    return base64.b64decode(configuration.GPWEBPAY_PUBLIC_KEY)
