# pylint: disable=missing-docstring

# import sys
# sys.path.append("lib")

import json
from datetime import datetime
from datetime import timedelta

import requests
import webapp2 # webob, paste

import config

AUTH = {'user': config.ANSWERHUB_USER, 'password': config.ANSWERHUB_PASS}
URL = (
    "https://community.clover.com/services/v2/question.json?unanswered=true&pageSize=100"
    "&sort=newest&includeOnly=id,slug,title,lastActiveDate"
)
BASE_URL = config.BASE_URL

SLACK_WEB_HOOK = config.SLACK_WEB_HOOK
CCBOT_ID = None

def daily_digest():
    # web_response = json.loads(requests.get(url, auth=(auth["user"], auth["password"])).text)
    comm_response = requests.get(URL, auth=(AUTH["user"], AUTH["password"])).text
    web_response = json.loads(comm_response)

    response = ""
    top_questions = top_ten_questions(web_response["list"])
    for question in top_questions:
        response += (
            "\n- *[" + time_label(timestamp_to_date(question["lastActiveDate"])) + "]* <" +
            BASE_URL + str(question["id"]) + "/" + question["slug"] + ".html|" +
            question["title"] + ">"
        )
    return response

def top_ten_questions(question_list):
    sorted_web_response = sorted(question_list, key=lambda x_y: x_y["lastActiveDate"])

    chosen_ones = []
    for question in sorted_web_response:
        if all([
                older_than_two_days(question["lastActiveDate"]),
                younger_than_one_month(question["lastActiveDate"])
        ]):
            chosen_ones.append(question)
            if len(chosen_ones) >= 10:
                break
    return chosen_ones

def time_label(question_time):
    age = datetime.now() - question_time
    return str(age.days) + " days ago"

### Requirements for top questions

def older_than_two_days(timestamp):
    return timestamp_to_date(timestamp) <= (datetime.now() - timedelta(days=2))

def younger_than_one_month(timestamp):
    return timestamp_to_date(timestamp) >= (datetime.now() - timedelta(days=30))

def timestamp_to_date(milliseconds):
    return datetime.fromtimestamp(milliseconds/1e3)

class DailyDigest(webapp2.RequestHandler):
    def post(self):
        text = "Here you go!"
        fallback = "Required plain-text summary of the attachment."
        color = "#2eb886"
        pretext = "Your Daily Digest"
        attachments = [{
            "fallback": fallback,
            "color": color,
            "pretext": pretext,
            "text": daily_digest()
        }]
        slack_response = {"text": text, "attachments": attachments}
        response_object = webapp2.Response(json.dumps(slack_response))
        response_object.content_type = "application/json"

        return response_object


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

APP = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/daily_digest', DailyDigest),
], debug=True)

if __name__ == "__main__":
    from paste import httpserver
    httpserver.serve(APP, host='127.0.0.1', port='8080')
