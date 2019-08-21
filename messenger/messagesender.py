import pika
import time
import json

#brokerip="localhost"
#brokerip="130.188.94.76"
#brokerip="wotan.ad.vtt.fi"
brokerip="fasolt1.willab.fi"
brokerport=5672
username="telegrafuser"
userpw="K0ukku55"
applicationkey="applicationtestkey"



tickeroutexname = "ticker-out"
exchangename = "in"
bidroutingkey = "bid"
askroutingkey = "ask"
__channel = None
__connection = None
__callback_queue = None

def getcurrenttimems():
    #return round(time.time()*1000)
    return  int(time.time()*1000)

def connecttobroker():
    global __channel, __connection, __callback_queue
    credentials = pika.PlainCredentials(username, userpw)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    #Create callback queue
    result = __channel.queue_declare('', exclusive=True)
    __callback_queue = result.method.queue
    __channel.queue_bind(__callback_queue, tickeroutexname)
    return __callback_queue

def connecttobrokerwithparams(username, userpw, brokerip, brokerport):
    global __channel, __connection
    credentials = pika.PlainCredentials(username, userpw)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    #Create callback queue
    result = __channel.queue_declare('', exclusive=True)
    __callback_queue = result.method.queue    
    __channel.queue_bind(__callback_queue, tickeroutexname)    
    return __callback_queue
    
def setreceiver(callback):
    global __channel, __callback_queue
    __channel.basic_consume(queue=__callback_queue, on_message_callback=callback, auto_ack=True)

def checkreplies():
    global __connection
    __connection.process_data_events()
    
def closeconnection():
    global __channel, __connection
    __connection.close()

def sendaskmsg(askmsg):
    global __channel, __connection
    props = pika.BasicProperties(user_id=username, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=askroutingkey, properties=props, body=askmsg)

def sendbidmsg(bidmsg):
    global __channel, __connection
    props = pika.BasicProperties(user_id=username, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})    
    __channel.basic_publish(exchange=exchangename, routing_key=bidroutingkey, properties=props, body=bidmsg)

#Test
#connecttobroker()
#sendaskmsg("askmsg")
#closeconnection()
