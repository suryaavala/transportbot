###############################################################################
# https://developers.facebook.com/docs/messenger-platform/thread-settings
###############################################################################
import os
import sys
import json
import requests
from config import *


def send_greetings():
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type": "greeting",
        "greeting": {
            "text": "G'day {{user_first_name}} I'm TransportBot! I'm ready to help you get real time directions in NSW."
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)


def get_started():
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": [
            {
                "payload": "Successfully added new_thread's CTAs"
            }
        ]
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)


def delete_get_started(recipient_id):
    print("====================> NEW USER: delete getting started for user {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type": "call_to_actions",
        "thread_state": "new_thread"
    })
    r = requests.delete("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)


def show_persistent_menu():
    print("show persistent menu for user")

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type": "call_to_actions",
        "thread_state": "existing_thread",
        "call_to_actions": [
            {
                "type": "postback",
                "title": "Fastest",
                "payload": "MENU_ALL"
            },
            {
                "type": "postback",
                "title": "Fewer transfers",
                "payload": "MENU_FAV"
            },
            {
                "type": "postback",
                "title": "Least walking",
                "payload": "MENU_FAV"
            },
            {
                "type": "web_url",
                "title": "Like Facebook Page",
                "url": "https://www.facebook.com/eventochatbot/"
            },

        ]
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
