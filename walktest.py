from config import *
import json
#import datetime


l = '{"duration":780,"distance":797,"origin":{"id":"streetID:20956:3:95310008:1:Elphick Av:Mascot:Elphick Av::::ANY:DIVA_ADDRESS:4887692:3761718:GDAV::0","name":"3 Elphick Av, Mascot","type":"street","coord":[-33.92457,151.19305],"parent":{"id":"95310008|-1","type":"locality"},"departureTimePlanned":"2017-04-29T18:58:00Z","departureTimeEstimated":"2017-04-29T18:58:00Z","properties":{"downloads":[{"type":"RM","href":"FILELOAD?Filename=4724_4585372dep_4724_5432_78586500_00005ed0.pdf"}]}},"destination":{"isGlobalId":true,"id":"2020111","name":"Mascot Station","type":"platform","pointType":"Bstg","coord":[-33.92318,151.18722],"parent":{"id":"10101330","name":"Mascot Station","type":"stop","parent":{"id":"95310008|1","name":"Mascot","type":"locality"}},"arrivalTimePlanned":"2017-04-29T19:11:00Z","arrivalTimeEstimated":"2017-04-29T19:11:00Z","properties":{"downloads":[{"type":"RM","href":"FILELOAD?Filename=4724_4585374dep_4724_5432_78586500_00005ed0.pdf"}],"WheelchairAccess":"true"}},"transportation":{"product":{"class":100,"name":"Fussweg","iconId":100}},"footPathInfo":[{"position":"IDEST","duration":60,"footPathElem":[{"description":"","type":"STAIRS","levelFrom":0,"levelTo":-1,"level":"DOWN","origin":{"location":{"id":"10101330","type":"stop","coord":[-33.92308,151.1872]},"area":1,"platform":0,"georef":"100561947:90:GDAV:100"},"destination":{"location":{"id":"10101330","type":"stop","coord":[-33.92326,151.18745]},"area":11,"platform":0,"georef":"0:0:GDAV:100"}},{"description":"","type":"RAMP","levelFrom":-1,"levelTo":0,"level":"UP","origin":{"location":{"id":"10101330","type":"stop","coord":[-33.92326,151.18745]},"area":11,"platform":0,"georef":"0:0:GDAV:100"},"destination":{"location":{"id":"10101330","type":"stop","coord":[-33.92318,151.18722]},"area":10,"platform":0,"georef":"1014794:4459:GDAV:100"}}]}],"infos":[],"coords":[[-33.92457,151.19305],[-33.92457,151.19303],[-33.92458,151.19312],[-33.92458,151.19314],[-33.9246,151.19319],[-33.92462,151.19322],[-33.92463,151.19323],[-33.92464,151.19324],[-33.92467,151.19327],[-33.92471,151.19329],[-33.92476,151.19329],[-33.92521,151.19321],[-33.92513,151.1926],[-33.92503,151.19188],[-33.92478,151.19013],[-33.92443,151.18776],[-33.92437,151.18725],[-33.92434,151.18717],[-33.92358,151.18706],[-33.92307,151.18718],[-33.92308,151.1872],[-33.92326,151.18745],[-33.92318,151.1873]],"pathDescriptions":[{"turnDirection":"STRAIGHT","manoeuvre":"UNKNOWN","name":"Elphick Av","coord":[-33.92457,151.19303],"skyDirection":283,"duration":77,"cumDuration":77,"distance":87,"cumDistance":87,"fromCoordsIndex":0,"toCoordsIndex":11},{"turnDirection":"RIGHT","manoeuvre":"UNKNOWN","name":"Coward St","coord":[-33.92521,151.19321],"skyDirection":102,"duration":507,"cumDuration":584,"distance":568,"cumDistance":655,"fromCoordsIndex":11,"toCoordsIndex":17},{"turnDirection":"SLIGHT_RIGHT","manoeuvre":"UNKNOWN","name":"Bourke St","coord":[-33.92434,151.18717],"skyDirection":176,"duration":127,"cumDuration":711,"distance":142,"cumDistance":797,"fromCoordsIndex":17,"toCoordsIndex":19}],"properties":{"PTWalkMinutes":"1"}}'


leg = json.loads(l)




def walkDir (leg): #get given one leg of the trip
    directions = []
    for section in leg["pathDescriptions"]:
        if section["turnDirection"] == "STRAIGHT":
            directions.append("continue straight down " + section["name"] + " for " + str(section["distance"]) + "m")
        else:
            directions.append("turn "+ section["turnDirection"].lower().replace("_"," ") + " down " + section["name"] + " and continue " + str(section["distance"]) + "m")
    return directions

print(walkDir(leg))



