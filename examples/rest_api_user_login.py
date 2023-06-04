"""Example usage of the trading client using AMPQ protocol"""
import signal
import sys
import time
from logging import ERROR, INFO
from pprint import pformat

from flxtrd import (
    ASK,
    BID,
    FlexBroker,
    FlexAPIClient,
    FlexResource,
    FlexMarket,
    MarketOrder,
    FlexUser,
    log,
    utils,
)


def main() -> None:
    GLOCALFLEX_MARKET_URL = "localhost"

    user = FlexUser(name="<your_email>",
                    password="<your_password>",
                    access_token="<your_device_access_token>"
                    )

    
    market = FlexMarket(market_url=GLOCALFLEX_MARKET_URL)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(base_url=GLOCALFLEX_MARKET_URL,
                                   user=user,
                                   market=market
                                   )

    # Send a request to the GLocalFlex with REST API
    response, err = trading_client.make_request(method="POST",
                                                endpoint="/users/login",
                                                data={"email": user.name, "password": user.password},
                                                )
    if err:
        log(ERROR, err)

    log(INFO, pformat(response.request_response.json()))
    log(INFO, response.request_response.status_code)


if __name__ == "__main__":
    main()
