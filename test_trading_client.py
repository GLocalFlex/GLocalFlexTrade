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
                print("--- Wohoo! My bit order deal went through for ", msgBody['closed_order']['price'])
            if msgBody['msgtype'] == 'ask_closed_order':
                print("--- Wohoo! My ask order deal went through for ", msgBody['closed_order']['price'])
    except ValueError:
        print("RECEIVED A NON JSON MESSAGE:", body)

def start_client(args, procnum):
    print(procnum, " Starting connection")
    #Username is unique for each process number up to 20 
    applicationKey = snd.connecttobroker(username.format(procnum), userpw, brokerip, brokerport)
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
            bidmsg = msg.getLineBidMessage(applicationKey, bidwattage, bidduration, bidstarttime,
                                           bidtotenergy, bidprice, bidstarttime).strip('"')
            snd.sendbidmsg(bidmsg)
            print(procnum, bidmsg)
        if args.ask:
            asktotenergy = askwattage * (askduration / (60 * 60 *1000))
            askmsg = msg.getLineAskMessage(applicationKey, askwattage, askduration, askstarttime,
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
    parser = argparse.ArgumentParser(description='Test client for running imaginary trading client')
    parser.add_argument('--proc', type=int, dest="procnum", default=1, choices=range(1,21), action='store', help='Number of test client processes to start, up to 20')
    parser.add_argument('--delay', type=int, dest="delaymultip", default=10, action='store', help='Random delay multiplier between messages')
    parser.add_argument('--bid', action='store_true', help='Switch for operating in bidding mode')
    parser.add_argument('--ask', action='store_true', help='Switch for operating in asking mode')
    args=parser.parse_args()
    print(args)
    jobs = []
    for i in range(1, args.procnum+1):
        p = multiprocessing.Process(target=start_client, args=(args,i,))
        jobs.append(p)
        p.start()

