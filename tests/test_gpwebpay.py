from collections import OrderedDict

import responses

from gpwebpay.config import settings


# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200

# Example message = "<GPWEBPAY_MERCHANT_ID>|CREATE_ORDER|<order_number>|<amount>|
# <GPWEBPAY_CURRENCY>|<GPWEBPAY_DEPOSIT_FLAG>|<GPWEBPAY_RESPONSE_URL>|[description]"


def test_init(gateway_client):
    assert gateway_client


@responses.activate
def test_connection(gateway_client, private_key):
    responses.add(responses.POST, str(settings.url), status=200)
    response = gateway_client.request_payment(
        order_number="123456", amount=10, key=private_key
    )
    assert response.status_code == 200


def test_create_data(gateway_client, monkeypatch):
    monkeypatch.setattr(settings, "merchant_id", "1234567890")

    expected_data = OrderedDict(
        MERCHANTNUMBER="1234567890",
        OPERATION="CREATE_ORDER",
        ORDERNUMBER="123456",
        AMOUNT="10",
        CURRENCY="978",
        DEPOSITFLAG="1",
        URL="https://localhost:5000/payment_callback",
        DESCRIPTION="Very important payment",
    )
    gateway_client._create_payment_data(order_number="123456", amount=10, description="Very important payment")
    assert gateway_client.data == expected_data


def test_create_message(gateway_client, monkeypatch):
    monkeypatch.setattr(settings, "merchant_id", "1234567890")

    expected_message = (
        b"1234567890|CREATE_ORDER|123456|10|978|1|https://localhost:5000/"
        b"payment_callback"
    )
    gateway_client._create_payment_data(order_number="123456", amount=10, description="Very important payment")
    message = gateway_client._create_message(gateway_client.data)
    assert message == expected_message


def test_sign_data(gateway_client, private_key, monkeypatch):
    monkeypatch.setattr(settings, "merchant_id", "1234567890")

    # Created with java -jar digestProc.jar -s
    # "1234567890|CREATE_ORDER|123456|10|978|1|https://localhost:5000/payment_callback"
    expected_digest = (
        "DWarvfXJP5CFFvn8zNEtImumad7Cmj/M5qQrbcFd66bjhFR4NxkEj4WSR4sCG/6YBWQAgJ3H/n7XPC"
        "RnTu670GaivWQ0dg7DevzyZKcCJwFs4olcA2mb4vfM0yAFW0jkqD3G3eCpHylWogxCVCXrMso8WIpc"
        "5nliwq1Sp/53Q3weXAYXIwvgOe/qtVqhdeOa+r5RNaYcgKzAWafSf9bAfweoedq1yMGfXRPTyLIQfw"
        "Ahsk8DTN9ybohw4mQeZ2/LFcJklMdUuLKqJ/5MLwyV9/0jmxf2bZvymr4aj3S/wpLCJnZV5HDXqYXa"
        "VPokOwvnvGXwSMNw45h1zIwIXpQhig=="
    )
    gateway_client._create_payment_data(order_number="123456", amount=10)
    message = gateway_client._create_message(gateway_client.data)
    gateway_client._sign_message(message, key=private_key)

    assert gateway_client.data["DIGEST"] == expected_digest.encode()


