import requests
from config import *
import json
#import datetime
import dateutil.parser
#https://opendata.transport.nsw.gov.au/sites/default/files/TfNSW_TripPlannerAPI_technical_doc.pdf


def get_directions (Date, Time, Origin, Destination, nb_journies):
    url = "https://api.transport.nsw.gov.au/v1/tp/trip"
    #itdDate = '20170429'
    #idtTime = '1635'
    itdDate = Date
    itdTime = Time
    coord_standard = "EPSG:4326"
    origin_coordinates = Origin['long'] + ":" + Origin["lat"] + ":" + coord_standard
    dest_coordinates = Destination['long'] + ":" + Destination['lat'] + ":" + coord_standard

    querystring = {"outputFormat":"rapidJSON","coordOutputFormat":"EPSG:4326","depArrMacro":"dep","itdDate":itdDate,"itdTime":itdTime,"type_origin":"coord","name_origin":origin_coordinates,"type_destination":"coord","name_destination":dest_coordinates,"calcNumberOfTrips":nb_journies,"TfNSWTR":"true","version":"10.2.1.15"}
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
        alerts = []
        legnumber = 0
        directions = []
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

            if rt == 'Walk':
                #call aaron's function
                leg_directions = walking_directions(leg)
            else:
                leg_directions = vehicle_directions(leg)
            directions.append(leg_directions)
            summary.append(rt)
            #alerts
#             [[], [{'timestamps': {'creation': '2016-11-22T04:42:00Z', 'lastModification
# ': '2016-11-22T04:43:00Z'}, 'properties': {'appliesTo': 'departingArriving', 'stopIDglobalID': '10101103:2000274,20006,20005,20004,2
# 0003'}, 'priority': 'veryLow', 'id': '6000034', 'version': '1', 'urlText': 'Departure or arrival wharf may change at short notice',
# 'url': 'http://localhost:8085/ics/XSLT_CM_SHOWADDINFO_REQUEST?infoID=6000034&seqID=1', 'content': '&nbsp;Please check indicator boar
# ds and listen for announcements.', 'subtitle': 'Departure or arrival wharf may change at short notice'}]]
            alerts.append(leg['infos'])
            legnumber += 1
        minutes = totalduration/60

        print(depart, arrive, minutes, directions)

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

def vehicle_directions(leg):
    stops = []
    for stop in leg['stopSequence']:
        #stops.append(stop['disassembledName'])
        # print(stop['parent'])
        # print(stop['parent']['disassembledName'])
        try:
            stops.append(stop['parent']['disassembledName'])
        except KeyError:
            stops.append(stop['parent']['name'])
    return stops

def walking_directions (leg): #get given one leg of the trip
    directions = []
    for section in leg["pathDescriptions"]:
        if section["distance"]:
            if section["turnDirection"] == "STRAIGHT":
                directions.append("continue straight down " + section["name"] + " for " + str(section["distance"]) + "m")
            else:
                directions.append("turn "+ section["turnDirection"].lower().replace("_"," ") + " down " + section["name"] + " and continue " + str(section["distance"]) + "m")
    return directions


if __name__ == '__main__':
    Origin = {'long' : '151.1930151', 'lat' : '-33.9247547'}
    Destination = {'long': '151.2066417', 'lat' : '-33.8689677'}
    Date = '20170430'
    Time = '0900'
    print(get_directions(Date,Time, Origin,Destination,5))
