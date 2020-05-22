import responses

from gpwebpay.gpwebpay import PaymentGateway
from gpwebpay.config import configuration


# Card for test payments
# Card number: 4056070000000008
# Expiry date: 12/2020
# CVC2: 200

# message = "8888880035|CREATE_ORDER|123456|10|978|1|https://www.vinte.sk/"

def test_init():
    gw = PaymentGateway()
    assert gw


@responses.activate
def test_connection():
    gw = PaymentGateway()
    responses.add(responses.POST, configuration.GPWEBPAY_TEST_URL, status=200)
    response = gw.request_payment("123456")
    assert response.status_code == 200


def test_sign_data():
    expected_digest = "JwJUYtV/Z8SpGIk6r0gzk7ioKcOhERfOR4+bhUBxC8BwbH9wxuf9ct6cHMpXDqI" \
                      "bCrgk5nhIqdQ8tPWGbDCiDSeaDAMQyB9G/HcWk5N6r4tLmife3wzw0CSJ1mdRhY" \
                      "A0gyRTMwHRIiUIodbX/0dFh9rJgB+Sz91nnMV5KA07YNyGvIFpBsi91w6FideB3" \
                      "6EweQY2dq3MPXr6yMmj5Dzlvus4DBNY8VfnKZvFUoNvuxj78r9WDeowSvQwQVrc" \
                      "znKx2gHyb9XI5cGyISzL5tcHIFeLENi4+NPuHNQYk+m+W9QeabSjpu1w+nTGXui" \
                      "+ViYIArfnfZylBa6oUvhSAw4l3w=="

    gw = PaymentGateway()
    gw._create_data("123456")
    gw._sign_data()

    assert gw.data["DIGEST"] == expected_digest.encode()
