import trademessage.messageserializer as msg
import messenger.messagesender as snd
import socket
import json
import argparse
from random import random
from time import sleep
from time import time

tickprice = 0

def on_response(ch, method, props, body):
    global tickprice
    print("REPLY MESSAGE:", body)
    #Tick message ex. {'msgtype': 'tick', 'last_price_time': 1559732378418422410, 'last_price': 7.529581909307273}
    msgBody = json.loads(body)
    if 'msgtype' in msgBody.keys():
        if msgBody['msgtype'] == 'tick':
            tickprice = msgBody['last_price']

parser = argparse.ArgumentParser(description='Test client for running imaginary trading client')               
parser.add_argument('--delay', type=int, dest="delaymultip", default=10, action='store', help='Random delay multiplier between messages')
parser.add_argument('--bid', action='store_true', help='Switch for operating in bidding mode')
parser.add_argument('--ask', action='store_true', help='Switch for operating in asking mode')
args=parser.parse_args()
print(args)

print("Starting connection")
applicationKey = snd.connecttobroker()
snd.setreceiver(on_response)
print("Connection started")

while True:
    delay=random()*args.delaymultip
    print("-----------------------------------")    
    print("Current price is: ", tickprice)
    if tickprice != 0:
        askprice = tickprice + random()       
        bidprice = askprice - random()
    else:
        askprice = random()*10
        bidprice = askprice + (random()*10)
    askstarttime = int((time()*1000)+(1000*60*60*random()*10))
    bidstarttime = int(askstarttime + random()*1000)
    bidstarttime = int(askstarttime)
    askwattage = random()*1000
    bidwattage = random()*1000
    askduration=random()
    bidduration=random()
    if args.bid:
        bidmsg = msg.getLineBidMessage(applicationKey, bidwattage, bidduration, bidstarttime, (bidwattage*bidduration), bidprice).strip('"')        
        snd.sendbidmsg(bidmsg)
        print(bidmsg)
    if args.ask:
        askmsg = msg.getLineAskMessage(applicationKey, askwattage, askduration, askstarttime, (askwattage*askduration), askprice).strip('"')      
        snd.sendaskmsg(askmsg)
        print(askmsg)

    #This will explicitly query for the replies which are then processed on the on_response callback function
    snd.checkreplies()
    print("Delaying ", delay, " seconds")
    sleep(delay)    

snd.closeconnection()
print("Closed connection")

 