import os

from dotenv import load_dotenv

load_dotenv()  # Automaticaly loads the .env file


class Config:
    GPWEBPAY_CURRENCY = os.getenv("GPWEBPAY_CURRENCY", "978")  # EUR
    GPWEBPAY_DEPOSIT_FLAG = os.getenv("GPWEBPAY_DEPOSIT_FLAG", "1")
    GPWEBPAY_MERCHANT_CALLBACK_URL = os.getenv(
        "GPWEBPAY_MERCHANT_CALLBACK_URL", "https://localhost:5000/payment_callback"
    )
    GPWEBPAY_MERCHANT_ID = os.getenv("GPWEBPAY_MERCHANT_ID", "")
    GPWEBPAY_MERCHANT_PRIVATE_KEY = os.getenv("GPWEBPAY_MERCHANT_PRIVATE_KEY", "")
    GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE = os.getenv(
        "GPWEBPAY_MERCHANT_PRIVATE_KEY_PASSPHRASE", ""
    )
    GPWEBPAY_PUBLIC_KEY = os.getenv("GPWEBPAY_PUBLIC_KEY", "")
    GPWEBPAY_URL = "https://test.3dsecure.gpwebpay.com/pgw/order.do"


configuration = Config()
