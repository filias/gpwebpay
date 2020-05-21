from flask import Flask

from gpwebpay.gpwebpay import PaymentGateway


app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World!"


@app.route('/pay')
def request_payment():
    gw = PaymentGateway()
    response = gw.request_payment()
    return response.content.decode()


if __name__ == '__main__':
    app.run()
