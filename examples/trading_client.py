"""Example usage of the trading client using AMPQ protocol"""
import logging
import sys
import time
from typing import List
from urllib import request

from flxtrd import (
    ASK,
    BID,
    FlexAPIClient,
    FlexMarket,
    FlexResource,
    FlexUser,
    MarketOrder,
    utils,
)

# create a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def market_response(responses: List, expected: int) -> None:
    if responses is not None:
        logger.info(f"Received {len(responses)} responses from market broker")
        if len(responses) == expected:
            return True
        return False

def main() -> None:

    GLOCALFLEX_MARKET_URL = "glocalflexmarket.com"
    ACCESS_TOKEN = "<your_device_access_token>"

    trading_client = FlexAPIClient(market_url=GLOCALFLEX_MARKET_URL,
                                   access_token=ACCESS_TOKEN)
    trading_client.connect()

    # Define a flexibility resource that will be traded
    # The resource is a 100W power for 60 minutes starting in 5 minutes
    flex_resource = FlexResource(
        power_w=100,
        start_time_epoch_s=utils.utc_timestamp_s() - utils.min_to_s(5),
        duration_min=60,
        order_expiration_min=50,
    )

    # Create a market ask order to sell flexibility
    market_order = MarketOrder(order_type=ASK, price_eur=100, resource=flex_resource)

    # Send the market order to the message broker
    # The connection to the broker will be initiated automatically
    _, err = trading_client.send_order(market_order=market_order)

    if err:
        logger.error(err)

    # Create a market bid order to buy flexibility
    market_order = MarketOrder(order_type=BID, price_eur=100, resource=flex_resource)

    _, err = trading_client.send_order(market_order=market_order)

    if err:
        logger.error(err)
        sys.exit(1)

    # Check the market responses for closed_deals, price tick messages
    # from the message broker for 60 seconds and exit
    wait_sec = 0
    expected_responses = 3
    logger.info(f"Waiting for messages from market broker")

    try:
        while wait_sec < 60:
            if market_response(responses=trading_client.check_market_responses(),
                               expected=expected_responses):
                break

            time.sleep(1)
            wait_sec += 1

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Closing connection to the market broker")
    finally:
        trading_client.trade_protocol.close_connection()


if __name__ == "__main__":
    main()
