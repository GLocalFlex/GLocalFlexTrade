""" Example usage of the REST API client"""

import sys
from logging import ERROR, INFO

from flxtrd import Broker, FlexAPIClient, Market, User, log


def main():
    GFLEX_API_URL = "localhost"

    # Define types for the user, market and message broker
    user = User(
        name="123@123.fi",
        password="12345",
        accessToken="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDIxODY3NmRjNDJjNzE0YzFmMDgwNDEiLCJ1dWlkIjoiZjk3NTIzMGYtOWU3Yi00YjZlLWJhYjgtMTI1MjU2OGFlMDVkIiwiaWF0IjoxNjc5OTIwOTIyLCJleHAiOjE3NzQ1Mjg5MjJ9.CsPwTxcTDNIohdN6HH0weeHQI_gy8Y3STq_0inyRFGo",  # noqa
    )

    market = Market(ip=GFLEX_API_URL, broker=Broker(ip=GFLEX_API_URL))

    # Create a REST client
    rest_client = FlexAPIClient(base_url=GFLEX_API_URL, user=user, market=market)

    # Send a request to the GLocalFlex REST API
    response, err = rest_client.make_request(
        method="POST",
        endpoint="/users/login",
        data={"email": user.name, "password": user.password},
    )

    if err:
        log(ERROR, err)
        sys.exit(1)

    log(INFO, response.request_response.json())
    log(INFO, response.request_response.status_code)


if __name__ == "__main__":
    main()
