import pytest

from gpwebpay.gpwebpay import PaymentGateway, GPWebPaySetupException


DUMMY_ACCOUNT_DETAILS = dict(
    GPWEBPAY_MERCHANT_ID="8888880035",
    GPWEBPAY_CURRENCY="978",
    GPWEBPAY_DEPOSIT_FLAG="1",
    GPWEBPAY_RESPONSE_URL="https://www.vinte.sk/",
    GPWEBPAY_PRIVATE_KEY_NAME="gpwebpay-pvk.key",
    GPWEBPAY_PASSPHRASE="PyLadies2020",
    GPWEBPAY_PUBLIC_KEY_NAME="gpe.signing_test.pem",
    GPWEBPAY_TEST_URL="https://test.3dsecure.gpwebpay.com/pgw/order.do",
)

# Here we have an incomplete account
DUMMY_ACCOUNT_DETAILS_INCOMPLETE = {
    key: DUMMY_ACCOUNT_DETAILS[key]
    for key in ["GPWEBPAY_MERCHANT_ID", "GPWEBPAY_CURRENCY", "GPWEBPAY_DEPOSIT_FLAG"]
}

# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200


def test_init_error():
    with pytest.raises(GPWebPaySetupException):
        PaymentGateway(**DUMMY_ACCOUNT_DETAILS_INCOMPLETE)


def test_init():
    gw = PaymentGateway(**DUMMY_ACCOUNT_DETAILS)
    assert gw

@responses.activate
def test_connection():
    gw = PaymentGateway(**DUMMY_ACCOUNT_DETAILS)
    responses.add(
        responses.POST, DUMMY_ACCOUNT_DETAILS["GPWEBPAY_TEST_URL"], status=200
    )
    response = gw.request_payment()
    assert response.status_code == 200