import base64
import logging
import os
import requests
from collections import OrderedDict

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


_logger = logging.getLogger(__name__)


class PaymentGateway(object):
    keys = ['GPWEBPAY_' + key for key in ['MERCHANT_ID', 'CURRENCY',
                                          'DEPOSIT_FLAG', 'RESPONSE_URL',
                                          'PRIVATE_KEY_NAME', 'PASSPHRASE',
                                          'PUBLIC_KEY_NAME', 'TEST_URL']]
    account_details = {}
    data = OrderedDict()
    payment = None

    def __init__(self, **kwargs):
        # We try to get the values of the needed account details from kwargs
        # if they are not present we try to get them from os.env
        for key in self.keys:
            if kwargs:
                try:
                    self.account_details[key] = kwargs[key]
                except KeyError:
                    raise GPWebPaySetupException("Not enough account details.")
            else:
                value = os.getenv(key)
                if value:
                    self.account_details[key] = value
                else:
                    raise GPWebPaySetupException("Not enough account details.")

    def _prefill_card_data(self):
        """For prefilling the card used in a previous successful payment"""
        # How to do it?
        # 1. Get the last payment data from your db
        # 2. Fill up the 'FASTPAYID' parameter with the unique ORDERNUMBER
        pass

    def _make_add_info(self):
        pass

    def _create_data(self):
        """To create the DIGEST we need to keep the order of the params"""
        self.data = OrderedDict()
        self.data['MERCHANTNUMBER'] = self.account_details['GPWEBPAY_MERCHANT_ID']
        self.data['OPERATION'] = 'CREATE_ORDER'
        self.data['ORDERNUMBER'] = '123456'  # Dummy for now
        self.data['AMOUNT'] = '10'  # Fixed for now
        self.data['CURRENCY'] = self.account_details['GPWEBPAY_CURRENCY']
        self.data['DEPOSITFLAG'] = self.account_details['GPWEBPAY_DEPOSIT_FLAG']
        self.data['URL'] = self.account_details['GPWEBPAY_RESPONSE_URL']
        self.data['PAYMETHOD'] = 'CRD'  # Just card payments for now
        #if self.payment.payment_method == 'MPS':
        #    self._make_add_info()

    def _sign_data(self):
        # Create DIGEST according to GPWebPay documentation (9.1.1)
        digest_bytes = '|'.join(self.data.values()).encode('utf-8')
        # Sign the data according to GPWebPay documentation (9.1.3)
        # a) - apply SHA1 algorithm on the digest
        #digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
        #digest.update(digest_bytes)
        #digest.finalize()

        # b) - apply EMSA-PKCS1-v1_5-ENCODE
        pk_file = os.path.join(os.getcwd(), self.account_details['GPWEBPAY_PRIVATE_KEY_NAME'])
        with open(pk_file, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(),
                                                             password=self.account_details['GPWEBPAY_PASSPHRASE'].encode("UTF-8"),
                                                             backend=default_backend())

        # c) - apply RSASSA-PKCS1-V1_5-SIGN
        signature = private_key.sign(
            digest_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA1())

        # d) - encode c) with BASE64
        digest = base64.b64encode(signature)

        # Put the digest in the data
        self.data['DIGEST'] = digest

    def _create_payment(self, user, product, payment_method):
        """Put here the code to create a Payment in your db"""
        pass

    def request_payment(self):
        self._create_data()
        self._sign_data()

        # Send the request
        headers = {
            'accept-charset': 'UTF-8',
            'accept-encoding': 'UTF-8',
        }
        response = requests.post(self.account_details['GPWEBPAY_TEST_URL'],
                                 data=self.data, headers=headers)
        return response


class PaymentCallback(object):
    data = OrderedDict()
    payment = None

    def _create_data(self, request):
        # To create the DIGEST we need to keep the order of the params
        self.data = OrderedDict()
        self.data['OPERATION'] = 'CREATE_ORDER'
        for key in ('ORDERNUMBER', 'MERORDERNUM', 'MD', 'PRCODE', 'SRCODE',
                    'RESULTTEXT', 'USERPARAM1', 'ADDINFO'):
            value = request.GET.get(key)
            # Only use existing params
            if value:
                self.data[key] = value
        digest = '|'.join(self.data.values()).encode('utf-8')
        return digest

    def _is_data_verified(self, request, digest):
        # Decode the DIGEST using base64
        signature = request.GET.get('DIGEST')
        signature = base64.b64decode(signature)

        # Initialize RSA key
        pubk_file = os.path.join(os.getcwd(), "../", self.account_details['GPWEBPAY_PUBLIC_KEY_NAME'])
        with open(pubk_file, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read(),
                                                           backend=default_backend())

        # Verify the message
        try:
            public_key.verify(signature,
                              digest,
                              padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                          salt_length=padding.PSS.MAX_LENGTH),
                              hashes.SHA1())
            return True
        except InvalidSignature:
            return False

    def _update_payment(self):
        pass

    def callback(self, request):
        # Make DIGEST based on the request params
        digest = self._create_data(request)

        # Verify the data authenticity
        data_is_verified = self._is_data_verified(request, digest)

        if data_is_verified:
            # Update the payment
            pass
        else:
            # The message received was corrupted - bad signature
            return 'Data not verified.'


class GPWebPaySetupException(Exception):
    pass
