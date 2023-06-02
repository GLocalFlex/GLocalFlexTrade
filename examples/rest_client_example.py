""" Example usage of the REST API client"""

import sys
from flxtrd import FlexAPIClient
from flxtrd import AuthPlugin, ListDevices
from flxtrd import User
from flxtrd import User, Market, Broker, MarketOrder, Flexibility, OrderType
from flxtrd import log
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL


def main():

    GFLEX_API_URL = "localhost"

    # Define types for the user, market and message broker
    user = User(name="",
                password="",
                accessToken="")
    
    market = Market(ip=GFLEX_API_URL,
                    broker=Broker(ip=GFLEX_API_URL))

    # Create a REST client
    rest_client = FlexAPIClient(base_url=GFLEX_API_URL,
                                user=user,
                                market=market)    

    # Send a request to the GLocalFlex REST API
    response, err = rest_client.make_request(method="POST",
                                        endpoint="/users/login", 
                                        data={"email": user.name, "password": user.password})
    
    if err:
          log(ERROR, err)
          sys.exit(1)

    log(INFO, response.request_response.json())
    log(INFO, response.request_response.status_code)

if __name__ == "__main__":
        main()