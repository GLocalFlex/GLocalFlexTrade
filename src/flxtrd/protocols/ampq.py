import json
import ssl as _ssl
import time
from logging import DEBUG, ERROR, INFO
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


class AmpqAPI(BaseAPI):
    """Amqp API implementation that connects to public API"""

    def __init__(self, base_url: str, user: User, broker: Broker, callback_fn=None):
        super().__init__(base_url=base_url)
        self.user: User = user
        self.broker: Broker = broker
        self.ssl_options: pika.SSLOptions = None
        self.connection = None
        self.channel = None
        self.callback_queue_id = None
        self.callback_fn = callback_fn
        self.callback_response = None

    def send_request(
        self,
        endpoint: str = None,
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

        market: Market = kwargs["market"]

        user: User = kwargs["user"]
        order: MarketOrder = kwargs["order"]
        flexibility = order.flexibility

        routingkey = order.type.value

        log(INFO, f"Using {routingkey} as routing key for message broker")

        log(INFO, f"Creating line protocol message for the order {order}")
        msg = self.create_line_message(
            user=user, flexibility=flexibility, marketOrder=order
        )

        log(INFO, f"Send market order {order}")
        log(DEBUG, f"Order message: {msg}")

        self.publish(
            message=msg,
            userid=user.userId,
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
            user=self.user,
            broker=self.broker,
            ssl_options=ssl_options,
            verify_ssl=verify_ssl,
        )
        # TODO
        return err

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
        if self.connection is None:
            return False
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


def setreceiver(callback, callback_queue, channel):
    channel.basic_consume(
        queue=callback_queue, on_message_callback=callback, auto_ack=True
    )


def checkreplies(connection):
    connection.process_data_events()
