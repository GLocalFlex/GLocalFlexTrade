"""Example usage of the trading client using AMPQ protocol"""
import sys
import time
from logging import ERROR, INFO

from flxtrd import (
    ASK,
    BID,
    FlexAPIClient,
    FlexMarket,
    FlexResource,
    FlexUser,
    MarketOrder,
    log,
    utils,
)


def main() -> None:
    GLOCALFLEX_MARKET_URL = "localhost"

    user = FlexUser(
        name="<your_email>",
        password="<your_password>",
        access_token="<your_device_access_token>",
    )

    market = FlexMarket(market_url=GLOCALFLEX_MARKET_URL)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(user=user, market=market)

    # Define a flexibility resource that will be traded
    # The resource is a 100W power for 60 minutes starting in 5 minutes
    flex_resource = FlexResource(
        power_w=100,
        start_time_epoch_s=utils.utc_timestamp_s() + utils.min_to_s(5),
        duration_min=60,
        order_expiration_min=50,
    )

    # Create a market ask order to sell flexibility
    market_order = MarketOrder(order_type=ASK,
                               price_eur=100,
                               resource=flex_resource)

    # Send the market order to the message broker
    # The connection to the broker will be initiated automatically
    _, err = trading_client.send_order(market_order=market_order)

    if err:
        log(ERROR, err)

    # Create a market bid order to buy flexibility
    market_order = MarketOrder(order_type=BID, price_eur=100, resource=flex_resource)

    _, err = trading_client.send_order(market_order=market_order)

    if err:
        log(ERROR, err)
        sys.exit(1)

    # Check the market responses for closed_deals, price tick messages
    # from the message broker for 60 seconds and exit
    wait_sec = 0
    expected_responses = 3
    log(INFO, f"Waiting for messages from market broker")

    try:
        while wait_sec < 60:
            market_responses = trading_client.check_market_responses()
            if market_responses is not None:
                log(INFO, f"Received {len(market_responses)} responses from market broker")
                # Close the connection to the market message broker
                if len(market_responses) == expected_responses:
                    break

            time.sleep(1)
            wait_sec += 1

    except KeyboardInterrupt:
        log(INFO, "Keyboard interrupt received. Closing connection to the market broker")
    finally:
        trading_client.trade_protocol.close_connection()


if __name__ == "__main__":
    main()
