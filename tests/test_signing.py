"""Tests for the low-level signing module."""

from __future__ import annotations

import base64

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from gpwebpay import signing


def test_sign_returns_base64(merchant_private_key):
    signature = signing.sign(b"hello", merchant_private_key, password="test-password")
    # Should be valid base64 and decode to a non-empty byte string.
    decoded = base64.b64decode(signature)
    assert len(decoded) > 0


def test_sign_then_verify_roundtrip(gateway_certificate, gateway_private_key):
    """A signature made with the matching private key must verify."""
    # Re-export the gateway private key without a password so we can sign.
    pem = gateway_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    signature = signing.sign(b"hello world", pem)
    assert signing.verify(b"hello world", signature, gateway_certificate) is True


def test_verify_returns_false_on_tampered_message(
    gateway_certificate, gateway_private_key
):
    pem = gateway_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    signature = signing.sign(b"original", pem)
    assert signing.verify(b"tampered", signature, gateway_certificate) is False


def test_sign_rejects_non_rsa_key():
    ec_key = ec.generate_private_key(ec.SECP256R1())
    pem = ec_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with pytest.raises(TypeError):
        signing.sign(b"hello", pem)


def test_verify_rejects_non_rsa_certificate():
    """A certificate carrying a non-RSA public key should raise TypeError."""
    import datetime as dt

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.x509.oid import NameOID

    ec_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ec-test")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ec_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + dt.timedelta(days=1))
        .sign(ec_key, hashes.SHA256())
    )
    pem = cert.public_bytes(serialization.Encoding.PEM)

    with pytest.raises(TypeError):
        signing.verify(b"msg", b"c2lnbmF0dXJl", pem)
