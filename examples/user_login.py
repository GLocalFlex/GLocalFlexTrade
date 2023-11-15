"""Example usage of the REST API client"""

import json
import logging
import sys

from flxtrd import FlexAPIClient, FlexMarket, FlexUser

# create a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main() -> None:
    GLOCALFLEX_MARKET_URL = "localhost"

    user = FlexUser(
        name="<your_email>", password="<your_password>", access_token="<your_device_access_token>"
    )

    market = FlexMarket(market_url=GLOCALFLEX_MARKET_URL)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(user=user, market=market)

    # Send a request to the GLocalFlex with REST API
    response, err = trading_client.make_request(
        method="POST",
        endpoint="/users/login",
        data={"email": user.name, "password": user.password},
    )
    if err:
        logger.error(err)
        sys.exit(1)

    logger.info(json.dumps(response.request_response.json(), indent=4))
    logger.info(response.request_response.status_code)


if __name__ == "__main__":
    main()
