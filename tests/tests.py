import unittest

import gpwebpay


DUMMY_ACCOUNT_DETAILS = dict(
    GPWEBPAY_MERCHANT_ID='0987654321',
    GPWEBPAY_CURRENCY='978',
    GPWEBPAY_DEPOSIT_FLAG='1',
    GPWEBPAY_RESPONSE_URL='bla.com/callback',
    GPWEBPAY_PRIVATE_KEY_NAME='private_key.key',
    GPWEBPAY_PASSPHRASE='bla',
    GPWEBPAY_PUBLIC_KEY_NAME='public_key.key',
    GPWEBPAY_TEST_URL='https://test.3dsecure.gpwebpay.com/pgw/order.do'
)

DUMMY_ACCOUNT_DETAILS_INCOMPLETE = dict(DUMMY_ACCOUNT_DETAILS.items()[:3])

# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200


class TestGPWebPayGatewayMethods(unittest.TestCase):

    def test_init_error(self):
        with self.assertRaises(gpwebpay.GPWebPaySetupException):
            gw = gpwebpay.PaymentGateway(**DUMMY_ACCOUNT_DETAILS_INCOMPLETE)

    def test_init(self):
        gw = gpwebpay.PaymentGateway(**DUMMY_ACCOUNT_DETAILS)
        self.assertTrue(gw)

    def test_connection(self):
        gw = gpwebpay.PaymentGateway()
        response = gw.request_payment()
        self.assertEquals(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
