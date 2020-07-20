import urllib.parse
from collections import OrderedDict

import pytest
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


def test_verify_payment_callback_invalid_signature(payment_gateway, public_key_bytes):
    url = (
        "https://localhost:5000/payment_callback?OPERATION=CREATE_ORDER&ORDERNUMBER=269701&PRCODE=0&SRCODE=0&RESULTTEXT"
        "=OK&DIGEST=qYn9bGBnOtdy%2BAgdOqYRRgwcF3ED3N5nqs4hsORz%2ByhyXLMdaPsgi1FNhoQPpOsLrP4bWJ3%2B%2FWNrh6MJ0a6Id82WIgn"
        "Yku%2FX%2FqzPg31qbd2AKBeUqniYZ3NMyIw7WpGqNLmoBumA0RMDfcU38juTpIKq40FE7%2Fj1KHW2Lu6M2TDzj0T86PdKGLoFN%2BnQHLHg%"
        "2BHFOpXJHH%2BbJiB7I1Sf4fkFZu23uOz73DykPjLM7wDYQj%2FkkOdC6V%2BNboTQAXFd8KLLji3eujD1dfxSfS1VMzrGoXsqXlb0Q9oAXuhd"
        "4TvhcjSOTOzOZot47NCzhP0X8uElDXb5kXqrboegsvgRK8A%3D%3D&DIGEST1=WwI6L0sAb7PjwKS5biXRbU46Q%2BYOcJMtogdIojwxgUOD78"
        "mzhyhncpsXRdkgqvA36WaOaDslQk%2FI5o5h1INBwvuZXPWJm1%2FEX0bY2wTzaeLsyxwG%2FuARkJrZLFNucOYytXICLeEMALeiR%2FacxcfQ"
        "abQbfpy8orVFMmLX4RkfkfJD3t5ozp0ITsYCyXXzZZO%2BqdwdHVzDDVRTlcq9HyR1yBtEVGvaE4lXipR68jbT5qr7zyeWBzuknf5yLJPREFxV"
        "%2F0aZ1A9JEP%2BL31lxRMCZDtFNt%2FaxdrjJG%2BjsKreCtrdDsCZ%2FwfwF4z6qEd74nNUOMLMbRF2a5w%2FeVE0U35cWxA%3D%3D"
    )
    url = urllib.parse.unquote(url)
    assert not payment_gateway.is_payment_valid(url, key_bytes=public_key_bytes)


# TODO: implement this test
def test_verify_payment_callback_valid_signature(payment_gateway, public_key_bytes):
    pass
