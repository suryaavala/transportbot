import requests
from config import *
import json
#import datetime
import dateutil.parser

def get_directions (Date, Time, Origin, Destination, nb_journies):
    url = "https://api.transport.nsw.gov.au/v1/tp/trip"
    #itdDate = '20170429'
    #idtTime = '1635'
    itdDate = Date
    itdTime = Time

    querystring = {"outputFormat":"rapidJSON","coordOutputFormat":"EPSG:4326","depArrMacro":"dep","itdDate":itdDate,"itdTime":itdTime,"type_origin":"any","name_origin":"10101331","type_destination":"any","name_destination":"10102027","calcNumberOfTrips":nb_journies,"TfNSWTR":"true","version":"10.2.1.15"}
    apikey = 'apikey ' + TRANSPORT_API_KEY
    headers = {
        'authorization': apikey,
        'cache-control': "no-cache",
        'postman-token': "66c25c3b-ab19-97a2-37d1-54a4e9f0cf6b"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    decoded = json.loads(response.text)
    print(len(decoded['journeys']))
    for journey in decoded['journeys']:

        legs = journey['legs']
        fares = journey['fare']
        totalduration = 0
        summary = []
        legnumber = 0
        for leg in legs:
            totalduration += leg['duration']
            origin = leg['origin']
            destination = leg['destination']
            if legnumber == 0:
                #depart = origin['departureTimePlanned']
                depart = dateutil.parser.parse(origin['departureTimePlanned'])
            if legnumber == len(legs) -1:
                #arrive = origin['departureTimePlanned']
                arrive = dateutil.parser.parse(origin['departureTimePlanned'])
            transportation = leg['transportation']
            routetype = transportation['product']['class']
            rt = transport_tpyes(routetype)
            summary.append(rt)
            legnumber += 1
        minutes = totalduration/60

        print(depart, arrive, minutes)

        print ("->".join(summary))
    return summary
def transport_tpyes(routType):
    return {
        1: 'Train',
        4: 'Light Rail',
        5: 'Bus',
        7: 'Coach',
        9: 'Ferry',
        11: 'School Bus',
        99: 'Walk',
        100: 'Walk'
    } [routType]

if __name__ == '__main__':
    print(get_directions('20170430','0010','d','o',5))
