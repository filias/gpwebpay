# gpwebpay

GPWebPay Gateway access with python

## How to run the tests

To run the tests:
`pytest

## Configuration
To use this module create a PaymentGateway:

```python
import gpwebpay

gw = gpwebpay.PaymentGateway()
```

and then call its available methods:

```python
gw.request_payment()
gw.check_status()

```

Environmental variables needed:
```
GPWEBPAY_MERCHANT_ID = "0987654321"  # Your merchant's id from gpwebpay
GPWEBPAY_RESPONSE_URL = ""           # The url for the callback
GPWEBPAY_PRIVATE_KEY_NAME = ""       # The path to the private key file
GPWEBPAY_PUBLIC_KEY_NAME = ""        # The path to the public key file

# Optional:
GPWEBPAY_CURRENCY = "978"       # If not set EURO is the default currency
GPWEBPAY_DEPOSIT_FLAG = "1"     # Requests instant payment
GPWEBPAY_PASSPHRASE = ""        # If any
```

For more details refer to the GPWebPay documentation in > http://www.gpwebpay.cz/en/Download


