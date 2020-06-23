import base64
import random
import string

from flask import Flask, redirect, request, render_template

from gpwebpay import gpwebpay
from gpwebpay.config import configuration


app = Flask(__name__)


@app.route("/")
def index():
    # dummy data
    products = [{
        "id": "1",
        "title": "Avocado 1ps",
        "price": "2.99",
        "image": "avocado.png"

    },
        {
        "id": "2",
        "title": "Tofu 500g",
        "price": "1.99",
        "image": "tofu.png"

    },
        {
        "id": "3",
        "title": "Hummus 200g",
        "price": "2.99",
        "image": "hummus.png"

    },
        {
        "id": "4",
        "title": "Mango 1ps",
        "price": "1.6",
        "image": "mango.png"

    },
    ]
    return render_template("index.html", products=products)


@app.route("/pay")
def request_payment():
    order_number = "".join(random.choices(string.digits, k=6))
    amount = request.values.get("amount")

    gw = gpwebpay.PaymentGateway()
    key_bytes = base64.b64decode(configuration.GPWEBPAY_PRIVATE_KEY)
    response = gw.request_payment(
        order_number=order_number, amount=amount, key_bytes=key_bytes
    )
    return redirect(response.url)


@app.route("/payment_callback")
def payment_callback():
    # TODO: call verify_payment
    # verify_payment(self, request, key_bytes)
    return "Your order is paid!"


if __name__ == "__main__":
    app.run(ssl_context="adhoc")  # To use https
