"""
Example: Client listening to the market broker for ticker messages
The client automatically listens for ticker messages when connected to the marketplace.

This connection can also be used to submit orders to the marketplace.
"""

import logging
import os
import json
from flxtrd import FlexAPIClient

# create a basic logger
logger = logging.getLogger("flxtrd")
logger.setLevel(logging.INFO)


def main() -> None:
    GLOCALFLEX_MARKET_URL = "glocalflexmarket.com"
    # ACCESS_TOKEN = "<your_device_access_token>"
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "invalid_token")

    trading_client = FlexAPIClient(market_url=GLOCALFLEX_MARKET_URL,
                                   access_token=ACCESS_TOKEN)
    trading_client.connect()

    logger.info(f"Waiting for ticker messages from marketplace")
    market_responses = []
    while True:
        if trading_client.check_market_responses() is not None:
            market_responses.extend(trading_client.check_market_responses())
            # Empty the market responses after retrieving to avoid keeping all the messages in memory
            # of the trading client
            trading_client.empty_market_responses()
            
        for response in market_responses:
            logger.info(f"Received message type: {response.get('msg_type')}")
            logger.info(f" {json.dumps(response, indent=4)}")
            logger.info(f"Received {len(market_responses)} responses from market broker")
            
            # reset the market responses
            market_responses = []
       
        trading_client.sleep(1)
        logger.info(f"Waited for new ticker messages")
        
        # this will run forever
        

    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Closing connection to the market broker")


if __name__ == "__main__":
    main()