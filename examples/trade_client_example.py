"""Example usage of the trading client using AMPQ protocol"""
import sys
import time
from logging import ERROR, INFO
from pprint import pformat
from random import random

from flxtrd import (
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

    user = User(
        name="<your_email>",
        password="<your_password>",
        accessToken="<your_device_access_token>",
    )

    market = Market(ip=GFLEX_API_URL, broker=Broker(ip=GFLEX_API_URL))

    # Define the tradable flexibility to sell or buy
    flexResource = Flexibility(
        wattage=random() * 100,
        starttime=int((time.time() + (60 * 60 * random() * 10)) / 60) * 60 * 1000,
        duration=int(((round(random()) * 14 + 1) / 60.0) * 60 * 60 * 1000),
        expirationtime=int(time.time() / (60 * 1000) + random() * 20) * 60 * 1000,
    )

    # Create a market order to sell or buy flexibility
    market_order = MarketOrder(type=OrderType.ASK, price=100, flexibility=flexResource)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(base_url=GFLEX_API_URL, user=user, market=market)

    # Send a request to the GLocalFlex with REST API
    response, err = trading_client.make_request(
        method="POST",
        endpoint="/users/login",
        data={"email": user.name, "password": user.password},
    )

    if err:
        log(ERROR, err)
        sys.exit(1)

    log(INFO, pformat(response.request_response.json()))
    log(INFO, response.request_response.status_code)

    # Send the market order to the message broker with AMPQ protocol
    # The connection to the market message broker will be initiated automatically
    response, err = trading_client.send_order(
        method="",
        verify_ssl=False,
        order=market_order,
    )

    if err:
        log(ERROR, err)
        sys.exit(1)

    log(INFO, "Received response from message broker")
    log(INFO, response.order_response)

    # Send the market order to the message broker with AMPQ protocol
    # The connection to the market message broker will be initiated automatically
    response, err = trading_client.send_order(
        method="",
        verify_ssl=False,
        order=market_order,
    )

    if err:
        log(ERROR, err)
        sys.exit(1)

    log(INFO, "Received response from message broker")
    log(INFO, response.order_response)

    # Close the connection to the market message broker
    trading_client.trade_protocol.close_connection()


if __name__ == "__main__":
    main()
