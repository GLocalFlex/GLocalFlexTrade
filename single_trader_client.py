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
brokerip="wotan.ad.vtt.fi"
brokerport=5672
username="testuser_{0}@testdomain.com"
userpw="passu123"

def on_response(ch, method, props, body):
    global tickprice
    #Tick message ex. {'msgtype': 'tick', 'last_price_time': 1559732378418422410, 'last_price': 7.529581909307273}
    try:
        msgBody = json.loads(body)
        if 'msgtype' in msgBody.keys():
            if msgBody['msgtype'] == 'tick':
                tickprice = msgBody['last_price']
                print("--- Tick ",tickprice)
            if msgBody['msgtype'] == 'bid_closed_order':
                if "closed_order" in msgBody.keys():
                    print("--- Wohoo! My bid order deal went through for ", msgBody['closed_order']['price'])
            if msgBody['msgtype'] == 'ask_closed_order':
                if "closed_order" in msgBody.keys():
                    print("--- Wohoo! My ask order deal went through for ", msgBody['closed_order']['price'])
    except ValueError:
        print("RECEIVED A NON JSON MESSAGE:", body)

def start_client(args):
    if args.mpnum == 1:
        procnum=1
        apptoken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZGJjMWNkNzRjMmM4YjY5MDlhZjU5NWMiLCJ1dWlkIjoiNTM5MDY5NzgtNmQ0OS00YmVjLTg0ZjktNzczMmYzZGRhOWFjIiwiaWF0IjoxNTcyNjA5MzU4LCJleHAiOjE2NjcyMTczNTh9.uzzrdDX5CQaDV__hNdVWwLKHa0IEBWIFrV91axHbqM4'
        known_appkey='5dbc1d4e4c2c8b6909af595e'
    if args.mpnum == 2:
        procnum=2
        apptoken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZGJjMWNkNzRjMmM4YjY5MDlhZjU5NWMiLCJ1dWlkIjoiM2Q2NGY1NTktOTA0NC00ODgyLTk5NDgtN2ExMGM1NTRiN2ExIiwiaWF0IjoxNTc0MjM5NDgzLCJleHAiOjE2Njg4NDc0ODN9.G77kHT4KzFNyI2AgOe4hJPjC6wweagoKafkHJxHYog8'
        known_appkey='5dd4fcfbfc999d456a93da14'
        
    appkey = snd.connecttobrokerWithAppToken(brokerip, brokerport, apptoken)
    if appkey==known_appkey:
        print("Appkeys match - starting")
        print(appkey)
        
    print(procnum, " Starting connection")


    snd.setreceiver(on_response)
    print(procnum, " Connection started")

    while True:
        delay=random()*args.delaymultip
        print(procnum, "-----------------------------------")
        print(procnum, "Current price is: ", tickprice)
        if tickprice != 0:
            askprice = tickprice + random()
            bidprice = askprice - random()
        else:
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
            print(procnum, bidmsg)
        if args.ask:
            asktotenergy = askwattage * (askduration / (60 * 60 *1000))
            askmsg = msg.getLineAskMessage(appkey, askwattage, askduration, askstarttime,
                                           asktotenergy, askprice, bidstarttime).strip('"')
            snd.sendaskmsg(askmsg)
            print(procnum, askmsg)

        #This will explicitly query for the replies which are then processed on the on_response callback function
        snd.checkreplies()
        print(procnum, "Delaying ", delay, " seconds")
        sleep(delay)

    snd.closeconnection()
    print(procnum, "Closed connection")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test client for running imaginary trading client for testuser_1')
    parser.add_argument('--mpnum', type=int, dest="mpnum", default=1, choices=range(1,3), action='store', help='Selection of which metering point should do trading, 1 or 2')
    parser.add_argument('--delay', type=int, dest="delaymultip", default=10, action='store', help='Random delay multiplier between messages')
    parser.add_argument('--bid', action='store_true', help='Switch for operating in bidding mode')
    parser.add_argument('--ask', action='store_true', help='Switch for operating in asking mode')
    args=parser.parse_args()
    print(args)
    start_client(args)

