import base64
import random
import string

from flask import Flask, redirect, request

from gpwebpay import gpwebpay
from gpwebpay.config import configuration


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/pay")
def request_payment():
    order_number = "".join(random.choices(string.digits, k=6))

    gw = gpwebpay.PaymentGateway()
    key_bytes = base64.b64decode(configuration.GPWEBPAY_PRIVATE_KEY)
    response = gw.request_payment(
        order_number=order_number, amount=10, key_bytes=key_bytes
    )
    return redirect(response.url)


@app.route("/payment_callback")
def payment_callback():
    return "Your order is paid!"


if __name__ == "__main__":
    app.run(ssl_context="adhoc")  # To use https
