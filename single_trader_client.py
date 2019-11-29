import trademessage.messageserializer as msg
import messenger.messagesender as snd
import multiprocessing
import socket
import json
import argparse
from random import random
from time import sleep
from time import time

tickprice = 0
brokerport=5672
username="testuser_20@testdomain.com"
userpw="passu123"

def on_response(ch, method, props, body):
    global tickprice
    currTimeMs = int(time()*1000)
    #Tick message ex. {'msgtype': 'tick', 'last_price_time': 1559732378418422410, 'last_price': 7.529581909307273}
    try:
        msgBody = json.loads(body)
        if 'msgtype' in msgBody.keys():
            if msgBody['msgtype'] == 'cancel':
                    print("--- Bohoo! My message got cancelled for ", msgBody['reason'])
            if msgBody['msgtype'] == 'tick':
                tickprice = msgBody['last_price']
                print("--- Tick ",tickprice)
                if 'sendertimestamp_in_ms' in props.headers.keys():
                    print(f"----- Tick was received in {currTimeMs - props.headers['sendertimestamp_in_ms']} ms")
            if msgBody['msgtype'] == 'bid_closed_order':
                if "closed_order" in msgBody.keys():
                    print("--- Wohoo! My bid order deal went through for ", msgBody['closed_order']['price'])
            if msgBody['msgtype'] == 'ask_closed_order':
                if "closed_order" in msgBody.keys():
                    print("--- Wohoo! My ask order deal went through for ", msgBody['closed_order']['price'])
    except ValueError:
        print("RECEIVED A NON JSON MESSAGE:", body)

def start_client(args):
    brokerip=args.markethost
    
    apptoken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZGJjMWNkNzRjMmM4YjY5MDlhZjU5NWMiLCJ1dWlkIjoiNTM5MDY5NzgtNmQ0OS00YmVjLTg0ZjktNzczMmYzZGRhOWFjIiwiaWF0IjoxNTcyNjA5MzU4LCJleHAiOjE2NjcyMTczNTh9.uzzrdDX5CQaDV__hNdVWwLKHa0IEBWIFrV91axHbqM4'
    known_appkey='5dbc1d4e4c2c8b6909af595e'
        
    #See other methods for authentication from .messenger/messagesender.py including:
    # - connecttobrokerWithAppToken(brokerip, brokerport, apptoken)
    # - connecttobrokerWithUsernameAndPWAndAppKey(brokerip, brokerport, username, userpw, applicationKey)
    # - connecttobrokerWithUsernameAndPW(brokerip, brokerport, username, userpw)
    
    appkey = snd.connecttobrokerWithAppToken(brokerip, brokerport, apptoken)
    if appkey==known_appkey:
        print("Appkeys match - starting")
       
    print(f" Starting connection to {brokerip}")
    snd.setreceiver(on_response)
    print(f" Connection started to {brokerip}")

    while True:
        delay=random()*args.delaymultip
        print("-----------------------------------")       
        if tickprice != 0:
            print("Current price is: ", tickprice)
            askprice = tickprice + random()
            bidprice = askprice - random()
        else:
            print("Current price is: NO tick messages yet")
            askprice = random()*10
            bidprice = askprice + (random()*10)

        askstarttime = int((time() + (60 * 60 * random() * 10)) / 60) * 60 * 1000
        bidstarttime = int(askstarttime / (60 * 1000) + random() * 20) * 60 * 1000
        askwattage = random() * 100
        bidwattage = random() * 300
        askduration = int(((round(random()) * 14 + 1) / 60.0) * 60 * 60 * 1000)
        bidduration = int((round(random() * 0.25 * 60) / 60.0) * 60 * 60 * 1000)
        if args.bid:
            bidtotenergy = bidwattage * (bidduration / (60 * 60 *1000))
            bidmsg = msg.getLineBidMessage(appkey, bidwattage, bidduration, bidstarttime,
                                           bidtotenergy, bidprice, bidstarttime).strip('"')
            snd.sendbidmsg(bidmsg)
            print(bidmsg)
        if args.ask:
            asktotenergy = askwattage * (askduration / (60 * 60 *1000))
            askmsg = msg.getLineAskMessage(appkey, askwattage, askduration, askstarttime,
                                           asktotenergy, askprice, bidstarttime).strip('"')
            snd.sendaskmsg(askmsg)
            print(askmsg)

        #This will explicitly query for the replies which are then processed on the on_response callback function
        snd.checkreplies()
        print("Random sleep of ", delay, " seconds")
        sleep(delay)

    snd.closeconnection()
    print("Closed connection")

if __name__ == '__main__':
    print("Single trader client. See options with -h switch, without options will connect to default market place and show only ticker.")
    print("-------------------")
    parser = argparse.ArgumentParser(description='A reference implementation and test client and for running imaginary trading agent')
    parser.add_argument('--markethost', type=str, dest="markethost", default="wotan.ad.vtt.fi", action='store', help='IP or hostname for the market place to trade on')
    parser.add_argument('--delay', type=int, dest="delaymultip", default=10, action='store', help='Random delay multiplier between messages')
    parser.add_argument('--bid', action='store_true', help='Switch for operating in bidding mode')
    parser.add_argument('--ask', action='store_true', help='Switch for operating in asking mode')
    args=parser.parse_args()
    start_client(args)

