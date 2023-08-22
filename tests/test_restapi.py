import pytest
import requests

from flxtrd.protocols.rest import RestAPI

"""
Use REST-calls like these:
http://wotan.ad.vtt.fi:3333/asks
http://wotan.ad.vtt.fi:3333/asks/?startTime=2019-11-13T12:00:00Z&duration=0.5
http://wotan.ad.vtt.fi:3333/asks/?appkeys=["5dbc1d4e4c2c8b6909af595e"]

http://wotan.ad.vtt.fi:3333/bids
http://wotan.ad.vtt.fi:3333/bids/?startTime=2019-11-13T12:00:00Z&duration=0.5
http://wotan.ad.vtt.fi:3333/bids/?appkeys=["5dbc1d4e4c2c8b6909af595e"]

http://localhost:3000/locations/owner/'+uid

fetch('http://localhost:3000/messages/user/'+uid
fetch('http://localhost:3000/orders/customer/'+cid

app.use('/products', productRoutes);
app.use('/orders', orderRoutes);
app.use('/users', userRoutes);
app.use('/messages', messageRoutes);
app.use('/locations', locationRoutes);

app.use('/bids', bidRoutes);
app.use('/asks', askRoutes);
app.use('/deals', dealsRoutes);
app.use('/latencies', latenciesRoutes);
app.use('/iota', iotaRoutes);
"""


@pytest.fixture
def create_rest_api_instance(base_url="localhost"):
    """Creates a RestAPI instance"""
    return RestAPI(base_url=base_url)


def test_restapi_instance(create_rest_api_instance):
    """Tests that a RestAPI instance is created"""
    assert isinstance(create_rest_api_instance, RestAPI)


# paramaterize the test with different endpoints
# and expected status codes
@pytest.mark.skip()
@pytest.mark.parametrize(
    "endpoint, expected_status_code, ssl",
    [
        ("/", 200, False),
        ("/", 200, True),
        ("/users/login", 200, False),
        ("/users/login", 200, True),
    ],
)
def test_restapi_send_request(create_rest_api_instance, endpoint, expected_status_code, ssl):
    """Tests that the send_request method returns a response"""
    response, error = create_rest_api_instance.send_request(
        method="GET", endpoint=endpoint, ssl=ssl, verify_ssl=False
    )
    assert isinstance(response, requests.Response)
    assert not error, f"{error, response}"
    assert (
        response.status_code == expected_status_code
    ), f"Received status code: {response.status_code} instead of {expected_status_code}"


def test_api_not_accessible(create_rest_api_instance: RestAPI):
    """Tests that the send_request method returns a response"""
    response, error = create_rest_api_instance.send_request(
        method="GET", endpoint="/users/login", ssl=True, verify_ssl=False
    )
    assert {} == response
    assert error == "Connection to api endpoint https://localhost/users/login failed"