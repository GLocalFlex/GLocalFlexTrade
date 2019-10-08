import pika
import time
import json
import requests

brokerip="wotan.ad.vtt.fi"
brokerport=5672
authserver=brokerip+":3000"
username="testuser@testdomain.com"
userpw="testing"
applicationkey=""

tickeroutexname = "ticker-out"
exchangename = "in"
bidroutingkey = "bid"
askroutingkey = "ask"
__channel = None
__connection = None
__callback_queue = None

def authClient(username, password):
    global applicationkey
    userauthurl = f'http://{authserver}/users/login'
    usertoken=""
    uid=""
    authdata = {'email': username, 'password': password}
    response = requests.post(userauthurl, data=authdata)
    if response.status_code == 200:
        json_response = response.json()
        print("User authentication success")
        usertoken = json_response['token']
        uid = json_response['userId']
        appauthurl = f'http://{authserver}/locations/{uid}'
        appresponse = requests.get(appauthurl, headers={"Authorization": "Bearer "+usertoken})
        if appresponse.status_code == 200:
            print(f'Location/device/application auth success with {uid}')
        else:
            print(f'Location/device/application auth failed with response {appresponse.status_code}')
    else:
       print("User authentication failed")
    return uid, usertoken

def getcurrenttimems():
    return  int(time.time()*1000)

def connecttobroker():
    global __channel, __connection, __callback_queue, applicationkey
    applicationkey, usertoken = authClient(username, userpw)
    credentials = pika.PlainCredentials(applicationkey, usertoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    #Create callback queue
    result = __channel.queue_declare(applicationkey, exclusive=True)
    __callback_queue = result.method.queue
    __channel.queue_bind(__callback_queue, tickeroutexname)
    return __callback_queue

def connecttobrokerwithparams(username, userpw, brokerip, brokerport):
    global __channel, __connection, applicationkey
    applicationkey, usertoken = authClient(username, userpw)
    credentials = pika.PlainCredentials(applicationkey, usertoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    #Create callback queue
    result = __channel.queue_declare(applicationkey, exclusive=True)
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
    global __channel, __connection, applicationkey
    props = pika.BasicProperties(user_id=applicationkey, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=askroutingkey, properties=props, body=askmsg)

def sendbidmsg(bidmsg):
    global __channel, __connection, applicationkey
    props = pika.BasicProperties(user_id=applicationkey, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=bidroutingkey, properties=props, body=bidmsg)

#Test
#connecttobroker()
#sendaskmsg("askmsg")
#closeconnection()
