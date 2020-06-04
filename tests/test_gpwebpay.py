import base64
from collections import OrderedDict

import responses

from gpwebpay.gpwebpay import PaymentGateway
from gpwebpay.config import configuration


# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200

# Example message = "<GPWEBPAY_MERCHANT_ID>|CREATE_ORDER|<order_number>|<amount>|
# <GPWEBPAY_CURRENCY>|<GPWEBPAY_DEPOSIT_FLAG>|<GPWEBPAY_RESPONSE_URL>"


def test_init():
    gw = PaymentGateway()
    assert gw


@responses.activate
def test_connection():
    gw = PaymentGateway()
    responses.add(responses.POST, configuration.GPWEBPAY_TEST_URL, status=200)
    key_bytes = base64.b64decode(configuration.GPWEBPAY_PRIVATE_KEY)
    response = gw.request_payment(order_number="123456", amount=10, key_bytes=key_bytes)
    assert response.status_code == 200


def test_create_data(monkeypatch):
    monkeypatch.setattr(configuration, "GPWEBPAY_MERCHANT_ID", "1234567890")

    expected_data = OrderedDict(
        MERCHANTNUMBER="1234567890",
        OPERATION="CREATE_ORDER",
        ORDERNUMBER="123456",
        AMOUNT="10",
        CURRENCY="978",
        DEPOSITFLAG="1",
        URL="https://localhost:5000/payment_callback",
    )
    gw = PaymentGateway()
    gw._create_data(order_number="123456", amount=10)
    assert gw.data == expected_data


def test_create_message(monkeypatch):
    monkeypatch.setattr(configuration, "GPWEBPAY_MERCHANT_ID", "1234567890")

    expected_message = (
        b"1234567890|CREATE_ORDER|123456|10|978|1|https://localhost:5000/"
        b"payment_callback"
    )
    gw = PaymentGateway()
    gw._create_data(order_number="123456", amount=10)
    message = gw._create_message()
    assert message == expected_message


def test_sign_data(monkeypatch):
    monkeypatch.setattr(configuration, "GPWEBPAY_MERCHANT_ID", "1234567890")

    # Created with java -jar digestProc.jar -s
    # "1234567890|CREATE_ORDER|123456|10|978|1|https://localhost:5000/payment_callback"
    expected_digest = (
        "DWarvfXJP5CFFvn8zNEtImumad7Cmj/M5qQrbcFd66bjhFR4NxkEj4WSR4sCG/6YBWQAgJ3H/n7XPC"
        "RnTu670GaivWQ0dg7DevzyZKcCJwFs4olcA2mb4vfM0yAFW0jkqD3G3eCpHylWogxCVCXrMso8WIpc"
        "5nliwq1Sp/53Q3weXAYXIwvgOe/qtVqhdeOa+r5RNaYcgKzAWafSf9bAfweoedq1yMGfXRPTyLIQfw"
        "Ahsk8DTN9ybohw4mQeZ2/LFcJklMdUuLKqJ/5MLwyV9/0jmxf2bZvymr4aj3S/wpLCJnZV5HDXqYXa"
        "VPokOwvnvGXwSMNw45h1zIwIXpQhig=="
    )
    gw = PaymentGateway()
    gw._create_data(order_number="123456", amount=10)
    message = gw._create_message()
    print(configuration.GPWEBPAY_PRIVATE_KEY)
    key_bytes = base64.b64decode(configuration.GPWEBPAY_PRIVATE_KEY)
    print(key_bytes)
    gw._sign_data(message, key_bytes=key_bytes)

    assert gw.data["DIGEST"] == expected_digest.encode()
