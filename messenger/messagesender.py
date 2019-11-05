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

def authClient(authServer, username, password):
    userauthurl = f'http://{authServer}/users/login'
    usertoken=""
    appToken=""
    uid=""
    authdata = {'email': username, 'password': password}
    print("AUTHDATA "+str(authdata))
    response = requests.post(userauthurl, data=authdata)
    if response.status_code == 200:
        json_response = response.json()
        print("User authentication success")
        usertoken = json_response['token']
        uid = json_response['userId']
        appauthurl = f'http://{authServer}/locations/owner/{uid}'
        appresponse = requests.get(appauthurl, headers={"Authorization": "Bearer "+usertoken})
        if appresponse.status_code == 200:
            if 'count' in appresponse.json().keys():
                if appresponse.json()['count'] > 0:
                    print("Found "+str(appresponse.json()['count'])+" measuring points/locations")
                    mpoint_json=appresponse.json()['locations'][0]
                    print("Using "+mpoint_json['name']+" "+str(mpoint_json['_id']))
                    applicationkey = mpoint_json['_id']
                    appToken=mpoint_json['token']
                    print(f'Location/device/application auth success with {applicationkey}')
            print("------------------------")
        else:
            print(f'Location/device/application auth failed with response {appresponse.status_code}')
    else:
       print("User authentication failed")
    return uid, usertoken, applicationkey, appToken

def getcurrenttimems():
    return  int(time.time()*1000)

def declareReplyToQueue(__channel, applicationkey):
    try:
        dec_res = __channel.queue_declare(applicationkey, exclusive=True)
        return dec_res
    except pika.exceptions.ChannelClosedByBroker:
        print("ReplyTo queue creation failed "+applicationkey)

def connecttobroker(username, userpw, brokerip, brokerport):
    global __channel, __connection, userid, __callback_queue
    authServer=brokerip+":3000"
    userid, usertoken, applicationkey, apptoken = authClient(authServer, username, userpw)
    credentials = pika.PlainCredentials(userid, apptoken)
    parameters = pika.ConnectionParameters(brokerip, brokerport, "/", credentials)
    __connection = pika.BlockingConnection(parameters)
    __channel = __connection.channel()
    result = declareReplyToQueue(__channel, applicationkey)
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
    global __channel, __connection, userid
    props = pika.BasicProperties(user_id=userid, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=askroutingkey, properties=props, body=askmsg)

def sendbidmsg(bidmsg):
    global __channel, __connection, applicationkey
    props = pika.BasicProperties(user_id=userid, reply_to=__callback_queue, headers={'sendertimestamp_in_ms': getcurrenttimems()})
    __channel.basic_publish(exchange=exchangename, routing_key=bidroutingkey, properties=props, body=bidmsg)

#Test
#connecttobroker()
#sendaskmsg("askmsg")
#closeconnection()
