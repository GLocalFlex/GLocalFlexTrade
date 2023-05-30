
# GLocalFlexTrade Public API

<!-- [![Release](https://img.shields.io/github/v/release/glocalflex/flxtrd)](https://img.shields.io/github/v/release/glocalflex/flxtrd)
[![Build status](https://img.shields.io/github/actions/workflow/status/glocalflex/flxtrd/main.yml?branch=main)](https://github.com/glocalflex/flxtrd/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd) -->

<!-- [![License](https://img.shields.io/github/license/glocalflex/flxtrd)](https://img.shields.io/github/license/glocalflex/flxtrd) -->

Public client API for the flexible energy trading market GLocalFlex Market.

The client libary provides standard interface to access the GLocalFlex Market public API. 
The client integrates Rest API and AMPQ protocol for communication with the GLocalFlex server. 


The **GLocalFlex Market** documentation is available here [GLocalFlex Market Documentation](https://www.glocalflex.com/docs)

Trade energy or offer flexible loads to the European energy market.

Install Python package

    pip install flxtrd

Import in to your trading client

    import flxtrd

You can use a sample trading client from the command line for testing 

    python -m flxtrd --help


## Basic Example

```py

from flxtrd import FlexAPIClient
from flxtrd import AuthPlugin


def main():

    API_BASE_URL = "localhost"

    client = FlexAPIClient(base_url=API_BASE_URL)
    client.add_plugin(AuthPlugin(app_token="secret"))

    response = client.make_request(method="POST", endpoint="/user/login")
    print(response)


if __name__ == "__main__":
        main()

```