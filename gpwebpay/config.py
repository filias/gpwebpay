import os

from dotenv import load_dotenv
load_dotenv()  # Automaticaly loads the .env file


class Config:
    GPWEBPAY_MERCHANT_ID = os.getenv("GPWEBPAY_MERCHANT_ID", "")
    GPWEBPAY_CURRENCY = os.getenv("GPWEBPAY_CURRENCY", "978")  # EUR
    GPWEBPAY_DEPOSIT_FLAG = os.getenv("GPWEBPAY_DEPOSIT_FLAG", "1")
    GPWEBPAY_RESPONSE_URL = os.getenv(
        "GPWEBPAY_RESPONSE_URL", "https://localhost:5000/payment_callback"
    )
    # GPWEBPAY_PRIVATE_KEY_NAME = os.getenv(
    #     "GPWEBPAY_PRIVATE_KEY_NAME", "gpwebpay-pvk.key"
    # )
    GPWEBPAY_PRIVATE_KEY = os.getenv("GPWEBPAY_PRIVATE_KEY", "")
    GPWEBPAY_PASSPHRASE = os.getenv("GPWEBPAY_PASSPHRASE", "")
    GPWEBPAY_PUBLIC_KEY_NAME = os.getenv(
        "GPWEBPAY_PUBLIC_KEY_NAME", "gpe.signing_test.pem"
    )
    GPWEBPAY_TEST_URL = "https://test.3dsecure.gpwebpay.com/pgw/order.do"


configuration = Config()
