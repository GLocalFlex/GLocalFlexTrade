from logging import ERROR, INFO

from flxtrd import (
    FlexAPIClient,
    FlexMarket,
    FlexUser,
    log,

)

def main() -> None:
    GLOCALFLEX_MARKET_URL = "glocalflexmarket.com"

    user = FlexUser(name="123@123.fi",
                    password="12345",
                    access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDg3NWM3Mjc2YTQzOTI4ZWJlNGVjMjUiLCJ1dWlkIjoiY2Y5MjI3YTQtNWU1My00MDJjLTkxMjYtZjA1ZTc5NTg5YTUxIiwiaWF0IjoxNjg2NjUzNDE4LCJleHAiOjE3ODEyNjE0MTh9.LjMzKW29OhGlW0vlPYIRV9yZMY-FdHCZnWBVeuLG_uM",
                    )

    market = FlexMarket(market_url=GLOCALFLEX_MARKET_URL)

    # Create a AMPQ client that connects to the message broker
    trading_client = FlexAPIClient(user=user,
                                   market=market,
                                   )

    
    trading_client.connect()

    # Check the market responses for closed_deals, price tick messages
    # from the message broker for 60 seconds and exit
    wait_sec = 0
    expected_responses = 1
    log(INFO, f"Waiting for ticker messages from marketplace")


    while True:
        log(INFO, f"Waited {wait_sec} seconds")
        market_responses = trading_client.check_market_responses()
        if market_responses is not None:
            log(INFO, f"Received {len(market_responses)} responses from market broker")
            # Close the connection to the market message broker
            if len(market_responses) == expected_responses:
                break
            
        trading_client.sleep(1)
        wait_sec += 1
        
    trading_client.disconnect()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log(INFO, "Keyboard interrupt received. Closing connection to the market broker")

