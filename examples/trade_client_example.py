"""Example usage of the trading client using AMPQ protocol"""
import sys
import time
from logging import ERROR, INFO
from random import random

from flxtrd import (
    AmpqAPI,
    Broker,
    FlexAPIClient,
    Flexibility,
    Market,
    MarketOrder,
    OrderType,
    User,
    log,
)


def main() -> None:
    GFLEX_API_URL = "localhost"
    FLEXMQ_TLS_PORT = 5671

    user = User(
        name="123@123.fi",
        password="12345",
        accessToken="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDIxODY3NmRjNDJjNzE0YzFmMDgwNDEiLCJ1dWlkIjoiZjk3NTIzMGYtOWU3Yi00YjZlLWJhYjgtMTI1MjU2OGFlMDVkIiwiaWF0IjoxNjc5OTIwOTIyLCJleHAiOjE3NzQ1Mjg5MjJ9.CsPwTxcTDNIohdN6HH0weeHQI_gy8Y3STq_0inyRFGo", # noqa
    )

    market = Market(
        ip=GFLEX_API_URL, broker=Broker(ip=GFLEX_API_URL, port=FLEXMQ_TLS_PORT)
    )

    # Define the tradable flexibility to sell or buy
    flex = Flexibility(
        wattage=random() * 100,
        starttime=int((time.time() + (60 * 60 * random() * 10)) / 60) * 60 * 1000,
        duration=int(((round(random()) * 14 + 1) / 60.0) * 60 * 60 * 1000),
        expirationtime=int(time.time() / (60 * 1000) + random() * 20) * 60 * 1000,
    )

    # Create a market order to sell or buy flexibility
    market_order = MarketOrder(type=OrderType.ASK, price=100, flexibility=flex)

    # Create a AMPQ client that connects to the message broker
    ampq_client = FlexAPIClient(
        base_url=GFLEX_API_URL, protocol=AmpqAPI, user=user, market=market
    )

    # Send the market order to the message broker
    response, err = ampq_client.make_request(
        method="",
        endpoint="ask",
        ssl=True,
        verify_ssl=False,
        order=market_order,
    )

    if err:
        log(ERROR, err)
        sys.exit(1)

    log(INFO, "Received response from message broker")
    log(INFO, response)


if __name__ == "__main__":
    main()
