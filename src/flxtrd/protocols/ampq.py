from sys import float_info
import requests
import time
import ssl as _ssl
import pika
import json
from flxtrd.core.types import Broker, Market, User, FlexError

from typing import List, Optional

from flxtrd.core.plugins.base import BasePlugin
from flxtrd.protocols.base import BaseAPI
from random import random


class AmpqAPI(BaseAPI):
    """Amqp API implementation that connects to public API"""
    
    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    def send_request(self,
                     endpoint: str,
                     params: Optional[dict] = None,
                     data: Optional[dict] = None,
                     ssl: Optional[bool] = False,
                     **kwargs) -> dict:
        
        if not "market" in kwargs:
            raise FlexError("Market not found request arguments")
        if not "user" in kwargs:
            raise FlexError("User not found in request arguments")

        market: Market = kwargs["market"]
        user: User = kwargs["user"]
        context = _ssl.create_default_context()

        price = 1
        starttime = int((time() + (60 * 60 * random() * 10)) / 60) * 60 * 1000
        wattage = random() * 100
        duration = int(((round(random()) * 14 + 1) / 60.0) * 60 * 60 * 1000)
        
        DEV=True 
        if DEV:
            # Disable ssl verfication for development with self signed certificates
            context.check_hostname = False
            context.verify_mode = _ssl.CERT_NONE
            VERIFY_SSL = False
        else:
            VERIFY_SSL = True

        ssl_options = pika.SSLOptions(context)
    
        user, connection, channel, callback_queue = connecttobrokerWithAppToken(user=user,
                                        broker=market.broker)

        if endpoint == "ask":
            routingkey = "ask"

        elif endpoint == "bid":
            routingkey = "bid"

        else:
            err = FlexError("Endpoint not found")

        totenergy = wattage * (duration / (60 * 60 *1000))
        msg = getLineMessage(endpoint,
                            user.appkey,
                            wattage,
                            duration,
                            starttime,
                            totenergy,
                            price,
                            starttime).strip('"')
        
        sendmsg(msg)

        time.sleep(1)
        replies = checkreplies()
 
        return replies, err

def checkreplies(connection):
    connection.process_data_events()

def validateApplicationToken(authServer, appToken, verify_ssl=True):
    appAuthUrl = f'https://{authServer}/users/mptoken/{appToken}'
    userId = ""
    applicationKey = ""
    response = requests.get(appAuthUrl, verify=verify_ssl)
    if response.status_code == 200:
        userId = response.json()['userId']
        if 'locations' in response.json().keys():
            if len(response.json()['locations']) > 0:
                applicationKey = response.json()['locations'][0]['_id']
            else:
                print(f'Failed to validate applicationToken {appToken}')
        print(f'Application token {appToken} successfully validated with applicationKey {applicationKey}')
    else:
        print(f'Failed to validate applicationToken {appToken}')
    return userId, applicationKey



def getcurrenttimems():
    return  int(time.time()*1000)

def declareReplyToQueue(channel, applicationKey, tickeroutexname):
    try:
        dec_res = channel.queue_declare(applicationKey, exclusive=True)
        callback_queue = dec_res.method.queue
        channel.queue_bind(callback_queue, tickeroutexname)
        print("Creating "+str(applicationKey))
        print("Created "+str(callback_queue))
        return callback_queue
    except pika.exceptions.ChannelClosedByBroker:
        print("ReplyTo queue creation failed "+applicationKey)

def connecttobrokerWithAppToken(user: User,
                                broker: Broker,
                                tickeroutexname: str,
                                ssl_options: pika.SSLOptions,
                                brokerport:int = 5671):
    authServer=broker.brokerip # TODO: This should be the auth server
    brokerip=broker.brokerip
    accessToken =user.accessToken
    tickeroutexname = broker.tickeroutexname
    userid, applicationKey = validateApplicationToken(authServer, accessToken)

    credentials = pika.PlainCredentials(userid, accessToken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials, ssl_options=ssl_options)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    callback_queue = declareReplyToQueue(channel, applicationKey, tickeroutexname)
    return connection, channel, callback_queue

def setreceiver(callback, callback_queue, channel):
    channel.basic_consume(queue=callback_queue, on_message_callback=callback, auto_ack=True)

def checkreplies(connection):
    connection.process_data_events()

def closeconnection(connection):
    connection.close()

def sendmsg(msg,
            callback_queue,
            userid: str,
            channel: pika.channel.Channel,
            routingkey: str, 
            exchangename: str):
    """Send message to the broker"""
    props = pika.BasicProperties(user_id=userid, reply_to=callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    channel.basic_publish(exchange=exchangename, routing_key=routingkey, properties=props, body=msg)

def getLineMessage(endpoint: str,
                   applicationKey: str,
                   wattage: float, 
                   duration: int,
                   starttime: int, 
                   totalenergy: float, 
                   price: float, 
                   expirationtime:int):
    """Create a line protocol message for InfluxDB that is the payload in the AMQP message"""
    linemsg = createLineMessage(endpoint, applicationKey, wattage, duration, starttime, totalenergy, price, expirationtime)
    return json.dumps(linemsg)


def createLineMessage(order, applicationKey, wattage, duration, starttime, totalenergy, orderprice, expirationtime):
    """Create a line protocol"""
    starttime=int(starttime)
    lineordermsg = ""
    if "ask" in order:
        lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},askingprice={6},expirationtime={7}i"
    if "bid" in order:
        lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},biddingprice={6},expirationtime={7}i"
    return lineordermsg.format(order, applicationKey, starttime, wattage, duration, totalenergy, orderprice, expirationtime)



# def authClient(authServer, username, password, applicationKey):
#     userauthurl = f'https://{authServer}/users/login'
#     usertoken=""
#     appToken=""
#     userId=""
#     authdata = {'email': username, 'password': password}
#     print(authdata)
#     print(userauthurl)
#     response = requests.post(userauthurl, data=authdata)
#     if response.status_code == 200:
#         print("USER AUTH SUCCESFULL")
#         json_response = response.json()
#         userId = json_response['userId']
#         if 'locations' in json_response:
#             for locs in json_response['locations']:
#                 if applicationKey is not "":
#                     if applicationKey == locs['_id']:
#                         appToken = locs['token']
#                         break
#                 else:
#                     #Pick first application/Metering point
#                     applicationKey = locs['_id']
#                     appToken = locs['token']
#                     break
#     else:
#         print(f'Location/measurement point/application auth failed with response {response.status_code}')
#     return userId, applicationKey, appToken