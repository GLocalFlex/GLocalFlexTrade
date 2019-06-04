import trademessage.messageserializer as msg
import messenger.messagesender as snd
import socket
from random import random
from time import sleep
from time import time

def on_response(ch, method, props, body):
    print("REPLY MESSAGE:", body)

print("Starting connection")
applicationKey = snd.connecttobroker()
snd.setreceiver(on_response)
print("Started connection")

while True:
    delay=random()*100
    #applicationKey=socket.gethostbyname(socket.gethostname())
    askprice = random()*10
    bidprice = random()*10
    askstarttime = int((time()*1000)+(1000*60*60*random()*10))
    #bidstarttime = int((time()*1000)+(1000*60*60*random()*10))
    bidstarttime = askstarttime + 100
    askwattage = random()*1000
    bidwattage = random()*1000
    askduration=random()
    bidduration=random()
    askmsg = msg.getLineAskMessage(applicationKey, askwattage, askduration, askstarttime, (askwattage*askduration), askprice).strip('"')   
    bidmsg = msg.getLineBidMessage(applicationKey, bidwattage, bidduration, bidstarttime, (bidwattage*bidduration), bidprice).strip('"')        
    print(bidmsg)
    print(askmsg)
    snd.sendbidmsg(bidmsg)
    snd.sendaskmsg(askmsg)
    #This will explicitly query for the replies which are then processed on the on_response callback function
    snd.checkreplies()
    print("Delaying ", delay, " seconds")
    sleep(delay)    

snd.closeconnection()
print("Closed connection")

 