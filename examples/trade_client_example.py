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

    user = FlexUser(
        name="<your_email>",
        password="<your_password>",
        accessToken="<your_device_access_token>",
    )
    
    market = FlexMarket(market_url=GLOCALFLEX_MARKET_URL)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(base_url=GLOCALFLEX_MARKET_URL, user=user, market=market)

    # Send a request to the GLocalFlex with REST API
    response, err = trading_client.make_request(
        method="POST",
        endpoint="/users/login",
        data={"email": user.name, "password": user.password},
    )
    if err:
        log(ERROR, err)

    log(INFO, pformat(response.request_response.json()))
    log(INFO, response.request_response.status_code)

    # add a 5 min offset from current time
    flex_resource = FlexResource(
        power_w=100,
        start_time_epoch_s=utils.utc_timestamp_s() + utils.min_to_s(5), 
        duration_min=60,  # start time + 60 minutes
        order_expiration_min=50,  # start time + 50 minutes
    )

    # Create a market order to sell flexibility and
    # define the tradable flexibility to sell or buy
    market_order = MarketOrder(order_type=ASK,
                               price_eur=100,
                               resource=flex_resource)

    # Send the market order to the message broker with AMPQ protocol
    # The connection to the market message broker will be initiated automatically
    _, err = trading_client.send_order(market_order=market_order,
                                       verify_ssl=False)
    # exit on error
    if err: log(ERROR, err)

    # Create a market order to sell flexibility
    market_order = MarketOrder(order_type=BID,
                               price_eur=100,
                               resource=flex_resource)

    # Send the market order to the message broker with AMPQ protocol
    # The connection to the market message broker will be initiated automatically
    _, err = trading_client.send_order(market_order=market_order,
                                       verify_ssl=False)
    
    if err: log(ERROR, err); sys.exit(1)

    try:
        wait_sec = 0
        while wait_sec < 60:
            market_responses = trading_client.check_market_responses()
            if market_responses is None:
                log(INFO, "No market responses received")
            else:
                log(INFO, f"Received {len(market_responses)} responses from message broker")
                # Close the connection to the market message broker

            time.sleep(1)
            wait_sec += 1

    except KeyboardInterrupt:
        log(INFO, "Keyboard interrupt received. Closing connection to the market message broker")
        trading_client.trade_protocol.close_connection()


if __name__ == "__main__":
    main()
