import ssl
import pytest
from flxtrd import AuthPlugin, FlexUser, FlexMarket, AuthResponse
from flxtrd.core.plugins import auth
import copy

USER = FlexUser(name="12345@12345.fi",
                password="12345",
                access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDk5NTRmNWVkYmYxYTMyNTUzMTFjZjgiLCJ1dWlkIjoiYjA1ZThiOWEtZDBhYy00ZmQwLWE1Y2ItMTUzMjI1YzgwMWY2IiwiaWF0IjoxNjg3NzcwMzk2LCJleHAiOjE3ODIzNzgzOTZ9.ogobAMJ83uvgzzetSBbt5oRRuKJdsjHM7KnBSp-SL4k"                  
                )

MARKET = FlexMarket(market_url="localhost")



def test_auth_plugin_instance():
    """Tests that the AuthPlugin class is created"""
    user = copy.deepcopy(USER)
    assert isinstance(AuthPlugin(user=user, market=MARKET), AuthPlugin)

def test_user_validate_access_token():
    """Tests that the user_authenticate method returns a response"""
    user = copy.deepcopy(USER)
    assert user.access_token is not None, "user access_token is None"
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    auth_plugin.before_request()
    assert user.app_key is not None, "User app_key is None"


def test_user_validate_access_token_no_access_token_provided():
    """Tests that the user_authenticate method returns a response"""

    user = copy.deepcopy(USER)
    user.access_token = None
    assert user.access_token is None, "User access_token is None"
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    with pytest.raises(ValueError):
        auth_plugin.before_request()

def test_user_validate_access_token_invalid_access_token_provided():
    """Tests that the user_authenticate method returns a response"""

    user = copy.deepcopy(USER)
    user.access_token = "Not a valid access token"
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    response = auth_plugin.before_request()
    assert isinstance(response, AuthResponse), f"Response is not an AuthResponse is {type(response)}"
    assert response.is_authenticated is False, "Response should not be authenticated"

def test_user_authenticate_with_email_and_pw():
    """Tests that the user_authenticate method returns a response"""
    user = copy.deepcopy(USER)
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    response = auth_plugin.authenticate_user()
    assert isinstance(response, AuthResponse), f"Response is not an AuthResponse is {type(response)}" 
    assert response.is_authenticated is True, "Response should not be authenticated"

