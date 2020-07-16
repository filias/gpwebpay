import base64
import random
import string
import os

from flask import (
    Flask,
    request,
    render_template,
    jsonify,
    make_response,
    json,
)

from gpwebpay import gpwebpay
from gpwebpay.config import configuration


app = Flask(__name__)


@app.route("/")
def index():
    # dummy data
    filename = os.path.join(app.static_folder, "data", "products.json")
    with open(filename) as products_file:
        products = json.load(products_file)
    return render_template("index.html", products=products)


@app.route("/pay", methods=["GET", "POST"])
def request_payment():
    order_number = "".join(random.choices(string.digits, k=6))
    amount = 0
    if request.method == "POST":
        amount = int(float(request.json.get("amount")) * 100)

    gw = gpwebpay.PaymentGateway()
    key_bytes = base64.b64decode(configuration.GPWEBPAY_MERCHANT_PRIVATE_KEY)
    response = gw.request_payment(
        order_number=order_number, amount=amount, key_bytes=key_bytes
    )

    return make_response(jsonify({"url": response.url}), response.status_code)


@app.route("/payment_callback")
def payment_callback():
    # TODO: call verify_payment
    gw = gpwebpay.PaymentGateway()
    key_bytes = base64.b64decode(configuration.GPWEBPAY_PUBLIC_KEY)

    if gw.is_payment_valid(request.url, key_bytes):
        # TODO: Make some template for this
        return "Your order is paid!"
    else:
        # TODO: Return the correct error
        return "Some problem in your payment"


if __name__ == "__main__":
    app.run(ssl_context="adhoc")  # To use https