def test_get_payment_result(gateway_client, public_key):
    url = (
        "https://localhost:5000/payment_callback?OPERATION=CREATE_ORDER&ORDERNUMBER=364909&PRCODE=0&SRCODE=0&RESULTTEXT"
        "=OK&DIGEST=ZvBxMrvxZT5ifTsA%2Fp9r8S0A8YfSZfNvUoVOenbR6GPDOVIFgPOr7ywx%2Bhv3o%2BTalq0GT0WKizSKwlLsoPdfzWCckOtwJ"
        "qyClnEgDZ2%2FjqVwQ9tVa2XIMdoPTrsBzaTJMEmm7t%2FDN7hlbVj9LuFH5kM6ZQO4Y02v8oWB8184PprQl6yeXz8QvCBmqgZwOyZG9R7F66j"
        "K2G5y3BUQ3TDuLPM%2FNGlku594iV1iGfsH2v9n%2Bx6rMrWIL9i1ZMk46nTGLutm%2FEuBpKzeSN66pJPyMVg1sLFzfwxAbIUgLQWfL73H9q%"
        "2BalNrgz2ODkdFPeNzmr0Ei6W6DNEy%2FGzgspHq3bw%3D%3D&DIGEST1=QbTY4GUBw8bG1T46v97fe9flre%2FewJYr2nnyw2DUO3VnEzEhhY"
        "53dcKQpFcFR9PzQDI98UWo9S1MADzPLVQves5MMa1JEDHMi5MjOLt2WQsnkBWwqUCfoITEbxJfIkmv5FQaKqZRhKJ2COnYQgeAHoy4%2FFdbKd"
        "WcdJa9x6h074OJ%2BDDVK2dIaNnHofoPBtluOfNdj3FBF8HbCCHg2OundLljo4F7OnZ26d5Sea3GKQG8%2FxQHw8m%2BSLSAG4AS%2Bzk3oQW9"
        "r6%2BmYMH4R4BZlOOUXcDngxgMBJ86FGrGI4WnS6ddynjJIeFD236WBv8o0uRJaTZa67xD%2Fjx6Ch2zRiVGBw%3D%3D"
    )
    excepted_data = {
        "OPERATION": "CREATE_ORDER",
        "ORDERNUMBER": "364909",
        "PRCODE": "0",
        "SRCODE": "0",
        "RESULTTEXT": "OK",
    }
    assert gateway_client.get_payment_result(url, key=public_key) == excepted_data


def test_get_payment_result_with_invalid_signature(gateway_client, public_key):
    url = (
        "https://localhost:5000/payment_callback?OPERATION=CREATE_ORDER&ORDERNUMBER=269700&PRCODE=0&SRCODE=0&RESULTTEXT"
        "=OK&DIGEST=qYn9bGBnOtdy%2BAgdOqYRRgwcF3ED3N5nqs4hsORz%2ByhyXLMdaPsgi1FNhoQPpOsLrP4bWJ3%2B%2FWNrh6MJ0a6Id82WIgn"
        "Yku%2FX%2FqzPg31qbd2AKBeUqniYZ3NMyIw7WpGqNLmoBumA0RMDfcU38juTpIKq40FE7%2Fj1KHW2Lu6M2TDzj0T86PdKGLoFN%2BnQHLHg%"
        "2BHFOpXJHH%2BbJiB7I1Sf4fkFZu23uOz73DykPjLM7wDYQj%2FkkOdC6V%2BNboTQAXFd8KLLji3eujD1dfxSfS1VMzrGoXsqXlb0Q9oAXuhd"
        "4TvhcjSOTOzOZot47NCzhP0X8uElDXb5kXqrboegsvgRK8A%3D%3D&DIGEST1=WwI6L0sAb7PjwKS5biXRbU46Q%2BYOcJMtogdIojwxgUOD78"
        "mzhyhncpsXRdkgqvA36WaOaDslQk%2FI5o5h1INBwvuZXPWJm1%2FEX0bY2wTzaeLsyxwG%2FuARkJrZLFNucOYytXICLeEMALeiR%2FacxcfQ"
        "abQbfpy8orVFMmLX4RkfkfJD3t5ozp0ITsYCyXXzZZO%2BqdwdHVzDDVRTlcq9HyR1yBtEVGvaE4lXipR68jbT5qr7zyeWBzuknf5yLJPREFxV"
        "%2F0aZ1A9JEP%2BL31lxRMCZDtFNt%2FaxdrjJG%2BjsKreCtrdDsCZ%2FwfwF4z6qEd74nNUOMLMbRF2a5w%2FeVE0U35cWxA%3D%3D"
    )
    assert gateway_client.get_payment_result(url, key=public_key) == {
        "RESULT": "The payment communication was compromised."
    }


def test_get_payment_result_with_error(gateway_client, public_key):
    pass
