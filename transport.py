import requests
from config import *
import json
#import datetime
import dateutil.parser
#https://opendata.transport.nsw.gov.au/sites/default/files/TfNSW_TripPlannerAPI_technical_doc.pdf
from datetime import datetime
from dateutil import tz

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
    #print(len(decoded['journeys']))
    trip = {}
    for journey in decoded['journeys']:

        legs = journey['legs']
        fares = journey['fare']['tickets'][0]['priceBrutto']
        totalduration = 0
        summary = []
        alerts = []
        legnumber = 0
        directions = []
        for leg in legs:
            totalduration += leg['duration']
            origin = leg['origin']
            destination = leg['destination']
            #print(origin, destination)
            if legnumber == 0:
                #depart = origin['departureTimePlanned']
                depart = dateutil.parser.parse(origin['departureTimePlanned'])
                depart = _date_conv(depart)
            if legnumber == len(legs) -1:
                #arrive = origin['departureTimePlanned']
                arrive = dateutil.parser.parse(destination['arrivalTimeEstimated'])
                arrive = _date_conv(arrive)
            transportation = leg['transportation']
            routetype = transportation['product']['class']
            rt = transport_tpyes(routetype)
            leg_arrive = _date_conv(dateutil.parser.parse((leg['origin']["departureTimeEstimated"])))
            leg_depart = _date_conv(dateutil.parser.parse((leg['destination']["arrivalTimeEstimated"])))
            leg_directions = {}
            if rt == 'Bus':
                rt += " "+leg['transportation']['disassembledName']
            leg_directions['arrive'] = leg_arrive
            leg_directions['depart'] = leg_depart
            leg_directions['type'] = rt

            if rt == 'Walk':
                #call aaron's function
                leg_directions['starting_point'],leg_directions['ending_point'],leg_directions['dir'] = walking_directions(leg)
            else:
                leg_directions['dir'] = vehicle_directions(leg)
                leg_directions['starting_point'] = vehicle_directions(leg)[0]
                leg_directions['ending_point'] = vehicle_directions(leg)[-1]
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

        #print(depart, arrive, minutes, directions)

        #print ("->".join(summary))
        break
    '''
    legs = journey['legs']
    fares = journey['fare']
    totalduration = 0
    summary = []
    alerts = []
    legnumber = 0
    directions = []
    '''
    trip ['fare'] = fares
    # f = open('fare.txt', 'w')
    # fr = json.dumps(fares)
    # f.write(fr)
    trip ['duration'] = minutes
    trip ['summary'] = '->'.join(summary)
    trip ['directions'] = directions
    #trip ['alerts'] = alerts
    trip ['start'] = depart
    trip ['end'] = arrive

    detailed_trip = ''
    detailed_trip = _formatting_output(trip)
    return detailed_trip



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
    try:
        starting_point = leg['origin']['name']
        ending_point = leg['destination']['name']
        for section in leg["pathDescriptions"]:
            if section["distance"]:
                if section["turnDirection"] == "STRAIGHT":
                    directions.append("continue straight down " + section["name"] + " for " + str(section["distance"]) + "m")
                else:
                    directions.append("turn "+ section["turnDirection"].lower().replace("_"," ") + " down " + section["name"] + " and continue " + str(section["distance"]) + "m")
        return (starting_point, ending_point, directions)
    except KeyError:
        return
def _date_conv(date):


    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('AEST')

    # # METHOD 2: Auto-detect zones:
    # from_zone = tz.tzutc()
    # to_zone = tz.tzlocal()

    # utc = datetime.utcnow()
    # utc = datetime.strptime('2011-01-21 02:37:21', '%Y-%m-%d %H:%M:%S')

    # # Tell the datetime object that it's in UTC time zone since
    # # datetime objects are 'naive' by default
    # utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    return date.astimezone(to_zone)

def _formatting_output(trip):
    '''You will be Walking from starting_point to ending_point
    Then you will be taking a bus from stop[o] to stop[1]
    Then you will ---
    If you start now, you should reach your destination by end
    It is going to take about duration minutes and cost you around $fare.


    Walk/take the bus to ending_point
      - dir[0]
      - dir[1]

    Take the bus from stop[0] to stop [1]
    It stops at the following:
      -stop[0]
      -stop[1]


    You are where you want to be ;)
    '''
    trip_summary = ''
    leg_summary = ''
    final_message = "I\'m hoping you are where you wanted to be :P"

    for direction in trip['directions']:
        if direction['type'] == 'Walk':
            trip_summary += 'You\'ll {} from {} -> {}\n'.format('Walk', direction['starting_point'], direction['ending_point'])
            leg_summary += '{} from {} to {}:\n'.format('Walk', direction['starting_point'], direction['ending_point'])
            leg_summary += "\t-" + "\n\t-".join(direction['dir']) + '. '
        else:
            trip_summary += 'You\'ll take {} from {} -> {}\n'.format(direction['type'], direction['dir'][0],direction['dir'][-1])
            leg_summary += '\nTake the {} from {} to {},at {}'.format(direction['type'], direction['starting_point'], direction['ending_point'],direction['depart'].strftime("%H:%M"))
            #leg_summary += 'It leaves at {}, and stops at:\n'.format(direction['depart'])
            #leg_summary += "\t-" + "\n\t-".join(direction['dir'])
            leg_summary += '\nYou will arrive by {}'.format(direction['arrive'].strftime("%H:%M")) + '. '

    trip_summary += 'If you start {}, you should reach your destination by {}\nIt is going to take about {} minutes and cost you around {} bucks.'.format('now', trip['end'].strftime("%H:%M"),str(int(trip['duration'])), trip['fare'])

    return trip_summary + "\n" + leg_summary + "\n" + final_message



if __name__ == '__main__':
    Origin = {'long' : '151.1930151', 'lat' : '-33.9247547'}
    Destination = {'long': '151.187339', 'lat' : '-33.9232436'}
    Date = '20170430'
    Time = '0900'
    print(get_directions(Date,Time, Origin,Destination,5))
