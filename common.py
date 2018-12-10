# pylint: disable=missing-docstring

from datetime import timedelta
from datetime import datetime
import json
import requests
import config


SLACK_WEB_HOOK = config.SLACK_WEB_HOOK



# Specific to AnswerHub
AUTH = {'user': config.ANSWERHUB_USER, 'password': config.ANSWERHUB_PASS}

BASE_URL = config.BASE_URL
QUESTION_URL = BASE_URL + "/questions"
JSON = ".json"

ANSWERHUB_QUESTION_API = "/services/v2/question"
QUESTION_JSON_URL = BASE_URL + ANSWERHUB_QUESTION_API + JSON

testing_url = "https://community.clover.com/services/v2/question/9233.json"

PAGE_SIZE_100 = "pageSize=100"
PAGE_SIZE_5 = "pageSize=5"

SORT_HOTTEST = "sort=hottest"
SORT_NEWEST = "sort=newest"

ONLY_UNANSWERED = "unanswered=true"

INCLUDED_VALUES = "includeOnly=id,slug,title,lastActiveDate"

# HTML
CSS_LINK = (
    "<link rel='stylesheet' href='/assets/izzy.css' type='text/css'>" +
    "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/foundation-sites@6.5.1/dist/css/foundation.min.css' integrity='sha256-1mcRjtAxlSjp6XJBgrBeeCORfBp/ppyX4tsvpQVCcpA= sha384-b5S5X654rX3Wo6z5/hnQ4GBmKuIJKMPwrJXn52ypjztlnDK2w9+9hSMBz/asy9Gw sha512-M1VveR2JGzpgWHb0elGqPTltHK3xbvu3Brgjfg4cg5ZNtyyApxw/45yHYsZ/rCVbfoO5MSZxB241wWq642jLtA==' crossorigin='anonymous'>"
)
JS_LINK = (
    "<script src='https://code.jquery.com/jquery-3.3.1.min.js' integrity='sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=' crossorigin='anonymous'></script>" +
    "<script src='/assets/izzy.js'></script>" +
    "<script src='https://cdn.jsdelivr.net/npm/foundation-sites@6.5.1/dist/js/foundation.min.js' integrity='sha256-WUKHnLrIrx8dew//IpSEmPN/NT3DGAEmIePQYIEJLLs= sha384-53StQWuVbn6figscdDC3xV00aYCPEz3srBdV/QGSXw3f19og3Tq2wTRe0vJqRTEO sha512-X9O+2f1ty1rzBJOC8AXBnuNUdyJg0m8xMKmbt9I3Vu/UOWmSg5zG+dtnje4wAZrKtkopz/PEDClHZ1LXx5IeOw==' crossorigin='anonymous'></script>" 
)

START_HTML = "<html>"
END_HTML = "</html>"
PAGE_HEADER = "<head>" + CSS_LINK + JS_LINK + "</head>"
WEB_PAGE_START = PAGE_HEADER + "<body>"
WEB_PAGE_END = "</body>" + END_HTML



def get_results(url):
    comm_response = requests.get(url, auth=(AUTH["user"], AUTH["password"])).text
    return json.loads(comm_response)

def time_label(question_time):
    age = datetime.now() - question_time
    return str(age.days) + " days ago"

def older_than_two_days(timestamp):
    return timestamp_to_date(timestamp) <= (datetime.now() - timedelta(days=2))

def younger_than_one_month(timestamp):
    return timestamp_to_date(timestamp) >= (datetime.now() - timedelta(days=30))

def timestamp_to_date(milliseconds):
    return datetime.fromtimestamp(milliseconds/1e3)

def create_time_label(question_timestamp):
    return time_label(timestamp_to_date(question_timestamp))

def create_question_url(question):
    return QUESTION_URL + "/" + str(question["id"]) + "/" + question["slug"] + ".html"

def create_question_comments_api(question):
    return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(question["id"]) + "/comment" + JSON

def create_question_answers_api(question):
    return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(question["id"]) + "/answer" + JSON
