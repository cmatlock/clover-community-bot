# pylint: disable=missing-docstring

from datetime import timedelta
from datetime import datetime
import threading
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
PAGE_SIZE_1 = "pageSize=1"

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

CLOVER_OWNED_QUESTIONS = []
clover_lock = threading.Lock()

USER_OWNED_QUESTIONS = []
user_lock = threading.Lock()

class QuestionCard:
    def __init__(self, question):
        self.question_json = question
        self.id = question['id']
        self.slug = question['slug']
        self.title = question['title']
        self.lastActiveDate = question['lastActiveDate']
        self.lastActiveUserId = question['lastActiveUserId']
        self.childrenIds = question['childrenIds']
        self.commentIds = question['commentIds']
        self.answers = question['answers']
        self.author = question['author']
        self.marked = question['marked']

        self.browser_url = create_question_url(question)
        self.answers_url_api = self.create_question_answers_api()
        self.comments_url_api = self.create_question_comments_api()
        self.status = self.question_status()
        self.answer_count = question['answerCount']
        self.last_active = timestamp_to_date(question["lastActiveDate"])

        self.delete_url = self.create_question_delete_api()
        self.answers = []
        self.html_card = self.html_bootstrap_card()

    def console_question(self):
        print '{:^80}'.format("Current Question")

        print '{:<80}'.format("Title       : " + self.title)
        print '{:<80}'.format("URL         : " + self.browser_url)
        print '{:<80}'.format("Answer Count: " + str(self.answer_count))
        print '{:<80}'.format("Last Active : " + str(self.last_active.date()))

        print '{:~^80}'.format("")

    def console_answers(self):
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

    def html_bootstrap_card(self):
        response = ""
        question_card_start = "<div class='card question border-" + self.status + "'>"
        question_card_end = "</div>"

        response += question_card_start
        response += self.question_header()
        response += self.question_body()
        response += self.question_footer()
        response += question_card_end

        return response

    def question_header(self):
        response = ""

        question_title_start = "<div class='card-header font-weight-bold text-truncate bg-" + self.status + "'>"
        question_title_end = "</div>"

        response += question_title_start
        response += self.title
        response += question_title_end

        return response

    def question_body(self):
        response = "<div class='card-body bg-transparent'>"

        response += self.all_users_comments(self.comments_url_api)
        response += self.all_users_answers(self.answers_url_api)

        return response + "</div>"

    def question_footer(self):
        response = ""

        question_footer_start = "<div class='card-footer font-italic border-" + self.status + "'>"
        question_footer_end = "</div>"

        response += question_footer_start
        response += "<div class='float-left'>" + create_time_label(self.lastActiveDate) + "</div>"
        response += "<a href='" + self.browser_url + "' class='btn btn-sm btn-dark float-right' target='_blank'> View </a>"
        response += question_footer_end

        return response

    def question_status(self):
        # returns Bootstrap keyword for color/formatting

        if self.marked:
            return "success"

        # Not an accurate representation; find a better indicator
        if (len(self.childrenIds)) == 0:
            return "danger"

        return "warning"

    def all_users_comments(self, question):
        user_list = "<dt>Commenting Users:</dt>"
        unique_names = []

        comments = get_results(question)["list"]

        for comment in comments:
            name = comment["author"]["username"]
            if name not in unique_names:
                unique_names.append(name)
                user_list += (
                    "<dd>- " + str(name) + "</dd>"
                )

        if not unique_names:
            user_list += "<dd>No one has commented...</dd>"

        return user_list

    def all_users_answers(self, question):
        user_list = "<dt>Answering Users: </dt>"
        unique_names = []

        answers = get_results(question)["list"]

        for answer in answers:
            name = answer["author"]["username"]
            if name not in unique_names:
                unique_names.append(name)
                user_list += (
                    "<dd>- " + str(name) + "</dd>"
                )

        if not unique_names:
            user_list += "<dd>No one has answered...</dd>"

        return user_list

    def create_question_delete_api(self):
        return BASE_URL + ANSWERHUB_API + "node/" + str(self.id) + "/delete" + JSON

    def create_question_comments_api(self):
        return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(self.id) + "/comment" + JSON

    def create_question_answers_api(self):
        return BASE_URL + ANSWERHUB_QUESTION_API + "/" + str(self.id) + "/answer" + JSON

def get_results(url):
    comm_response = requests.get(url, auth=(AUTH["user"], AUTH["password"])).text
    return json.loads(comm_response)

def put_results(url):
    comm_response = requests.put(url, auth=(AUTH["user"], AUTH["password"])).text
    return comm_response

def get_clover_ids():
    clover_users = get_results(CLOVER_USERS_URL)["list"]
    ids = []
    for user in clover_users:
        ids.append(user.get("id"))

    return ids

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

def get_page_of_questions(num, base_url):
    return get_results(base_url + "&page=" + num)["list"]

def add_to_user_questions(question):
    user_lock.acquire()
    USER_OWNED_QUESTIONS.append(question)
    user_lock.release()

def add_to_clover_questions(question):
    clover_lock.acquire()
    CLOVER_OWNED_QUESTIONS.append(question)
    clover_lock.release()