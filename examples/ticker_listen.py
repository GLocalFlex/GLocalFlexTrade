import logging

from flxtrd import FlexAPIClient, FlexMarket, FlexUser

# create a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

def main() -> None:
    GLOCALFLEX_MARKET_URL = "glocalflexmarket.com"
    ACCESS_TOKEN = "<your_device_access_token>"

    trading_client = FlexAPIClient(market_url=GLOCALFLEX_MARKET_URL,
                                   access_token=ACCESS_TOKEN)
    trading_client.connect()

    # Check the market responses for closed_deals, price tick messages
    # from the message broker for 60 seconds and exit
    wait_sec = 0
    expected_responses = 1
    logger.info(f"Waiting for ticker messages from marketplace")

    while True:
        market_responses = trading_client.check_market_responses()
        if market_responses is not None:
            logger.info(f"Received {len(market_responses)} responses from market broker")
            # Close the connection to the market message broker
            if len(market_responses) >= expected_responses:
                break
            
        trading_client.sleep(1)
        
        wait_sec += 1
        logger.info(f"Waited {wait_sec} seconds")
        
    trading_client.disconnect()


    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Closing connection to the market broker")