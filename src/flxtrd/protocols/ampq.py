import json
import ssl as _ssl
import string
import time
from logging import ERROR, INFO
from typing import Optional

import pika

from flxtrd.core.logger import log
from flxtrd.core.types import (
    Broker,
    FlexError,
    Flexibility,
    Market,
    MarketOrder,
    OrderType,
    User,
)
from flxtrd.protocols.base import BaseAPI


class AmpqContext:
    """Context for AmpqAPI keeps the connection to the broker"""

    def __init__(self, user: User, broker: Broker, verify_ssl: bool = True):
        self.user: User = user
        self.broker: Broker = broker
        self.verify_ssl = verify_ssl
        self.ssl_options: pika.SSLOptions = None
        self.connection = None
        self.channel = None
        self.callback_queue_id = None

    def _ssl_context(self):
        context = _ssl.create_default_context()
        if self.verify_ssl is False:
            # Disable ssl verification for development with self signed certificates
            context.check_hostname = False
            context.verify_mode = _ssl.CERT_NONE
        return pika.SSLOptions(context)

    def connect(self):
        """Connect to RabbitMQ broker"""

        # TODO somewhere here some logic that checks if password and user or appkey or accesskeys are available
        # based on what the user provided different methods to connect to the server can be selected
        ssl_options = self._ssl_context()
        err = self._connecttobrokerWithAppToken(
            user=self.user,
            broker=self.broker,
            ssl_options=ssl_options,
            verify_ssl=self.verify_ssl,
        )
        # TODO
        return err

    def close_connection(self):
        """Close connection gracefully to message broker"""
        self.connection.close()

    def publish(
        self, message: str, userid: str, routingkey: str, exchangename=str
    ):
        """Send message to the broker"""
        props = pika.BasicProperties(
            user_id=userid,
            reply_to=self.callback_queue_id,
            headers={"sendertimestamp_in_ms": getcurrenttimems()},
        )
        try:
            self.channel.basic_publish(
                exchange=exchangename,
                routing_key=routingkey,
                properties=props,
                body=message,
            )
        except Exception as error:
            raise FlexError(str(error))

    def checkreplies(self):
        self.connection.process_data_events()

    def is_connected(self):
        return self.connection.is_open

    def _connecttobrokerWithAppToken(
        self,
        user: User,
        broker: Broker,
        ssl_options: pika.SSLOptions,
        verify_ssl: bool = True,
    ):
        """Connects to the broker with the application token"""
        err = None
        brokerip = broker.ip
        brokerport = broker.port
        accessToken = user.accessToken
        tickeroutexname = broker.tickeroutexname

        # userid, applicationKey = validateApplicationToken(authServer=authServer,
        #                                                 accessTaken=accessToken,
        #                                                 verify_ssl=verify_ssl)

        userid = user.userId
        applicationKey = user.appKey

        if userid is None or applicationKey is None:
            raise FlexError("User or application key is None")

        credentials = pika.PlainCredentials(userid, accessToken)
        parameters = pika.ConnectionParameters(
            brokerip, brokerport, "/", credentials, ssl_options=ssl_options
        )

        # Todo check which exceptions can occur
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.callback_queue_id = declareReplyToQueue(
                self.channel, applicationKey, tickeroutexname
            )
        except Exception as excep:
            err = FlexError(str(excep))
            raise err
        return err


