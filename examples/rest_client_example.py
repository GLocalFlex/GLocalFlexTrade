# Example usage of the client library
import sys
from flxtrd import FlexAPIClient
from flxtrd import AuthPlugin, ListDevices
from flxtrd import User


# Example usage of the client library

def main():

    # make User
    user = User(name="",
                password="")
    GFLEX_API_URL = "localhost"

    client = FlexAPIClient(user=user, base_url=GFLEX_API_URL)

    response, err = client.make_request(method="POST",
                                        endpoint="/users/login", 
                                        data={"email": user.name, "password": user.password})
    
    if err:
          print(err)
          sys.exit(1)

    print(response.request_response.json())
    print(response.request_response.status_code)

if __name__ == "__main__":
        main()