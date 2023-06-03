# GLocalFlexTrade Public API

Public client API for the flexible energy trading market GLocalFlex.
Trade energy or offer flexible loads to the European energy market.

[![Release](https://img.shields.io/github/v/release/glocalflex/flxtrd)](https://img.shields.io/github/v/release/glocalflex/flxtrd)
[![Build status](https://img.shields.io/github/actions/workflow/status/glocalflex/flxtrd/main.yml?branch=main)](https://github.com/glocalflex/flxtrd/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/glocalflex/flxtrd/branch/main/graph/badge.svg)](https://codecov.io/gh/glocalflex/flxtrd)
[![Commit activity](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)
[![License](https://img.shields.io/github/license/glocalflex/flxtrd)](https://img.shields.io/github/license/glocalflex/flxtrd)


[GLocalFlexTrade](https://glocalflex.github.io/GLocalFlexTrade/) **Documentation** provides information how to use the **flxtrd** Python package.

The official GLocalFlex Market [API Documentation](https://www.glocalflexmarket.com/docs/) gives an overview and more details of the public API and energy trading platform.

## Getting started with GLocalFlexTrade


Install GLocalFlexTrade Python package

```sh
pip install flxtrd
```
### Basic Example

```py
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
        endpoint="ask",
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
        endpoint="bi",
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

```
