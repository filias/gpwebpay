import responses

from gpwebpay.gpwebpay import PaymentGateway
from gpwebpay.config import configuration


# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200


def test_init():
    gw = PaymentGateway()
    assert gw


@responses.activate
def test_connection():
    gw = PaymentGateway()
    responses.add(responses.POST, configuration.GPWEBPAY_TEST_URL, status=200)
    response = gw.request_payment()
    assert response.status_code == 200
