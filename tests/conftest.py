import base64

import pytest

from gpwebpay.config import settings
from gpwebpay.gpwebpay import GpwebpayClient


@pytest.fixture()
def gateway_client():
    return GpwebpayClient()


@pytest.fixture()
def private_key() -> bytes:
    return base64.b64decode(settings.merchant_private_key)


@pytest.fixture()
def public_key() -> bytes:
    return base64.b64decode(settings.public_key)
