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

ANSWERHUB_API = "/services/v2/"
ANSWERHUB_QUESTION_API = ANSWERHUB_API + "question"


QUESTION_JSON_URL = BASE_URL + ANSWERHUB_QUESTION_API + JSON

APP_MARKET_SPACE = "spaceId=12"

PAGE_SIZE_100 = "pageSize=100"
PAGE_SIZE_50 = "pageSize=50"
PAGE_SIZE_30 = "pageSize=30"
PAGE_SIZE_10 = "pageSize=10"

SORT_HOTTEST = "sort=hottest"
SORT_NEWEST = "sort=newest"

ONLY_UNANSWERED = "unanswered=true"

INCLUDED_VALUES = "includeOnly=id,slug,title,lastActiveDate,lastActiveUserId,childrenIds,commentIds,answers,author,marked"

# List of current Clover Employees active on Community
CLOVER_USERS_URL = BASE_URL + ANSWERHUB_API + "group/16/user" + JSON + "?includeOnly=id"

# qObject = common.QuestionCard(common.get_results("https://community.clover.com/services/v2/question/14206.json"))

# HTML
CSS_LINK = (
    "<link rel='stylesheet' href='/assets/izzy.css' type='text/css'>" +
    "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css' integrity='sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO' crossorigin='anonymous'>"
)
JS_LINK = (
    "<script src='https://code.jquery.com/jquery-3.3.1.min.js' integrity='sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=' crossorigin='anonymous'></script>" +
    "<script src='/assets/izzy.js'></script>" +
    "<script src='https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js' integrity='sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy' crossorigin='anonymous'></script>"
)

START_HTML = "<html>"
END_HTML = "</html>"

PAGE_HEADER = "<head>" + CSS_LINK + JS_LINK + "</head>"

WEB_PAGE_START = PAGE_HEADER + "<body>"
WEB_PAGE_END = "</body>" + END_HTML

class QuestionCard:
    def __init__(self, question):
        self.question_json = question
        self.title = question['title']
        self.browser_url = create_question_url(question)
        self.answer_count = question['answerCount']
        self.last_active = timestamp_to_date(question["lastActiveDate"])

        self.delete_url = create_question_delete_api(question)
        self.answers = []

    def display_question(self):
        print '{:^80}'.format("Current Question")

        print '{:<80}'.format("Title       : " + self.title)
        print '{:<80}'.format("URL         : " + self.browser_url)
        print '{:<80}'.format("Answer Count: " + str(self.answer_count))
        print '{:<80}'.format("Last Active : " + str(self.last_active.date()))

        print '{:~^80}'.format("")

    def display_answers(self):
        if self.answer_count == 0:
            print '{:=^80}'.format("No Answers Posted")
            return

        if self.answers == []:
            self.answers = get_results(create_question_answers_api(self.question_json))['list']
        
        print '{:=^80}'.format("Answers")
        for answer in self.answers:
            print '{:^40}'.format("Author: " + answer['author']['username'])
            print '{:<80}'.format("Body: " + answer['body'])
            print '{:-^80}'.format("")




def get_results(url):
    comm_response = requests.get(url, auth=(AUTH["user"], AUTH["password"])).text
    return json.loads(comm_response)

def put_results(url):
    comm_response = requests.put(url, auth=(AUTH["user"], AUTH["password"])).text
    return comm_response

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

def create_question_delete_api(question):
    return BASE_URL + ANSWERHUB_API + "node/" + str(question["id"]) + "/delete" + JSON

def create_question_comments_api(question):
    return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(question["id"]) + "/comment" + JSON

def create_question_answers_api(question):
    return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(question["id"]) + "/answer" + JSON

def get_page_of_questions(num, base_url):
    return get_results(base_url + "&page=" + num)["list"]