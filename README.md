# gpwebpay

GPWebPay Gateway access with python

## How to run the tests

To run the tests:
`pytest

## Configuration (WIP)
To use this module define your own environmental variables listed below with an example:

```python
import gpwebpay

gw = gpwebpay.PaymentGateway()
```

Then you can call the available methods from GPWebPay's API:

```python
gw.request_payment()
gw.check_status()

```

Environmental variables needed:
```
GPWEBPAY_MERCHANT_ID = "0987654321"
GPWEBPAY_CURRENCY = "978"       # EUR
GPWEBPAY_DEPOSIT_FLAG = "1"     # requests instant payment
GPWEBPAY_RESPONSE_URL = ""
GPWEBPAY_PRIVATE_KEY_NAME = ""
GPWEBPAY_PASSPHRASE = ""
GPWEBPAY_PUBLIC_KEY_NAME = ""
```


For more details refer to the GPWebPay documentation in > http://www.gpwebpay.cz/en/Download


