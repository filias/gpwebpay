# gpwebpay

GPWebPay Gateway access with python

## How to run the tests

To run the tests:
`pytest tests/tests.py`

## Configuration (WIP)
To use this module construct a PaymentGateway object with a dictionary
with the details of your account. If you do not want to pass a dictionary
with the details you can define your own environmental variables.

import gpwebpay

ACCOUNT_DETAILS = dict(url='',

gw = gpwebpay.PaymentGateway(**ACCOUNT_DETAILS)

Then you can call the available methods from GPWebPay's API:

gw.request_payment()
gw.check_status()

Environmental variables needed:
GPWEBPAY_MERCHANT_ID = '0987654321'
GPWEBPAY_CURRENCY = '978'  # EUR
GPWEBPAY_DEPOSIT_FLAG = ''
GPWEBPAY_RESPONSE_URL = ''
GPWEBPAY_PRIVATE_KEY_NAME = ''
GPWEBPAY_PASSPHRASE = ''
GPWEBPAY_PUBLIC_KEY_NAME = ''


For more details refer to the GPWebPay documentation in > http://www.gpwebpay.cz/en/Download


