# gpwebpay

[![ci](https://github.com/filias/gpwebpay/actions/workflows/ci.yml/badge.svg)](https://github.com/filias/gpwebpay/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/filias/gpwebpay)
[![PyPI version](https://img.shields.io/pypi/v/gpwebpay.svg)](https://pypi.org/project/gpwebpay/)
[![PyPI downloads](https://img.shields.io/pypi/dm/gpwebpay.svg)](https://pypi.org/project/gpwebpay/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![types](https://img.shields.io/badge/types-included-blue.svg)](https://peps.python.org/pep-0561/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A modern Python client for the [GPWebPay](https://www.gpwebpay.cz/en/) payment gateway.

`gpwebpay` handles the RSA signing of outgoing payment requests and the verification
of signed callbacks coming back from the gateway, so you can integrate GPWebPay into
your Python webshop without dealing with the cryptography directly.

## Installation

```bash
pip install gpwebpay
# or
uv add gpwebpay
```

## Usage

```python
import base64
import os

from gpwebpay import GpwebpayClient, InvalidSignatureError

client = GpwebpayClient(
    merchant_id=os.environ["GPWEBPAY_MERCHANT_ID"],
    private_key=base64.b64decode(os.environ["GPWEBPAY_MERCHANT_PRIVATE_KEY"]),
    private_key_password=os.environ.get("GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE"),
    gateway_public_key=base64.b64decode(os.environ["GPWEBPAY_PUBLIC_KEY"]),
    callback_url="https://shop.example.com/payment_callback",
    # gateway_url defaults to the test environment; pass the production URL when ready
)

# Send a signed payment request to the gateway. Amount is in cents.
response = client.request_payment(order_number="123456", amount=999)
# Redirect the user's browser to the URL the gateway responded with:
# return redirect(str(response.url))

# In your callback handler, verify the response:
try:
    result = client.parse_callback(callback_url)
    # result is a dict of fields, e.g. {"OPERATION": "...", "PRCODE": "0", ...}
except InvalidSignatureError:
    # The callback was tampered with — reject it.
    ...
```

### Configuration

| Argument | Required | Default | Description |
|---|---|---|---|
| `merchant_id` | yes | — | Your merchant ID issued by GPWebPay |
| `private_key` | yes | — | PEM-encoded RSA private key bytes |
| `gateway_public_key` | yes | — | PEM-encoded x509 certificate from GPWebPay |
| `callback_url` | yes | — | Where GPWebPay should redirect users after payment |
| `gateway_url` | no | test gateway | Production: `https://3dsecure.gpwebpay.com/pgw/order.do` |
| `private_key_password` | no | `None` | Passphrase for the private key |
| `currency` | no | `"978"` (EUR) | ISO 4217 numeric currency code |
| `deposit_flag` | no | `"1"` | `"1"` requests instant payment |

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync               # install dependencies
uv run pytest         # run tests
uv run ruff check .   # lint
uv run ruff format .  # format
uv run mypy gpwebpay  # type check
```

## License

MIT
