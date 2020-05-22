from flask import Flask, redirect, request

from gpwebpay.gpwebpay import PaymentGateway


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/pay")
def request_payment():
    gw = PaymentGateway()
    response = gw.request_payment()
    return redirect(response.url)


@app.route("/payment_callback")
def payment_callback():
    return "Your order is paid!"


if __name__ == "__main__":
    app.run()