class AmpqAPI(BaseAPI):
    """Amqp API implementation that connects to public API"""

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    def send_request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        verifiy_ssl: Optional[bool] = False,
        **kwargs,
    ) -> dict:
        if "market" not in kwargs:
            raise FlexError("'market' not found arguments")
        if "user" not in kwargs:
            raise FlexError("'user' not found in arguments")
        if "order" not in kwargs:
            raise FlexError("'order' not found in arguments")
        if "context" not in kwargs:
            raise FlexError("'context' not found in arguments")

        ampq_context: AmpqContext = kwargs["context"]
        market: Market = kwargs["market"]
        broker = market.broker
        user: User = kwargs["user"]
        order: MarketOrder = kwargs["order"]
        flexibility = order.flexibility

        # context = _ssl.create_default_context()
        # if verifiy_ssl == False:
        #     # Disable ssl verification for development with self signed certificates
        #     context.check_hostname = False
        #     context.verify_mode = _ssl.CERT_NONE
        # ssl_options = pika.SSLOptions(context)

        # connection = ampq_context.connection
        # channel = ampq_context.channel
        # callback_queue_id = ampq_context.callback_queue_id

        # user, connection, channel, callback_queue_id = connecttobrokerWithAppToken(user=user,
        #                                                                         broker=market.broker,
        #                                                                         ssl_options=ssl_options,
        #                                                                         verify_ssl=verifiy_ssl)

        if "/" in endpoint:
            # accept endpoint in rest api style
            routingkeys = [key for key in endpoint.split("/") if key]
            if len(routingkeys) > 1:
                log(
                    INFO,
                    f"Received routing key with in Rest style: {endpoint}",
                )
            # take last item from list as expected
            routingkey = routingkeys[-1]
        else:
            routingkey = endpoint

        log(INFO, f"Using {routingkey} as routing key for message broker")

        log(INFO, f"Creating line protocol message for the order {order}")
        msg = self.create_line_message(
            user=user, flexibility=flexibility, marketOrder=order
        )

        log(INFO, f"Send market order {order}")
        log(INFO, f"Order message: {msg}")

        ampq_context.publish(
            message=msg,
            userid=user.userId,
            routingkey=routingkey,
            exchangename=broker.exchangename,
        )

        replies = ampq_context.checkreplies()

        err = None
        return replies, err

    @staticmethod
    def create_line_message(
        user: User, flexibility: Flexibility, marketOrder: MarketOrder
    ):
        """Create a line protocol message for InfluxDB that is the payload in the AMQP message

        Format ask:
        ask,applicationKey=64218f1adc42c714c1f08043,version=1 starttime=1685730000000i,wattage=19.556418841474642,runtime=60000i,totalenergy=0.32594031402457735,askingprice=7.933964367826437,expirationtime=1685730000000i

        Bid:
        bid,applicationKey=64218f1adc42c714c1f08043,version=1 starttime=1685732700000i,wattage=226.3288909510559,runtime=840000i,totalenergy=52.81007455524638,biddingprice=6.56704792164692,expirationtime=1685732700000i

        """
        lineordermsg = ""
        if marketOrder.type == OrderType.ASK:
            pricename = "askingprice"
        elif marketOrder.type == OrderType.BID:
            pricename = "biddingprice"
        else:
            raise FlexError(f"Order type {marketOrder.type} not supported")

        order_type = marketOrder.type
        applicationKey = user.appKey
        wattage = flexibility.wattage
        duration = flexibility.duration
        starttime = flexibility.starttime
        totalenergy = flexibility.energy
        orderprice = marketOrder.price
        expirationtime = flexibility.expirationtime

        lineordermsg = (
            f"{order_type.value},"
            f"applicationKey={applicationKey},"
            f"version=1 starttime={starttime}i,"
            f"wattage={wattage},"
            f"runtime={duration}i,"
            f"totalenergy={totalenergy},"
            f"{pricename}={orderprice},"
            f"expirationtime={expirationtime}i"
        )

        return json.dumps(lineordermsg).strip('"')
        # linemsg = createLineMessage(user=user ,marketOrder=marketOrder, flexibility=flexibility)
        # return json.dumps(linemsg).strip('"')


# def createLineMessage(user: User, marketOrder: MarketOrder ,flexibility: Flexibility) -> str:
#     """Create a line protocol"""

#     lineordermsg = ""
#     if marketOrder.type == OrderType.ASK.name:
#         pricename="askingprice"
#     elif marketOrder.type == OrderType.BID.name:
#         pricename="biddingprice"

#     order_type = marketOrder.type
#     applicationKey = user.appKey
#     wattage = flexibility.wattage
#     duration = flexibility.duration
#     starttime = flexibility.starttime
#     totalenergy = flexibility.energy
#     orderprice = marketOrder.price
#     expirationtime = flexibility.expirationtime

#     # lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},biddingprice={6},expirationtime={7}i"
#     # lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},askingprice={6},expirationtime={7}i"
#     # return lineordermsg.format(order, applicationKey, starttime, wattage, duration, totalenergy, orderprice, expirationtime)

#     lineordermsg = f"{order_type}"
#     f"applicationKey={applicationKey}"
#     f"version=1 starttime={starttime}i"
#     f"wattage={wattage}"f"runtime={duration}i"
#     f"totalenergy={totalenergy}"f"{pricename}={orderprice}"
#     f"expirationtime={expirationtime}i"
#     return lineordermsg
# #
# def validateApplicationToken(authServer, accessTaken, verify_ssl=True):
#     appAuthUrl = f'https://{authServer}/users/mptoken/{accessTaken}'
#     userId = ""
#     applicationKey = ""
#     response = requests.get(appAuthUrl, verify=verify_ssl)
#     if response.status_code == 200:
#         userId = response.json()['userId']
#         if 'locations' in response.json().keys():
#             if len(response.json()['locations']) > 0:
#                 applicationKey = response.json()['locations'][0]['_id']
#             else:
#                 log(INFO, f'Failed to validate applicationToken {accessTaken}')
#         log(INFO, f'Application token {accessTaken} successfully validated with applicationKey {applicationKey}')
#     else:
#         log(INFO, f'Failed to validate applicationToken {accessTaken}')
#     return userId, applicationKey

