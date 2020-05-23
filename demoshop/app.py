import random
import string

from flask import Flask, redirect, request

from gpwebpay import gpwebpay


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/pay")
def request_payment():
    order_number = "".join(random.choices(string.digits, k=6))

    gw = gpwebpay.PaymentGateway()
    response = gw.request_payment(order_number=order_number)

    return redirect(response.url)


@app.route("/payment_callback")
def payment_callback():
    return "Your order is paid!"


if __name__ == "__main__":
    app.run(ssl_context="adhoc")  # To use https
