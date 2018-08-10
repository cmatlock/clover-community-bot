import webapp2
import config
import requests
import json

from datetime import timedelta
from datetime import datetime

AUTH = {'user': config.ANSWERHUB_USER, 'password': config.ANSWERHUB_PASS}
URL = (
    "https://community.clover.com/services/v2/question.json?pageSize=100"
    "&sort=hottest"
)
BASE_URL = config.BASE_URL

def hottest_month():
    comm_response = requests.get(URL, auth=(AUTH["user"], AUTH["password"])).text
    web_response = json.loads(comm_response)

    # Meant to be on a webpage, so building HTML
    page_head = "<html><head><link rel='stylesheet' href='/assets/izzy.css' type='text/css'></head>"

    response = page_head + "<body><ol>"
    top_questions = top_twenty_questions(web_response["list"])
    for question in top_questions:
        response += (
            "\n <li> <b>[" + time_label(timestamp_to_date(question["lastActiveDate"])) + "]</b> " +
            "<a href='" + BASE_URL + str(question["id"]) + "/" + question["slug"] + ".html " + "' target='_blank' >" + question["title"] + "</a>" +
            "<ul>" +
            "<li>Name: " + str(question["author"]["username"]) + "</li>" +
            "<li>View Count: " + str(question["viewCount"]) + "</li>" +
            "<li>Upvote Count: " + str(question["upVoteCount"]) + "</li>" +
            "<li>Answer Count: " + str(question["answerCount"]) + "</li>" +
            "</ul></li>"
        )

    response += "</ol> \n\n This has been your hottest update!</body></html>"
    return response

def top_twenty_questions(question_list):
    chosen_ones = []
    for question in question_list:
        if all([
                younger_than_one_month(question["lastActiveDate"])
        ]):
            chosen_ones.append(question)
            if len(chosen_ones) >= 20:
                break
    return chosen_ones

def time_label(question_time):
    age = datetime.now() - question_time
    return str(age.days) + " days ago"

def younger_than_one_month(timestamp):
    return timestamp_to_date(timestamp) >= (datetime.now() - timedelta(days=30))

def timestamp_to_date(milliseconds):
    return datetime.fromtimestamp(milliseconds/1e3)

class Hottest(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(hottest_month())