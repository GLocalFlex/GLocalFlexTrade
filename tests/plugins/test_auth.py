import ssl
import pytest
from flxtrd import AuthPlugin, FlexUser, FlexMarket, AuthResponse
from flxtrd.core.plugins import auth
import copy
import requests

USER = FlexUser(name="12345@12345.fi",
                password="12345",
                access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NDk5NTRmNWVkYmYxYTMyNTUzMTFjZjgiLCJ1dWlkIjoiYjA1ZThiOWEtZDBhYy00ZmQwLWE1Y2ItMTUzMjI1YzgwMWY2IiwiaWF0IjoxNjg3NzcwMzk2LCJleHAiOjE3ODIzNzgzOTZ9.ogobAMJ83uvgzzetSBbt5oRRuKJdsjHM7KnBSp-SL4k"                  
                )

MARKET = FlexMarket(market_url="localhost")


def test_auth_plugin_instance():
    """Tests that the AuthPlugin class is created"""
    user = copy.deepcopy(USER)
    assert isinstance(AuthPlugin(user=user, market=MARKET), AuthPlugin)

def test_user_validate_access_token(requests_mock):
    """Tests that the user_authenticate method returns a response"""

    requests_mock.get(f'https://{MARKET.market_url}/users/mptoken/{USER.access_token}',
                      json={"userId": "12345", "locations": [{"_id": "12345"}]},
                      status_code=200
                        )
    
    user = copy.deepcopy(USER)
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

def test_user_validate_access_token_invalid_access_token_provided(requests_mock):
    """Tests that the user_authenticate method returns a response"""
    invalid_access_token = "invalid_access_token"
    
    requests_mock.get(f'https://{MARKET.market_url}/users/mptoken/{invalid_access_token}',
                      status_code=404
                        )
    

    user = copy.deepcopy(USER)
    user.access_token = invalid_access_token
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    response = auth_plugin.before_request()
    assert isinstance(response, AuthResponse), f"Response is not an AuthResponse is {type(response)}"
    assert response.is_authenticated is False, "Response should not be authenticated"

def test_user_authenticate_with_email_and_pw(requests_mock):
    """Tests that the user_authenticate method returns a response"""
    
    requests_mock.post(f'https://{MARKET.market_url}/users/login',
                    json={"userId": "12345", "locations": [{"_id": "12345", "token": "12345"}]},
                    status_code=200
                    )
    
    user = copy.deepcopy(USER)
    auth_plugin = AuthPlugin(user=user, market=MARKET, verify_ssl=False)
    response = auth_plugin.authenticate_user()
    assert isinstance(response, AuthResponse), f"Response is not an AuthResponse is {type(response)}" 
    assert response.is_authenticated is True, "Response should not be authenticated"

