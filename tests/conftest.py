"""Shared test fixtures.

We generate fresh RSA keys and a self-signed x509 certificate at the start
of each test session. This keeps the test suite self-contained and avoids
committing secrets — even test secrets — to the repo.
"""

from __future__ import annotations

import datetime as dt

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from gpwebpay import GpwebpayClient

MERCHANT_ID = "1234567890"
PRIVATE_KEY_PASSWORD = "test-password"
CALLBACK_URL = "https://localhost:5000/payment_callback"


@pytest.fixture(scope="session")
def merchant_keypair() -> tuple[bytes, rsa.RSAPrivateKey]:
    """Generate the merchant's private key (encrypted PEM bytes + raw key)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            PRIVATE_KEY_PASSWORD.encode("utf-8")
        ),
    )
    return pem, key


@pytest.fixture(scope="session")
def gateway_keypair() -> tuple[bytes, rsa.RSAPrivateKey]:
    """Generate the gateway's RSA keypair and a self-signed certificate.

    The gateway uses an x509 certificate to publish its public key. We
    return both the certificate (PEM) and the underlying private key so
    tests can sign callback URLs as if they came from GPWebPay.
    """
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test-gw")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + dt.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    pem = cert.public_bytes(serialization.Encoding.PEM)
    return pem, key


@pytest.fixture()
def merchant_private_key(merchant_keypair) -> bytes:
    return merchant_keypair[0]


@pytest.fixture()
def gateway_certificate(gateway_keypair) -> bytes:
    return gateway_keypair[0]


@pytest.fixture()
def gateway_private_key(gateway_keypair) -> rsa.RSAPrivateKey:
    return gateway_keypair[1]


@pytest.fixture()
def client(merchant_private_key, gateway_certificate) -> GpwebpayClient:
    return GpwebpayClient(
        merchant_id=MERCHANT_ID,
        private_key=merchant_private_key,
        private_key_password=PRIVATE_KEY_PASSWORD,
        gateway_public_key=gateway_certificate,
        callback_url=CALLBACK_URL,
    )
