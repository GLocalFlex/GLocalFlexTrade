import json
import ssl as _ssl
import sys
import time
from logging import DEBUG, ERROR, INFO
from pprint import pformat
from typing import Optional

import pika

from flxtrd.core.logger import log
from flxtrd.core.types import (
    FlexBroker,
    FlexError,
    FlexMarket,
    FlexResource,
    FlexUser,
    MarketOrder,
    OrderType,
)
from flxtrd.protocols.base import BaseAPI


def create_line_message(user: FlexUser, flexibility: FlexResource, marketOrder: MarketOrder):
    """Create a line protocol message for InfluxDB that is the payload in the AMQP message

    Format ask:
    ask,applicationKey=64218f1adc42c714c1f08043,version=1 starttime=1685730000000i,wattage=19.556418841474642,runtime=60000i,totalenergy=0.32594031402457735,askingprice=7.933964367826437,expirationtime=1685730000000i

    Bid:
    bid,applicationKey=64218f1adc42c714c1f08043,version=1 starttime=1685732700000i,wattage=226.3288909510559,runtime=840000i,totalenergy=52.81007455524638,biddingprice=6.56704792164692,expirationtime=1685732700000i

    """
    lineordermsg = ""
    if marketOrder.order_type == OrderType.ASK:
        pricename = "askingprice"
    elif marketOrder.order_type == OrderType.BID:
        pricename = "biddingprice"
    else:
        raise FlexError(f"Order type {marketOrder.order_type} not supported")

    order_type = marketOrder.order_type
    application_key = user.app_key
    wattage = flexibility.power_w
    duration = flexibility.duration_min
    starttime = flexibility.start_time_epoch_ms
    totalenergy = flexibility.energy_wh
    orderprice = marketOrder.price_eur
    expirationtime = flexibility.expiration_time_epoch_ms

    lineordermsg = (
        f"{order_type.value},"
        f"applicationKey={application_key},"
        f"version=1 starttime={starttime}i,"
        f"wattage={wattage},"
        f"runtime={duration}i,"
        f"totalenergy={totalenergy},"
        f"{pricename}={orderprice},"
        f"expirationtime={expirationtime}i"
    )

    return json.dumps(lineordermsg).strip('"')