# def checkreplies(connection):
#     connection.process_data_events()


def getcurrenttimems():
    return int(time.time() * 1000)


def declareReplyToQueue(
    channel: pika.adapters.blocking_connection.BlockingChannel,
    applicationKey: str,
    tickeroutexname: str,
) -> str:
    """Create a queue for the reply to messages from the broker
    The provided applicationKey is used as the queue name"""
    try:
        dec_res = channel.queue_declare(applicationKey, exclusive=True)
        callback_queue_id: str = dec_res.method.queue
        channel.queue_bind(callback_queue_id, tickeroutexname)
        log(INFO, f"Created queue with ID {callback_queue_id}")
        return callback_queue_id
    except pika.exceptions.ChannelClosedByBroker:
        log(ERROR, "ReplyTo queue creation failed " + applicationKey)


# def connecttobrokerWithAppToken(user: User,
#                                 broker: Broker,
#                                 ssl_options: pika.SSLOptions,
#                                 verify_ssl: bool = True):

#     authServer = broker.ip # TODO: This should be the auth server
#     brokerip = broker.ip
#     brokerport = broker.port
#     accessToken =user.accessToken
#     tickeroutexname = broker.tickeroutexname

#     userid, applicationKey = validateApplicationToken(authServer=authServer,
#                                                       accessTaken=accessToken,
#                                                       verify_ssl=verify_ssl)
#     user.userId = userid
#     user.appkey = applicationKey
#     credentials = pika.PlainCredentials(userid, accessToken)
#     parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials, ssl_options=ssl_options)
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     callback_queue_id = declareReplyToQueue(channel, applicationKey, tickeroutexname)
#     return user, connection, channel, callback_queue_id


def setreceiver(callback, callback_queue, channel):
    channel.basic_consume(
        queue=callback_queue, on_message_callback=callback, auto_ack=True
    )


def checkreplies(connection):
    connection.process_data_events()


# def closeconnection(connection):
#     connection.close()

# def sendmsg(message: str,
#             callback_queue: pika.adapters.blocking_connection.BlockingChannel,
#             userid: str,
#             channel: pika.channel.Channel,
#             routingkey: str,
#             exchangename: str):
#     """Send message to the broker"""
#     props = pika.BasicProperties(user_id=userid, reply_to=callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
#     channel.basic_publish(exchange=exchangename, routing_key=routingkey, properties=props, body=message)

# def getLineMessage(endpoint: str,
#                    applicationKey: str,
#                    wattage: float,
#                    duration: int,
#                    starttime: int,
#                    totalenergy: float,
#                    price: float,
#                    expirationtime:int):
#     """Create a line protocol message for InfluxDB that is the payload in the AMQP message"""
#     linemsg = createLineMessage(endpoint, applicationKey, wattage, duration, starttime, totalenergy, price, expirationtime)
#     return json.dumps(linemsg)


# def createLineMessage(order, applicationKey, wattage, duration, starttime, totalenergy, orderprice, expirationtime):
#     """Create a line protocol"""
#     starttime=int(starttime)
#     lineordermsg = ""
#     if "ask" in order:
#         lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},askingprice={6},expirationtime={7}i"
#     if "bid" in order:
#         lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},biddingprice={6},expirationtime={7}i"
#     return lineordermsg.format(order, applicationKey, starttime, wattage, duration, totalenergy, orderprice, expirationtime)


# def authClient(authServer, username, password, applicationKey):
#     userauthurl = f'https://{authServer}/users/login'
#     usertoken=""
#     appToken=""
#     userId=""
#     authdata = {'email': username, 'password': password}
#     log(INFO, authdata)
#     log(INFO, userauthurl)
#     response = requests.post(userauthurl, data=authdata)
#     if response.status_code == 200:
#         log(INFO, "USER AUTH SUCCESFULL")
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
#         log(INFO, f'Location/measurement point/application auth failed with response {response.status_code}')
#     return userId, applicationKey, appToken
