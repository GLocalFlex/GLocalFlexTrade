# Example usage of the client library
import sys
from flxtrd import FlexAPIClient, AmpqAPI
from flxtrd import User, Market, Broker


# Example usage of the client library

def main():

    GFLEX_API_URL = "localhost"

    user = User(name="123@123.fi",
                password="12345",
                accessToken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDIxODY3NmRjNDJjNzE0YzFmMDgwNDEiLCJ1dWlkIjoiZjk3NTIzMGYtOWU3Yi00YjZlLWJhYjgtMTI1MjU2OGFlMDVkIiwiaWF0IjoxNjc5OTIwOTIyLCJleHAiOjE3NzQ1Mjg5MjJ9.CsPwTxcTDNIohdN6HH0weeHQI_gy8Y3STq_0inyRFGo'
                )
    market = Market(ip=GFLEX_API_URL,
                    broker=Broker(ip=GFLEX_API_URL,
                                port=5672)
                    )
    
    ampq_client = FlexAPIClient(base_url=GFLEX_API_URL,
                           protocol=AmpqAPI,
                           user=user)

    response, err = ampq_client.make_request(method="",
                                        endpoint="ask",
                                        ssl=True,
                                        user=user,
                                        market=market
                                        )
    
    if err:
          print(err)
          sys.exit(1)

    print(response.request_response.json())
    print(response.request_response.status_code)

if __name__ == "__main__":
        main()