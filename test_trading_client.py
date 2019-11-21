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
            if msgBody['msgtype'] == 'cancel':
                    print("--- Bohoo! My message got cancelled for ", msgBody['reason'])
        else:
            print("GOT SOMETHING ELSE: ", body)
    except ValueError:
        print("RECEIVED A NON JSON MESSAGE:", body)

def start_client(args, procnum):
    print(procnum, " Starting connection")
    #Username is unique for each process number up to 20 - first available metering point selected
    applicationKey = snd.connecttobrokerWithUsernameAndPW(brokerip, brokerport, username.format(procnum), userpw)
    #This utilizes metering point token, unique for each metering point registed in the profile, as supplied by the portal - see your user profile at the portal
    #applicationKey = snd.connecttobrokerWithAppToken(brokerip, brokerport, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZGJjMjAyMTRjMmM4YjY5MDlhZjU5ODkiLCJ1dWlkIjoiNjhmZThmNmQtYmQ0OC00YzNlLWEyZmEtNmQxNzI1YjY2NTM2IiwiaWF0IjoxNTcyNjEwMTA1LCJleHAiOjE2NjcyMTgxMDV9.Qdh46nS_rKxITgqK2bdfOwF7Fg-XZe1c4J4G2TAJALA')
    #applicationKey = snd.connecttobrokerWithUsernameAndPWAndAppKey(brokerip, brokerport, username.format(procnum), userpw, "5dbc20394c2c8b6909af598b")
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
    for i in range(2, args.procnum+1):
        p = multiprocessing.Process(target=start_client, args=(args,i,))
        jobs.append(p)
        p.start()

