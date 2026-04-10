"""RSA signing and verification for the GPWebPay protocol.

GPWebPay uses RSASSA-PKCS1-v1_5 with SHA-1, as required by their protocol
specification. SHA-1 is mandated by the gateway and is not a security choice
on our side.
"""

from __future__ import annotations

import base64

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def sign(message: bytes, private_key: bytes, password: str | None = None) -> bytes:
    """Sign a message and return a base64-encoded signature.

    Args:
        message: The message bytes to sign.
        private_key: PEM-encoded RSA private key bytes.
        password: Optional passphrase for the private key.
    """
    key = serialization.load_pem_private_key(
        private_key,
        password=password.encode("utf-8") if password else None,
    )
    if not isinstance(key, RSAPrivateKey):
        raise TypeError("private_key must be an RSA private key")

    signature = key.sign(message, padding.PKCS1v15(), hashes.SHA1())
    return base64.b64encode(signature)


def verify(message: bytes, signature: bytes, certificate: bytes) -> bool:
    """Verify a base64-encoded signature against a PEM x509 certificate.

    Returns True if the signature is valid, False otherwise.
    """
    public_key = x509.load_pem_x509_certificate(certificate).public_key()
    if not isinstance(public_key, RSAPublicKey):
        raise TypeError("certificate must contain an RSA public key")

    raw_signature = base64.b64decode(signature)
    try:
        public_key.verify(raw_signature, message, padding.PKCS1v15(), hashes.SHA1())
        return True
    except InvalidSignature:
        return False
