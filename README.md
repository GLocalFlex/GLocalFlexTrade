# GLocalFlexTrade Public API 

Public client API for the flexible energy trading market GLocalFlex.
Trade energy or offer flexible loads to the European energy market.

[![Release](https://img.shields.io/github/v/release/glocalflex/flxtrd)](https://img.shields.io/github/v/release/glocalflex/flxtrd)
[![Build status](https://img.shields.io/github/actions/workflow/status/glocalflex/flxtrd/main.yml?branch=main)](https://github.com/glocalflex/flxtrd/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/glocalflex/flxtrd/branch/main/graph/badge.svg)](https://codecov.io/gh/glocalflex/flxtrd)
[![Commit activity](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)
[![License](https://img.shields.io/github/license/glocalflex/flxtrd)](https://img.shields.io/github/license/glocalflex/flxtrd)


[GLocalFlexTrade](https://glocalflex.github.io/GLocalFlexTrade/) **Documentation** provides information how to use the the **flxtrd** Python package. 

The official GLocalFlex Market [API Documentation](https://www.glocalflexmarket.com/docs/) gives an overview and more details of the public API and energy trading platform.

## Getting started with GLocalFlexTrade


Install GLocalFlexTrade Python package

```sh
pip install flxtrd
```
### Basic Rest API Example

```py
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
                accessToken='')
    
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
```

### Basic Trade Example connecting to the market message broker

```py
"""Example usage of the trading client using AMPQ protocol"""
import sys
import time
from random import random
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL

from flxtrd import log
from flxtrd import FlexAPIClient, AmpqAPI
from flxtrd import User, Market, Broker, MarketOrder, Flexibility, OrderType


def main():

    GFLEX_API_URL = "localhost"
    FLEXMQ_TLS_PORT = 5671

    user = User(name="",
                password="",
                accessToken="")
    
    market = Market(ip=GFLEX_API_URL,
                    broker=Broker(ip=GFLEX_API_URL, port=FLEXMQ_TLS_PORT))
    
    # Define the tradable flexibility to sell or buy
    flex = Flexibility(wattage = random() * 100,
                        starttime = int((time.time() + (60 * 60 * random() * 10)) / 60) * 60 * 1000,
                        duration = int(((round(random()) * 14 + 1) / 60.0) * 60 * 60 * 1000),
                        expirationtime = int(time.time() / (60 * 1000) + random() * 20) * 60 * 1000)

    # Create a market order to sell or buy flexibility
    market_order = MarketOrder(type=OrderType.ASK,
                        price=100,
                        flexibility=flex)

    # Create a AMPQ client that connects to the message broker
    ampq_client = FlexAPIClient(base_url=GFLEX_API_URL,
                                protocol=AmpqAPI,
                                user=user,
                                market=market
                                )

    # Send the market order to the message broker
    response, err = ampq_client.make_request(method="",
                                        endpoint="ask",
                                        ssl=True,
                                        verify_ssl=False,
                                        order=market_order,
                                        )
    
    if err:
          log(ERROR, err)
          sys.exit(1)

    log(INFO, "Received response from message broker")
    log(INFO, response)


if __name__ == "__main__":
        main()

```

# Development

export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring