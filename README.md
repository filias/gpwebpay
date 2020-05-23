# gpwebpay

GPWebPay Gateway access with python.

## How to run the tests

To run the tests:
```bash
 pytest
 ```

## Configuration
To use this package create a PaymentGateway:

```python
from gpwebpay import gpwebpay

gw = gpwebpay.PaymentGateway()

# Call this method to request a payment to GPWebPay.
# Returns a response, redirect to response.url to go to GPWebPay's and make the payment
# order_number needs to be unique.
gw.request_payment(order_numer="123456")  

# Call this method to check the status of a payment
gw.check_status(order_numer="123456")

```

Environmental variables needed:
```
GPWEBPAY_MERCHANT_ID = "0987654321"  # Your merchant's id from gpwebpay
GPWEBPAY_RESPONSE_URL = ""           # The url for the callback
GPWEBPAY_PRIVATE_KEY_NAME = ""       # The path to the private key file
GPWEBPAY_PUBLIC_KEY_NAME = ""        # The path to the public key file

# Optional:
GPWEBPAY_CURRENCY = "978"       # If not set EUR is the default currency
GPWEBPAY_DEPOSIT_FLAG = "1"     # Requests instant payment
GPWEBPAY_PASSPHRASE = ""        # If any
```

For more details refer to the GPWebPay documentation in > http://www.gpwebpay.cz/en/Download


## Demo shop
There is a demoshop folder which demonstrates the usage of this package in your webshop.
It is a flask app.

To run it locally:
```bash
python demoshop/app.py
```


# Development
We use poetry to manage dependencies, packaging and publishing.
If you want to develop locally install poetry and run:

```bash
poetry install
```
