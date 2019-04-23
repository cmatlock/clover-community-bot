# pylint: disable=missing-docstring

import webapp2

import os
from google.appengine.ext.webapp import template

import common
import communityCrawler

def overview():
    common.USER_OWNED_QUESTIONS = []
    common.CLOVER_OWNED_QUESTIONS = []
    relevant_url = (
        common.QUESTION_JSON_URL + "?" + common.APP_MARKET_SPACE + "&"+ common.ONLY_UNANSWERED +
        "&" + common.PAGE_SIZE_10 + "&" + common.INCLUDED_VALUES
    )
    
    create_start_crawlers(relevant_url)

    user_questions = sorted(common.USER_OWNED_QUESTIONS, key=lambda x_y: x_y.lastActiveDate)
    clover_questions = sorted(common.CLOVER_OWNED_QUESTIONS, key=lambda x_y: x_y.lastActiveDate)

    return [user_questions, clover_questions]

def prepare_cards(questions):
    response = ""
    for question in questions:
        response += question.html_card

    return response

def create_start_crawlers(relevant_url):
    crawler_list = []

    for i in range(5):
        crawler_list.append(communityCrawler.communityCrawler(relevant_url, i))

    for crawler in crawler_list:
        crawler.start()

    for crawler in crawler_list:
        crawler.join()

class Overview(webapp2.RequestHandler):
    def get(self):
        results = overview()
        template_values = {
            "user_questions": results[0],
            "clover_questions": results[1]
        }

        path = os.path.join('templates/overview.html')
        self.response.out.write(template.render(path, template_values))
