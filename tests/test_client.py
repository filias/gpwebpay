"""Tests for the high-level GpwebpayClient."""

from __future__ import annotations

import base64
from urllib.parse import urlencode

import httpx
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from gpwebpay import InvalidCallbackError, InvalidSignatureError
from gpwebpay.client import _build_message
from tests.conftest import CALLBACK_URL, MERCHANT_ID


def test_build_payment_data_orders_fields(client):
    data = client.build_payment_data(order_number="123456", amount=10)
    keys = list(data.keys())
    assert keys == [
        "MERCHANTNUMBER",
        "OPERATION",
        "ORDERNUMBER",
        "AMOUNT",
        "CURRENCY",
        "DEPOSITFLAG",
        "URL",
        "DIGEST",
    ]
    assert data["MERCHANTNUMBER"] == MERCHANT_ID
    assert data["OPERATION"] == "CREATE_ORDER"
    assert data["ORDERNUMBER"] == "123456"
    assert data["AMOUNT"] == "10"
    assert data["URL"] == CALLBACK_URL


def test_build_payment_data_signs_with_valid_signature(client, merchant_keypair):
    """The DIGEST should verify against the matching merchant public key."""
    data = client.build_payment_data(order_number="123456", amount=10)
    digest = data.pop("DIGEST")

    message = _build_message(data)
    signature = base64.b64decode(digest)

    _, key = merchant_keypair
    # If verification raises, the test fails.
    key.public_key().verify(signature, message, padding.PKCS1v15(), hashes.SHA1())


def test_request_payment_posts_signed_data(client, monkeypatch):
    captured: dict = {}

    def fake_post(url, data=None, headers=None):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr("httpx.post", fake_post)
    response = client.request_payment(order_number="42", amount=999)

    assert response.status_code == 200
    assert captured["url"] == client.gateway_url
    assert captured["data"]["MERCHANTNUMBER"] == MERCHANT_ID
    assert captured["data"]["ORDERNUMBER"] == "42"
    assert captured["data"]["AMOUNT"] == "999"
    assert "DIGEST" in captured["data"]


def test_parse_callback_returns_data_when_signature_valid(client, gateway_private_key):
    callback_url = _make_signed_callback(gateway_private_key, MERCHANT_ID)
    result = client.parse_callback(callback_url)
    assert result == {
        "OPERATION": "CREATE_ORDER",
        "ORDERNUMBER": "364909",
        "PRCODE": "0",
        "SRCODE": "0",
        "RESULTTEXT": "OK",
    }


def test_parse_callback_raises_on_invalid_signature(client, gateway_private_key):
    """Tamper with the data after signing — verification must fail."""
    callback_url = _make_signed_callback(gateway_private_key, MERCHANT_ID)
    tampered = callback_url.replace("ORDERNUMBER=364909", "ORDERNUMBER=999999")
    with pytest.raises(InvalidSignatureError):
        client.parse_callback(tampered)


def test_parse_callback_raises_on_invalid_digest1(client, gateway_private_key):
    """Sign DIGEST1 with the wrong merchant id so DIGEST passes but DIGEST1 fails."""
    callback_url = _make_signed_callback(
        gateway_private_key, merchant_id_for_digest1="WRONG"
    )
    with pytest.raises(InvalidSignatureError, match="DIGEST1"):
        client.parse_callback(callback_url)


def test_parse_callback_raises_when_digest_missing(client):
    url = "https://localhost:5000/payment_callback?OPERATION=CREATE_ORDER"
    with pytest.raises(InvalidCallbackError):
        client.parse_callback(url)


def _make_signed_callback(
    gateway_private_key,
    merchant_id_for_digest: str = MERCHANT_ID,
    *,
    merchant_id_for_digest1: str | None = None,
) -> str:
    """Build a fake callback URL signed by the gateway's private key.

    By default DIGEST1 is signed with the same merchant id as DIGEST. Pass
    `merchant_id_for_digest1` to deliberately mismatch them for negative tests.
    """
    data = {
        "OPERATION": "CREATE_ORDER",
        "ORDERNUMBER": "364909",
        "PRCODE": "0",
        "SRCODE": "0",
        "RESULTTEXT": "OK",
    }
    message = _build_message(data)
    digest_signature = gateway_private_key.sign(
        message, padding.PKCS1v15(), hashes.SHA1()
    )

    digest1_merchant = merchant_id_for_digest1 or merchant_id_for_digest
    message1 = message + b"|" + digest1_merchant.encode("utf-8")
    digest1_signature = gateway_private_key.sign(
        message1, padding.PKCS1v15(), hashes.SHA1()
    )

    params = {
        **data,
        "DIGEST": base64.b64encode(digest_signature).decode("ascii"),
        "DIGEST1": base64.b64encode(digest1_signature).decode("ascii"),
    }
    return f"https://localhost:5000/payment_callback?{urlencode(params)}"
