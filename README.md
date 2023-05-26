# GLocalFlexTrade Public API 

Public client API for the flexible energy trading market GLocalFlex.
Trade energy or offer flexible loads to the European energy market.

[![Release](https://img.shields.io/github/v/release/glocalflex/flxtrd)](https://img.shields.io/github/v/release/glocalflex/flxtrd)
[![Build status](https://img.shields.io/github/actions/workflow/status/glocalflex/flxtrd/main.yml?branch=main)](https://github.com/glocalflex/flxtrd/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/glocalflex/flxtrd/branch/main/graph/badge.svg)](https://codecov.io/gh/glocalflex/flxtrd)
[![Commit activity](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)](https://img.shields.io/github/commit-activity/m/glocalflex/flxtrd)
[![License](https://img.shields.io/github/license/glocalflex/flxtrd)](https://img.shields.io/github/license/glocalflex/flxtrd)


- **Github repository**: <https://github.com/glocalflex/GLocalFlexTrade/>

## Getting started with GLocalFlexTrade

- **Documentation** <https://glocalflex.github.io/GLocalFlexTrade/>

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


# Development

