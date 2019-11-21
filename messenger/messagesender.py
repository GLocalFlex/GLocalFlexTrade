import pika
import time
import json
import requests

userid=""

tickeroutexname = "ticker-out"
exchangename = "in"
bidroutingkey = "bid"
askroutingkey = "ask"

__channel = None
__connection = None
__callback_queue = None

def validateApplicationToken(authServer, appToken):
    appAuthUrl = f'http://{authServer}/users/mptoken/{appToken}'
    userId = ""
    applicationKey = ""
    response = requests.get(appAuthUrl)
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

def authClient(authServer, username, password, applicationKey):
    userauthurl = f'http://{authServer}/users/login'
    usertoken=""
    appToken=""
    userId=""
    authdata = {'email': username, 'password': password}
    response = requests.post(userauthurl, data=authdata)
    if response.status_code == 200:
        json_response = response.json()
        userId = json_response['userId']
        if 'locations' in json_response:
            for locs in json_response['locations']:
                if applicationKey is not "":
                    if applicationKey == locs['_id']:
                        appToken = locs['token']
                        break
                else:
                    #Pick first application/Metering point
                    applicationKey = locs['_id']
                    appToken = locs['token']
                    break
    else:
        print(f'Location/measurement point/application auth failed with response {response.status_code}')
    return userId, applicationKey, appToken

def getcurrenttimems():
    return  int(time.time()*1000)

def declareReplyToQueue(__channel, applicationKey):
    try:
        dec_res = __channel.queue_declare(applicationKey, exclusive=True)
        __callback_queue = dec_res.method.queue
        __channel.queue_bind(__callback_queue, tickeroutexname)
        print("Creating "+str(applicationKey))
        print("Created "+str(__callback_queue))
        return __callback_queue
    except pika.exceptions.ChannelClosedByBroker:
        print("ReplyTo queue creation failed "+applicationKey)

def connecttobrokerWithAppToken(brokerip, brokerport, apptoken):
    global __channel, __connection, __callback_queue, userid
    authServer=brokerip+":3000"
    userid, applicationKey = validateApplicationToken(authServer, apptoken)
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    __callback_queue = declareReplyToQueue(__channel, applicationKey)
    return __callback_queue

def connecttobrokerWithUsernameAndPWAndAppKey(brokerip, brokerport, username, userpw, applicationKey):
    global __channel, __connection, __callback_queue, userid
    authServer=brokerip+":3000"
    userid, applicationKey, apptoken = authClient(authServer, username, userpw, applicationKey)
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    __callback_queue = declareReplyToQueue(__channel, applicationKey)
    return __callback_queue

def connecttobrokerWithUsernameAndPW(brokerip, brokerport, username, userpw):
    global __channel, __connection, userid, __callback_queue
    authServer=brokerip+":3000"
    userid, applicationKey, apptoken = authClient(authServer, username, userpw, "")
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    __callback_queue = declareReplyToQueue(__channel, applicationKey)
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
    global __channel, __connection, userid
    #props = pika.BasicProperties(user_id=userid, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    props = pika.BasicProperties(user_id=userid, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    ack = __channel.basic_publish(exchange=exchangename, routing_key=askroutingkey, properties=props, body=askmsg)
    print(ack)

def sendbidmsg(bidmsg):
    global __channel, __connection
    #props = pika.BasicProperties(user_id=userid, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    props = pika.BasicProperties(user_id=userid, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    ack = __channel.basic_publish(exchange=exchangename, routing_key=bidroutingkey, properties=props, body=bidmsg)
    print(ack)
