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

def createLineMessage(order, applicationKey, wattage, duration, starttime, totalenergy, orderprice):
    lineordermsg = ""
    if "ask" in order:
        lineordermsg = "{0},applicationKey={1},version=0,starttime={2} wattage={3},duration={4},totalenergy={5},askingprice={6}"
    if "bid" in order:
        lineordermsg = "{0},applicationKey={1},version=0,starttime={2} wattage={3},duration={4},totalenergy={5},biddingprice={6}"
    return lineordermsg.format(order, applicationKey, starttime, wattage, duration, totalenergy, orderprice)

def getAskMessageJSON(applicationKey, wattage, duration, starttime, totalenergy, askingprice):
    askmsg = createaskmessage("ask", applicationKey, wattage, duration, starttime, totalenergy, askingprice)
    return json.dumps(askmsg)
    
def getBidMessageJSON(applicationKey, wattage, duration, starttime, totalenergy, biddingprice):
    bidmsg = createbidmessage("bid", applicationKey, wattage, duration, starttime, totalenergy, biddingprice)
    return json.dumps(bidmsg)

def getLineAskMessage(applicationKey, wattage, duration, starttime, totalenergy, askingprice):
    askmsg = createLineMessage("ask", applicationKey, wattage, duration, starttime, totalenergy, askingprice)
    return json.dumps(askmsg)
    
def getLineBidMessage(applicationKey, wattage, duration, starttime, totalenergy, biddingprice):
    bidmsg = createLineMessage("bid", applicationKey, wattage, duration, starttime, totalenergy, biddingprice)
    return json.dumps(bidmsg)