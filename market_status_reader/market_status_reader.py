import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient

__currentEtag = None

def checkIfResourceUpdated(baseURL, authToken, etag):
    header = {'Authorization' : 'Bearer '+authToken, 'Accept':'application/json'}
    url = baseURL+":3000/deals"
    resp = requests.head(url, headers=header)
    if resp.status_code == 200:
        if 'ETag' in resp.headers.keys():
            if etag is not None:
                if etag != resp.headers['ETag'] and resp.headers['ETag'] is not None:
                    return True
    return False
                    

def fetchClosedDeals(baseURL, authToken):
    global __currentEtag
    header = {'Authorization' : 'Bearer '+authToken, 'Accept':'application/json'}    
    url = baseURL+":3000/deals/?relativeTime=1h"
    resp = requests.get(url, headers=header)
    if resp.status_code == 200:        
        if checkIfResourceUpdated(baseURL, authToken, __currentEtag) or __currentEtag is None:
            __currentEtag = resp.headers['ETag']
        return resp.json()
    else:
        return None   

def convertMSTimeStampToRFC3339(timestamp):
    return datetime.datetime.fromtimestamp((timestamp/1000)).isoformat("T")+"Z"


    
if __name__ == '__main__':
    #readClosedOrdersFromCSVFile('deals.csv')
    token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1ZGY4OTQ0OWU2YTgwYzRiMGQyODZlODIiLCJ1dWlkIjoiODVkMGRhOTItN2M2Zi00NzVhLTkzZGItYjZmYWIxMjJmNWI2IiwiaWF0IjoxNTc2NTcyMDcwLCJleHAiOjE2NzExODAwNzB9._kpdJzZXnIamXFCnQCOlfF3D4W8yIjaBmEqKGe7l4Lg'    
    deals = fetchClosedDeals('http://www.fleximarex.com', token)
    #for idx, deal in enumerate(deals):
    #    #{'time': '2019-12-19T13:12:23.782Z', 'starttime': 1576767240000, 'runtime': 60000, 'price': 35.19229105439947, 'totalenergy': #1.640582512353486, 'totalprice': 57.73585727350179}
    #    #datetime.datetime.fromtimestamp(1576769100).isoformat("T")+"Z"
    #    print(str(idx)+', '+deal['time']+', '+str(convertMSTimeStampToRFC3339(deal['starttime']))+', '+str(deal['runtime'])+', #'+str(deal['price'])+', '+str(deal['totalenergy'])+', '+str(deal['totalprice']))
    df = pd.DataFrame(deals)    

    