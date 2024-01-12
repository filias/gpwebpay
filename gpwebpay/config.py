from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix='gpwebpay_')

    currency: str = "978"  # EUR
    deposit_flag: str = "1"
    merchant_callback_url: HttpUrl = "https://localhost:5000/payment_callback"
    merchant_id: str = ""
    merchant_private_key: str = ""
    merchant_private_key_passphrase: str = ""
    public_key: str = ""
    url: HttpUrl = "https://test.3dsecure.gpwebpay.com/pgw/order.do"  # Default to test env
    response_url: HttpUrl = "https://gpwebpay.net"


settings = Settings()
