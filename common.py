# pylint: disable=missing-docstring

from datetime import timedelta
from datetime import datetime
import config

AUTH = {'user': config.ANSWERHUB_USER, 'password': config.ANSWERHUB_PASS}
SLACK_WEB_HOOK = config.SLACK_WEB_HOOK

BASE_URL = config.BASE_URL
QUESTION_URL = BASE_URL + "/questions"

# Specific to AnswerHub
QUESTION_JSON_URL = BASE_URL + "/services/v2/question.json"

PAGE_SIZE_100 = "pageSize=100"

SORT_HOTTEST = "sort=hottest"
SORT_NEWEST = "sort=newest"

ONLY_UNANSWERED = "unanswered=true"

INCLUDED_VALUES = "includeOnly=id,slug,title,lastActiveDate"

# HTML
CSS_LINK = "<link rel='stylesheet' href='/assets/izzy.css' type='text/css'>"
JS_LINK = "<script src='/assets/izzy.js'></script>"
PAGE_HEADER = "<html><head>" + CSS_LINK + JS_LINK + "</head>"
START_HTML = PAGE_HEADER + "<body>"
END_HTML = "</body></html>"


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
