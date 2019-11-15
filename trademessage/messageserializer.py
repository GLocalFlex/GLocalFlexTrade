import json

def createJSONMessage(order, applicationKey, wattage, duration, starttime, totalenergy, orderprice):
    trademessage={}
    trademessage['order']=order
    trademessage['applicationKey']=applicationKey
    trademessage['version']=0
    trademessage['starttime']=starttime
    trademessage['wattage']=wattage
    trademessage['duration']=duration
    trademessage['totalenergy']=totalenergy
    if "ask" in order:
        trademessage['askingprice']=orderprice
    if "bid" in order:
        trademessage['biddingprice']=orderprice
    return trademessage

def createLineMessage(order, applicationKey, wattage, duration, starttime, totalenergy, orderprice, expirationtime):
    starttime=int(starttime)
    lineordermsg = ""
    if "ask" in order:
        lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},askingprice={6},expirationtime={7}i"
    if "bid" in order:
        lineordermsg = "{0},applicationKey={1},version=1 starttime={2}i,wattage={3},runtime={4}i,totalenergy={5},biddingprice={6},expirationtime={7}i"
    return lineordermsg.format(order, applicationKey, starttime, wattage, duration, totalenergy, orderprice, expirationtime)

def getAskMessageJSON(applicationKey, wattage, duration, starttime, totalenergy, askingprice):
    askmsg = createJSONMessage("ask", applicationKey, wattage, duration, starttime, totalenergy, askingprice)
    return json.dumps(askmsg)

def getBidMessageJSON(applicationKey, wattage, duration, starttime, totalenergy, biddingprice):
    bidmsg = createJSONMessage("bid", applicationKey, wattage, duration, starttime, totalenergy, biddingprice)
    return json.dumps(bidmsg)

def getLineAskMessage(applicationKey, wattage, duration, starttime, totalenergy, askingprice, expirationtime):
    askmsg = createLineMessage("ask", applicationKey, wattage, duration, starttime, totalenergy, askingprice, expirationtime)
    return json.dumps(askmsg)

def getLineBidMessage(applicationKey, wattage, duration, starttime, totalenergy, biddingprice, expirationtime):
    bidmsg = createLineMessage("bid", applicationKey, wattage, duration, starttime, totalenergy, biddingprice, expirationtime)
    return json.dumps(bidmsg)
