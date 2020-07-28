import base64

import pytest

from gpwebpay.config import configuration
from gpwebpay.gpwebpay import GpwebpayClient


@pytest.fixture()
def gateway_client():
    return GpwebpayClient()


@pytest.fixture()
def private_key() -> bytes:
    return base64.b64decode(configuration.GPWEBPAY_MERCHANT_PRIVATE_KEY)


@pytest.fixture()
def public_key() -> bytes:
    return base64.b64decode(configuration.GPWEBPAY_PUBLIC_KEY)
