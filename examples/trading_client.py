"""Example usage of the trading client using AMPQ protocol"""

import logging
import os
import sys
import time
from typing import List
import json

from flxtrd import (
    ASK,
    BID,
    FlexAPIClient,
    FlexResource,

    MarketOrder,
    utils,
)

# create a basic logger
logger = logging.getLogger("flxtrd")
logger.setLevel(logging.INFO)


def handle_market_responses(responses: List, expected: int) -> None:
    """
    Custom handler for market responses
    
    Extend with your own logic.
    
    There are 3 types of responses:
    
    ask_closed_order
    bid_closed_order
    tick
    
    Examples:
    

    INFO flxtrd 2023-11-15 12:56:14,486 | trading_client.py:40 |  {
    "trade_time": "2023-11-15T10:56:14.226Z",
    "price": 100.0,
    "start_time": "2023-11-15T11:01:13.000Z",
    "energy": 100.0,
    "msg_type": "tick"
    }
    INFO flxtrd 2023-11-15 12:56:14,486 | trading_client.py:39 | Received message type: ask_closed_order
    INFO flxtrd 2023-11-15 12:56:14,486 | trading_client.py:40 |  {
        "msg_type": "ask_closed_order",
        "application_key": "***",
        "closed_order": {
            "bid_time": 1700045773535373405,
            "ask_time": 1700045773533945086,
            "ask_user": "6490252462817c189578807a",
            "bid_user": "6490252462817c189578807a",
            "price": 100.0,
            "totalenergy": 100.0,
            "energy": 100.0,
            "starttime": 1700046073000,
            "endtime": 1700049673000.0,
            "runtime": 3600000,
            "wattage": 100.0,
            "power": 100.0,
            "match_time": 1700045774226012928
        }
    }
    INFO flxtrd 2023-11-15 12:56:14,486 | trading_client.py:39 | Received message type: bid_closed_order
    INFO flxtrd 2023-11-15 12:56:14,486 | trading_client.py:40 |  {
        "msg_type": "bid_closed_order",
        "application_key": "***",
        "closed_order": {
            "bid_time": 1700045773535373405,
            "ask_time": 1700045773533945086,
            "ask_user": "6490252462817c189578807a",
            "bid_user": "6490252462817c189578807a",
            "price": 100.0,
            "totalenergy": 100.0,
            "energy": 100.0,
            "starttime": 1700046073000,
            "endtime": 1700049673000.0,
            "runtime": 3600000,
            "wattage": 100.0,
            "power": 100.0,
            "match_time": 1700045774226012928
        }
    }
    
    """
    if responses is not None:
        logger.info(f"Handle new responses from market broker")
        for response in responses:
            logger.info(f"Received message type: {response.get('msg_type')}")
            logger.info(f" {json.dumps(response, indent=4)}")
        if len(responses) == expected:
            return True
        return False


def main() -> None:
    GLOCALFLEX_MARKET_URL = "glocalflexmarket.com"
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "invalid_token")
    # ACCESS_TOKEN = "<your_device_access_token>"

    trading_client = FlexAPIClient(market_url=GLOCALFLEX_MARKET_URL, access_token=ACCESS_TOKEN)
    trading_client.connect()

    # Define a flexibility resource that will be traded
    # The resource is a 100W power for 60 minutes starting in 5 minutes
    flex_resource = FlexResource(
        power_w=100,
        start_time_epoch_s=utils.utc_timestamp_s() + utils.min_to_s(5),
        duration_min=60,
        order_expiration_min=50,
    )

    # Create a market ask order to sell flexibility
    ask_order = MarketOrder(order_type=ASK, price_eur=100, resource=flex_resource)

    # Send the market order to the message broker
    # The connection to the broker will be initiated automatically
    _, err = trading_client.send_order(market_order=ask_order)

    if err:
        logger.error(err)

    # Create a market bid order to buy flexibility
    bid_order = MarketOrder(order_type=BID, price_eur=100, resource=flex_resource)

    _, err = trading_client.send_order(market_order=bid_order)

    if err:
        logger.error(err)
        sys.exit(1)

    # Wait for the market broker to respond
    wait_sec = 0
    expected_responses = 3
    logger.info(f"Waiting for messages from market broker")
    market_responses = []
    try:
        while wait_sec < 10:
            if trading_client.check_market_responses() is not None:
                market_responses.extend(trading_client.check_market_responses())
                # Empty the market responses after retrieving to avoid keeping all the messages in memory
                # of the trading client
                trading_client.empty_market_responses()
            
            # Plug in your custom logic to handle the market responses
            # see details in function handle_market_responses()
            if handle_market_responses(responses=market_responses, expected=expected_responses):
                logger.info(f"Received total of {len(market_responses)} responses from market broker")
                break

            time.sleep(1)
            wait_sec += 1

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Closing connection to the market broker")
    finally:
        trading_client.trade_protocol.close_connection()


if __name__ == "__main__":
    main()
