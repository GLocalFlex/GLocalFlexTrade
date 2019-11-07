import pika
import time
import json
import requests

applicationkey=""
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

def authClient(authServer, username, password, applicationkey):
    userauthurl = f'http://{authServer}/users/login'
    usertoken=""
    appToken=""
    userId=""
    authdata = {'email': username, 'password': password}
    response = requests.post(userauthurl, data=authdata)
    if response.status_code == 200:
        json_response = response.json()
        usertoken = json_response['token']
        print("User authentication success")
        userId = json_response['userId']
        appauthurl = f'http://{authServer}/locations/owner/{userId}'
        appresponse = requests.get(appauthurl, headers={"Authorization": "Bearer "+usertoken})
        if appresponse.status_code == 200:
            if 'count' in appresponse.json().keys():
                if appresponse.json()['count'] > 0:
                    #If applicationkey given as a parameter
                    if applicationkey is not "":
                        if applicationkey in str(appresponse.text):
                            for measuringPoint in appresponse.json()['locations']:                               
                                print("Using "+measuringPoint['name']+" "+str(measuringPoint['_id'])+ " "+str(applicationkey))
                                if applicationkey == measuringPoint['_id']:
                                    appToken=measuringPoint['token']
                                    print(f'Location/device/application auth success with {applicationkey}')
                                else:
                                    print(f'Location/device/application auth failed with {applicationkey}. No such key, check your registered profile')
                                break
                        else:
                            print(f'No "+applicationKey+" location/measurement point/application registered to authenticate. Please check your registered profile and its measurement points!')
                    #If no applicationkey given as a parameter, we pick the first one
                    else:
                        mpoint_json=appresponse.json()['locations'][0]
                        print("Using "+mpoint_json['name']+" "+str(mpoint_json['_id']))
                        applicationkey = mpoint_json['_id']
                        appToken=mpoint_json['token']
                        print(f'Location/device/application auth success with {applicationkey}')
            else:
                print("No locations/measurement points/applications registered to authenticate. Please check your profile and registered measurement points!")
            print("------------------------")
        else:
            print(f'Location/measurement point/application auth failed with response {appresponse.status_code}')
    else:
       print("User authentication failed")
    return userId, usertoken, applicationkey, appToken

def getcurrenttimems():
    return  int(time.time()*1000)

def declareReplyToQueue(__channel, applicationkey):
    try:
        dec_res = __channel.queue_declare(applicationkey, exclusive=True)
        __callback_queue = dec_res.method.queue
        __channel.queue_bind(__callback_queue, tickeroutexname)
        return __callback_queue
    except pika.exceptions.ChannelClosedByBroker:
        print("ReplyTo queue creation failed "+applicationkey)

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

def connecttobrokerWithUsernameAndPWAndAppKey(brokerip, brokerport, username, userpw, applicationkey):
    global __channel, __connection, __callback_queue, userid
    authServer=brokerip+":3000"
    userid, usertoken, applicationkey, apptoken = authClient(authServer, username, userpw, applicationkey)
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    __callback_queue = declareReplyToQueue(__channel, applicationkey)
    return __callback_queue

def connecttobrokerWithUsernameAndPW(brokerip, brokerport, username, userpw):
    global __channel, __connection, userid, __callback_queue
    authServer=brokerip+":3000"
    userid, usertoken, applicationkey, apptoken = authClient(authServer, username, userpw, "")
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    __callback_queue = declareReplyToQueue(__channel, applicationkey)
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
    __channel.basic_publish(exchange=exchangename, routing_key=askroutingkey, properties=props, body=askmsg)

def sendbidmsg(bidmsg):
    global __channel, __connection, applicationkey
    #props = pika.BasicProperties(user_id=userid, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    props = pika.BasicProperties(user_id=userid, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=bidroutingkey, properties=props, body=bidmsg)
