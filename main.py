import os, sys, json, requests
from flask import Flask, request
import apiai
from config import *
from threadsettings import *
from geolocation.main import GoogleMaps
from transport import *
from datetime import datetime

app = Flask(__name__)

# An endpoint to ApiAi, an object used for making requests to a particular agent.
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
google_maps = GoogleMaps(api_key=GOOGLE_MAPS_KEY)

user_location = {}
user_destination = {}
user_name = "mate"


@app.route('/', methods=['GET'])
def print_signage():
    return "Conversational Chatbot Webservice, send your data towards this/webhook!"


# Handling HTTP GET when Facebook subscribes to our Webhook.
@app.route('/webhook', methods=['GET'])
def handle_verification():
    print("Handling Verification.")
    # Checking if the GET was sent by Messenger by matching the configured secret token.
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        # Request.args contains the parsed contents of the query string.
        # The query string is appended to a HTTP call, containing parameters and values.
        print("Webhook verified!")
        # Returning a random string that messenger has sent to us, for verification on their end.
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Error, wrong validation token"


# Handling HTTP POST when Facebook sends us a payload of messages that have
# have been sent to our bot. We're responding to a Messenger callback, one of
# the events our webhook is subscribed to has fired.
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    global user_destination
    global user_location
    global user_name

    if data["object"] == "page":
        send_greetings()
        get_started()
        show_persistent_menu()
        # Iterating through entries and messaging events batched and sent to us by Messenger
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]  # the facebook ID
                user_name = str(get_username(sender_id))
                recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID
                if "postback" in messaging_event.keys():
                    if "payload" in messaging_event["postback"].keys():
                        payload = messaging_event["postback"]["payload"]
                        if str(payload) == "Successfully added new_thread's CTAs":
                            apiai_reply = parse_natural_text("hello")
                            apiai_reply = apiai_reply.replace("#username", user_name)
                            send_message_staggered(sender_id, apiai_reply)  # Sending a response to the user.
                if messaging_event.get("message"):  # Checking if the messaging even contains a message field.
                    if 'attachments' in messaging_event['message'].keys():
                        print("after map:" + str(user_destination))
                        user_location = messaging_event['message']['attachments'][0]['payload']
                        reply_text = "ok, I got you! Your location is " + str(
                            user_location) + " and you want to go to " + str(
                            user_destination) + ". Let me search for it."

                        # NSW TRANSPORT WS CALL
                        if len(user_destination) > 0 and len(user_location) > 0:
                            now = datetime.now()
                            this_date = now.strftime("%Y%m%d")
                            this_time = now.strftime("%H%M%S")
                            origin = {'long': str(user_location['coordinates']['long']),
                                      'lat': str(user_location['coordinates']['lat'])}

                            destination = {'long': str(user_destination['long']),
                                           'lat': str(user_destination['lat'])}
                            nb_journies = 1
                            reply_text = get_directions(this_date, this_time, origin, destination, nb_journies)
                            print(reply_text)
                            # reply_text = "🚏 Walk 8 min towards Queen Victoria Building. 🚏 Take the M50 bus next to Town Hall"
                        send_message_staggered(sender_id, reply_text)
                    else:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        apiai_reply = parse_natural_text(message_text).replace("#username", user_name)

                        if "#location" in apiai_reply:
                            print("entering the send location button")
                            send_location_button(sender_id)
                        else:
                            send_message_staggered(sender_id, apiai_reply)  # Sending a response to the user.

                    print("SENT MESSAGE")

    return "ok"


def get_address_location(address):
    location = None
    if type(address) is dict:
        if address["address"] != "":  # Exact location
            location = google_maps.search(location=address["address"])
        else:
            if address["place"] != "" and address["suburb"] != "":
                location = google_maps.search(location=address["place"])
            elif address["place"] != "":
                location = google_maps.search(location=address["place"])
            elif address["suburb"] != "":
                location = google_maps.search(location=address["suburb"])
    if location is not None:
        return {'lat': location.first().lat, 'long': location.first().lng}
    else:
        return address


# Sending a message back through Messenger.
def send_message(sender_id, message_text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

                      params={"access_token": PAGE_ACCESS_TOKEN},

                      headers={"Content-Type": "application/json"},

                      data=json.dumps({
                          "recipient": {"id": sender_id},
                          "message": {"text": message_text}
                      }))


# Sending a message back through Messenger.
def send_location_button(sender_id):
    print("Entered the function of the button")
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

                      params={"access_token": PAGE_ACCESS_TOKEN},

                      headers={"Content-Type": "application/json"},

                      data=json.dumps({
                          "recipient": {"id": sender_id},
                          "message": {
                              "text": "Ok, where are you now?",
                              "quick_replies": [
                                  {
                                      "content_type": "location",
                                  }
                              ]
                          }
                      }))


# Takes a string of natural language text, passes it to ApiAI, returns a
# response generated by an ApiAI bot.
def parse_natural_text(user_text):
    global user_destination
    # Sending a text query to our bot with text sent by the user.
    request = ai.text_request()
    request.query = user_text

    # Receiving the response.
    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']
    if (responseStatus == 200):
        if len(response['result']['parameters']) > 0:
            # Sending the textual response of the bot.
            user_destination = get_address_location(response['result']['parameters'])
            print("assignment:" + str(user_destination))
        print("in natural text")
        return response['result']['fulfillment']['speech']

    else:
        return ("Sorry, I couldn't understand that question")

        # NOTE:
        # At the moment, all messages sent to ApiAI cannot be differentiated,
        # they are processed as a single conversation regardless of concurrent
        # conversations. We need to perhaps peg a session id (ApiAI) to a recipient
        # id (Messenger) to fix this.

        # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"


# Sends the message in segments delimited by a period.
def send_message_staggered(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)

    for message in messages:
        send_message(sender_id, message)


if __name__ == '__main__':
    app.run(debug=True)
