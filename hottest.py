# pylint: disable=missing-docstring

import json
import requests
import webapp2
import common

def hottest_month():
    comm_response = requests.get(
        (
            common.QUESTION_JSON_URL + "?" + common.PAGE_SIZE_100 +
            "&" + common.SORT_HOTTEST
        ),
        auth=(common.AUTH["user"], common.AUTH["password"])
    ).text
    web_response = json.loads(comm_response)

    # Meant to be on a webpage, so building HTML
    response = common.START_HTML + "<ol>"
    top_questions = top_twenty_questions(web_response["list"])
    for question in top_questions:
        response += (
            "\n <li> <b>[" + common.create_time_label(question["lastActiveDate"]) + "]</b> " +
            "<a href='" + common.create_question_url(question) + "' target='_blank' >" +
            question["title"] + "</a><ul>" +
            "<li>Name: " + str(question["author"]["username"]) + "</li>" +
            "<li>View Count: " + str(question["viewCount"]) + "</li>" +
            "<li>Upvote Count: " + str(question["upVoteCount"]) + "</li>" +
            "<li>Answer Count: " + str(question["answerCount"]) + "</li>" +
            "</ul></li>"
        )

    response += "</ol> \n\n This has been your hottest update!" + common.END_HTML
    return response

def top_twenty_questions(question_list):
    chosen_ones = []
    for question in question_list:
        if all([
                common.younger_than_one_month(question["lastActiveDate"])
        ]):
            chosen_ones.append(question)
            if len(chosen_ones) >= 20:
                break
    return chosen_ones

class Hottest(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(hottest_month())
