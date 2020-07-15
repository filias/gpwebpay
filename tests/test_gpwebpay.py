from collections import OrderedDict

import requests
import responses

from gpwebpay.config import configuration


# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200

# Example message = "<GPWEBPAY_MERCHANT_ID>|CREATE_ORDER|<order_number>|<amount>|
# <GPWEBPAY_CURRENCY>|<GPWEBPAY_DEPOSIT_FLAG>|<GPWEBPAY_RESPONSE_URL>"


def test_init(payment_gateway):
    assert payment_gateway


@responses.activate
def test_connection(payment_gateway, private_key_bytes):
    responses.add(responses.POST, configuration.GPWEBPAY_TEST_URL, status=200)
    response = payment_gateway.request_payment(
        order_number="123456", amount=10, key_bytes=private_key_bytes
    )
    assert response.status_code == 200


def test_create_data(payment_gateway, monkeypatch):
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
    payment_gateway._create_payment_data(order_number="123456", amount=10)
    assert payment_gateway.data == expected_data


def test_create_message(payment_gateway, monkeypatch):
    monkeypatch.setattr(configuration, "GPWEBPAY_MERCHANT_ID", "1234567890")

    expected_message = (
        b"1234567890|CREATE_ORDER|123456|10|978|1|https://localhost:5000/"
        b"payment_callback"
    )
    payment_gateway._create_payment_data(order_number="123456", amount=10)
    message = payment_gateway._create_message(payment_gateway.data)
    assert message == expected_message


def test_sign_data(payment_gateway, private_key_bytes, monkeypatch):
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
    payment_gateway._create_payment_data(order_number="123456", amount=10)
    message = payment_gateway._create_message(payment_gateway.data)
    payment_gateway._sign_message(message, key_bytes=private_key_bytes)

    assert payment_gateway.data["DIGEST"] == expected_digest.encode()


def test_verify_data(payment_gateway, public_key_bytes):
    url = "https://localhost:5000/payment_callback/"
    params = OrderedDict(
        OPERATION="CREATE_ORDER",
        ORDERNUMBER="696623",
        PRCODE="0",
        SRCODE="0",
        RESULTTEXT="OK",
        DIGEST="YgPdjK7zKtur9LQBNRsk5Rr8ue0U1MxP1tl3NJ2K/vSf1MhBzhKv74ho43pi44BAHgyxuhk"
        "V5UrW9waE2Bp7l095vrNOwTGvJSb6usY2grzOkdqL7EZOJ9bDqpltggiTGADU8CdXlAzu1T"
        "CR2rs7Ufp/Ez3rEQlSOCTtWTtVLmK8ipqq/U7g/20miNWXZGV9pGWDo6V5diFXJG7EadcUM"
        "mKBzGe5+3UTFc2oO2WVcfgalIHKVfEwV7/KTEE1dRhD8Goj29JbHZx0xCRd8yRnMrd8DW/4"
        "BGdjhF6EhpzjOuViiNjVptcl7npTFo0aV6t+pw+hP9bn8i0JN4+czhRtzw==",
        DIGEST1="OEiZFAFZ4AjeTSHF+I1eDodgTObVsB1xSqfziZOfYUj5nqL35n5XH6QQ1WphCPBjBUo8te"
        "8IvkkaMoouJoDgWJcUbu1+UQQfbMD2M032o8shpiL/E+8YGr4s81RMqVwdfL516dEVJJvv"
        "67uGOdo5wH5mgWzN5ZF7Aito3e7kgcOBkPlHyJq9QqvNJhXg4Bd3cueVQvICbe1FUyWED4"
        "PgaDY0eHLC7rL5vG80O+ZtFj7nYg1zZAzpWG/LS7z5HTaHk835pi1OMToWnhK4V60yEdQu"
        "uoO6OFTzB3Qefy3+5k/c9N6GNx7pXGUhCdhGkD/hA77QtUZww8IDlLrik4JYmw==",
    )
    request = requests.Request(method="GET", url=url, params=params)
    payment_gateway.verify_payment(request, key_bytes=public_key_bytes)