class AmpqAPI(BaseAPI):
    """Amqp API implementation that connects to public API"""

    def __init__(self, base_url: str, user: FlexUser, broker: FlexBroker, callback_fn=None):
        super().__init__(base_url=base_url)
        self.user: FlexUser = user
        self.broker: FlexBroker = broker
        self.ssl_options: pika.SSLOptions = None
        self.connection = None
        self.channel = None
        self.callback_queue_id = None
        self.callback_fn = callback_fn
        self.callback_responses: list = []

    def send_request(
        self,
        endpoint: Optional[str] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        verifiy_ssl: Optional[bool] = False,
        **kwargs,
    ) -> dict:
        if "market" not in kwargs:
            raise FlexError("'market' not found arguments")
        if "user" not in kwargs:
            raise FlexError("'user' not found in arguments")

        market: FlexMarket = kwargs["market"]
        user: FlexUser = kwargs["user"]
        order: MarketOrder = kwargs["order"]
        flexibility = order.resource

        routingkey = order.order_type.value

        log(DEBUG, f"Using {routingkey} as routing key for message broker")
        log(
            DEBUG,
            f"Creating line protocol message for the  {order.order_type.name} order",
        )
        msg = create_line_message(user=user, flexibility=flexibility, marketOrder=order)

        log(INFO, f"Send market order {order}")
        log(DEBUG, f"Order message: {msg}")

        self.publish(
            message=msg,
            userid=user.user_id,
            routingkey=routingkey,
            exchangename=market.broker.exchangename,
        )

        replies = self.checkreplies()

        err = None
        return replies, err

    def _ssl_context(self, verify_ssl: bool = True):
        context = _ssl.create_default_context()
        if verify_ssl is False:
            # Disable ssl verification for development with self signed certificates
            context.check_hostname = False
            context.verify_mode = _ssl.CERT_NONE
        return pika.SSLOptions(context)

    def connect(self, verify_ssl: bool = True):
        """Connect to RabbitMQ broker"""
        # TODO handle timeout

        # TODO somewhere here some logic that checks if password and user or
        #  appkey or accesskeys are available
        # based on what the user provided different methods
        #  to connect to the server can be selected
        ssl_options = self._ssl_context(verify_ssl)
        err = self._connecttobrokerWithAppToken(
            user=self.user, broker=self.broker, ssl_options=ssl_options
        )

        if err:
            return err
        
        self.set_consumer(
            callback=self.callback_on_response,
            callback_queue=self.callback_queue_id,
            channel=self.channel,
        )

    def close_connection(self):
        """Close connection gracefully to message broker"""
        if self.connection is not None:
            self.connection.close()
            log(INFO, "Connection closed")
        else:
            log(INFO, "No connection to be closed")

    def publish(self, message: str, userid: str, routingkey: str, exchangename=str):
        """Send message to the broker"""
        props = pika.BasicProperties(
            user_id=userid,
            reply_to=self.callback_queue_id,
            headers={"sendertimestamp_in_ms": get_current_time_ms()},
        )
        try:
            self.channel.basic_publish(
                exchange=exchangename,
                routing_key=routingkey,
                properties=props,
                body=message,
            )
        except pika.exceptions.ChannelWrongStateError as error:
            if 'Channel is closed' in str(error):
                raise FlexError('Channel is closed. Connection to broker is not possible.')


    def checkreplies(self):
        self.connection.process_data_events(time_limit=1)

    def is_connected(self):
        if self.connection is None:
            return False
        return self.connection.is_open

    def _connecttobrokerWithAppToken(
        self, user: FlexUser, broker: FlexBroker, ssl_options: pika.SSLOptions
    ):
        """Connects to the broker with the application token"""
        err = None
        brokerip = broker.url
        brokerport = broker.port
        accessToken = user.access_token
        tickeroutexname = broker.tickeroutexname

        userid = user.user_id
        applicationKey = user.app_key

        if userid is None or applicationKey is None:
            raise FlexError(
                "User authentication error. \nCheck if user credentials are correct or if auth"
                " plugin was correctly executed before connection."
            )

        credentials = pika.PlainCredentials(userid, accessToken)
        parameters = pika.ConnectionParameters(
            brokerip, brokerport, "/", credentials, ssl_options=ssl_options
        )

        try:
            self.connection = pika.BlockingConnection(parameters)
        except Exception as excep:
            # Todo check which exceptions can occur
            raise FlexError(str(excep))

        self.channel = self.connection.channel()
        self.callback_queue_id = declare_reply_queue(
            self.channel, applicationKey, tickeroutexname
        )
        if self.callback_queue_id is None:
            return FlexError("No callback queue declared, That usually happens if more than one connection to the broker is opened", )
        return None
    
    def set_consumer(self, callback, callback_queue, channel):
        if callback_queue is None:
            raise FlexError("No callback queue declared, That usually happens if more than one connection to the broker is opened", )
        channel.basic_consume(queue=callback_queue, on_message_callback=callback, auto_ack=True)

    def checkreplies(self):
        if self.connection is None:
            raise FlexError("No connection to broker established")
        self.connection.process_data_events()

    def callback_on_response(self, ch, method, props, body):
        global tickprice
        currTimeMs = int(time.time() * 1000)
        # Tick message ex. {'msgtype': 'tick', 'last_price_time': 1559732378418422410, 'last_price': 7.529581909307273}
        try:
            msgBody = json.loads(body.decode("utf-8"))
            self.callback_responses.append(msgBody)

            log(INFO, f"Received message")
            log(INFO, f"{pformat(msgBody)}")
            # if 'msgtype' in msgBody.keys():
            #     if msgBody['msgtype'] == 'cancel':
            #             log(INFO,"--- Bohoo! My message got cancelled for ", msgBody['reason'])
            #     if msgBody['msgtype'] == 'tick':
            #         tickprice = msgBody['last_price']
            #         log(INFO,"--- Tick ",tickprice)
            #         if 'sendertimestamp_in_ms' in props.headers.keys():
            #             log(INFO,f"----- Tick was received in {currTimeMs - props.headers['sendertimestamp_in_ms']} ms")
            #     if msgBody['msgtype'] == 'bid_closed_order':
            #         if "closed_order" in msgBody.keys():
            #             log(INFO,"--- Wohoo! My bid order deal went through for ", msgBody['closed_order']['price'])
            #     if msgBody['msgtype'] == 'ask_closed_order':
            #         if "closed_order" in msgBody.keys():
            #             log(INFO,"--- Wohoo! My ask order deal went through for ", msgBody['closed_order']['price'])

            # sys.exit(0)

        except ValueError:
            log(ERROR, "RECEIVED A NON JSON MESSAGE:", body)


def get_current_time_ms():
    return int(time.time() * 1000)


def declare_reply_queue(
    channel: pika.adapters.blocking_connection.BlockingChannel,
    applicationKey: str,
    tickeroutexname: str,
) -> str:
    """Create a queue for the reply to messages from the broker
    The provided applicationKey is used as the queue name"""
    try:
        dec_res = channel.queue_declare(applicationKey, exclusive=True)
    except pika.exceptions.ChannelClosedByBroker as error:
        if "RESOURCE_LOCKED" in str(error):
            log(ERROR, "A connection from user with specific access token already exists")
            return None
        else:
            log(ERROR, "ReplyTo queue creation failed " + applicationKey)
            log(ERROR, error)
            raise error

    
    callback_queue_id: str = dec_res.method.queue
    channel.queue_bind(callback_queue_id, tickeroutexname)
    log(INFO, f"Created queue with ID {callback_queue_id}")
    return callback_queue_id
