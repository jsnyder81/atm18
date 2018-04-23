"""Listener module."""
from sys import platform as _platform
from os import environ

from pync import Notifier
from flask import Flask, request
from random import randint
import json
import requests

clearpass_auth_token = "Bearer xxxx"
clearpass_fqdn = "192.0.2.1"

app = Flask(__name__)

# check for ngrok subdomain
ngrok = environ.get("NGROK_SUBDOMAIN", "")


def display_intro():
    """Helper method to display introduction message."""
    if ngrok:
        message = "".join([
            "You can access this webhook publicly via at ",
            "http://%s.ngrok.io/webhook. \n" % ngrok,
            "You can access ngrok's web interface via http://localhost:4040"
        ])
    else:
        message = "Webhook server online! Go to http://localhost:5000"
    print message


def display_html(request):
    """
    Helper method to display message in HTML format.

    :param request: HTTP request from flask
    :type  request: werkzeug.local.LocalProxy
    :returns message in HTML format
    :rtype basestring
    """
    url_root = request.url_root
    if ngrok:
        return "".join([
            """Webhook server online! Go to """,
            """<a href="http://localhost:4040">http://localhost:4040</a>"""
        ])
    else:
        return "".join([
            """Webhook server online! Go to """,
            """<a href="http://localhost:4040">http://localhost:4040</a>"""
        ])


@app.route("/", methods=["GET"])
def index():
    """Endpoint for the root of the Flask app."""
    return display_html(request)


@app.route("/webhook", methods=["GET", "POST"])
def tracking():
    """Endpoint for receiving webhook from bitbucket."""
    if request.method == "POST":
        data = request.get_json()
        processed_data = parse_Chatbot(data)
        results = create_ClearpassUser(processed_data, clearpass_auth_token)
        print(results)
        print(str(results.text))
        print "Webhook received!"
        my_response = {}
        my_response['displayText'] = "User has been created, they should receive an SMS with their login"
        #my_response['data'] = results.text
        return json.dumps(my_response)

    else:
        return display_html(request)

def parse_Chatbot(my_data):
    process_data = {}
    process_data['username'] = my_data['result']['parameters']['FirstName'] + my_data['result']['parameters']['LastName'] + str(randint(1000, 9999))
    process_data['email'] = my_data['result']['parameters']['Email']
    process_data['visitor_phone'] = my_data['result']['parameters']['Phone']
    process_data['enabled'] = True
    process_data['role_id'] = "2"
    process_data["auto_send_sms"] = "1"
    process_data['password'] = str(randint(1000,9999))
    print(json.dumps(process_data))
    return process_data

def create_ClearpassUser(my_data, my_auth_token):
    requests.packages.urllib3.disable_warnings()
    headers = {'Authorization': my_auth_token, 'Cache-Control': "no-cache"}
    response = aruba_Post("/api/guest", json.dumps(my_data), clearpass_auth_token)
    print(str(response.status_code))
    print(str(response.text))
    return response

def get_ClearpassUser(my_auth_token):
    requests.packages.urllib3.disable_warnings()
    headers = {'Authorization': my_auth_token, 'Cache-Control': "no-cache"}
    response = aruba_Get("/api/guest", clearpass_auth_token)
    print(str(response.status_code))
    print(str(response.text))
    return response

def aruba_Post(url_extention, payload, my_auth_token):
    requests.packages.urllib3.disable_warnings()
    my_session = requests.Session()
    my_req_url = "https://" + clearpass_fqdn + url_extention
    print(my_req_url)
    print(payload)
    headers = {'Authorization': my_auth_token, 'Cache-Control': "no-cache", 'Content-Type': "application/json"}
    response = my_session.post(my_req_url, headers=headers, data=payload, verify=False)
    return response

def aruba_Get(my_url_extention, my_auth_token):
    my_session = requests.Session()
    my_req_url = "https://" + clearpass_fqdn + my_url_extention
    headers = {'Authorization': my_auth_token, 'Cache-Control': "no-cache"}
    response = my_session.get(my_req_url, headers=headers, verify=False)
    return response

if __name__ == "__main__":
    display_intro()
    app.run(host="0.0.0.0", port=5000, debug=True)
