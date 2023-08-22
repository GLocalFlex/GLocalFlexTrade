import pytest
import os
from logging import DEBUG, INFO, WARNING, ERROR
import flxtrd
from flxtrd import FlexAPIClient, FlexUser, FlexMarket, AuthResponse, log
from flxtrd.core.plugins.auth import AuthPlugin
import copy

username=os.environ.get("FLEX_USERNAME")
password=os.environ.get("FLEX_PASSWORD")
market_url=os.environ.get("FLEX_MARKET_URL")
access_token=os.environ.get("FLEX_ACCESS_TOKEN")


# test flex api instance with a user pytest fixture
@pytest.fixture
def user():
    """Returns a FlexUser instance"""
    return FlexUser(name=username, password=password, access_token=access_token)

@pytest.fixture
def market():
    """Returns a FlexMarket instance"""
    return FlexMarket(market_url=market_url, market_port=80)


def test_flex_api_client_instance(user, market):
    """Tests that the FlexApiClient class is created"""
    assert isinstance(FlexAPIClient(user=user, market=market), FlexAPIClient)

def test_flex_api_client_instance_with_no_user(market):
    """Tests that the FlexApiClient class is created"""
    with pytest.raises(ValueError):
        FlexAPIClient(user=None, market=market)

def test_flex_api_client_instance_with_no_market(user):
    """Tests that the FlexApiClient class is created"""
    with pytest.raises(ValueError):
        FlexAPIClient(user=user, market=None)   

from unittest.mock import Mock
from flxtrd import AmpqAPI

@pytest.mark.skip("")
def test_flex_api_client_connect_valid_user_and_access_token(user, market):
    """"Test connection to message broker with valid user and access token"""
    usr = copy.deepcopy(user)
    AmpqAPI._connecttobrokerWithAppToken = Mock(return_value=None)
    AmpqAPI.set_consumer = Mock(return_value=None)
    AuthPlugin.before_request = Mock(return_value=None)

    client = FlexAPIClient(user=usr, market=market)
    assert client.connect() == None
    client.disconnect()
    
@pytest.mark.skip("")
def test_flex_api_client_connect_multiple_times_with_same_access_token(user, market):
    """Test connection to message broker with valid user and access token multiple times.
    Only one connection is allowed per access token"""
    user = copy.deepcopy(user)

    client = FlexAPIClient(user=user, market=market)
    assert client.connect() == None
    with pytest.raises(flxtrd.core.types.FlexError, match=r"No callback queue declared, That usually happens if more than one connection to the broker is opened") as flxerr:
        client.connect()
    client.disconnect()
    
@pytest.mark.skip("")
def test_flex_api_client_connect_invalid_user_and_access_token(market):
    """Tests that the FlexApiClient class is created"""
    user = FlexUser(name="invalid", password="invalid", access_token="invalid")
    client = FlexAPIClient(user=user, market=market)
    with pytest.raises(flxtrd.core.types.FlexError):
         client.connect()

        