# pylint: disable=missing-docstring

import webapp2

import common
import communityCrawler

def overview():
    relevant_url = (
        common.QUESTION_JSON_URL + "?" + common.APP_MARKET_SPACE + "&"+ common.ONLY_UNANSWERED +
        "&" + common.PAGE_SIZE_1 + "&" + common.INCLUDED_VALUES
    )
    
    create_start_crawlers(relevant_url)

    overview_start = "<div class='container'><h1>App Market Community Overview</h1>"
    overview_end = "</div>"

    legend = (
        "<p>"
            "<button class='btn btn-sm answered' type='button' data-toggle='collapse' data-target='#answered' aria-expanded='false' aria-controls='answered'>"
                "Answered"
            "</button> "
            "<button class='btn btn-sm inprogress' type='button' data-toggle='collapse' data-target='#inprogress' aria-expanded='false' aria-controls='inprogress'>"
                "In Progress"
            "</button> "
            "<button class='btn btn-sm untouched' type='button' data-toggle='collapse' data-target='#untouched' aria-expanded='false' aria-controls='untouched'>"
                "Untouched"
            "</button> "
        "</p>"
        "<div class='collapse' id='answered'>"
            "<div class='card card-body question answered'>"
                "This indicates that an answer has been provided an accepted. Currently, answered questions will never show up on this page."
            "</div>"
        "</div>"
        "<div class='collapse' id='inprogress'>"
            "<div class='card card-body question inprogress'>"
                "This indicates that someone has commented or answered the question, but there is no accepted answer yet. This could be due to a follow up question being asked. Usually this also means that someone is taking care of the question."
            "</div>"
        "</div>"
        "<div class='collapse' id='untouched'>"
            "<div class='card card-body question untouched'>"
                "This indicates that the question has no comments or answers. It craves attention."
            "</div>"
        "</div>"
        "<br>"
    )

    # Meant to be on a webpage, so building HTML
    response = common.WEB_PAGE_START + overview_start + legend

    response += "<h2>Last Response From Users</h2>" + "<div class='card-deck'>"
    response += prepare_cards(sorted(common.USER_OWNED_QUESTIONS, key=lambda x_y: x_y.lastActiveDate)) + "</div>"

    response += "<h2>Last Response From Clover</h2>" + "<div class='card-deck'>"
    response += prepare_cards(sorted(common.CLOVER_OWNED_QUESTIONS, key=lambda x_y: x_y.lastActiveDate)) + "</div>"

    response += overview_end + common.WEB_PAGE_END

    return response

def populate_card_deck():
    # start the deck of cards section
    response = "<div class='card-deck'>"

    return response + "</div>"

def prepare_cards(questions):
    response = ""
    for question in questions:
        response += question.html_card

    return response

def create_start_crawlers(relevant_url):
    crawler_list = []

    for i in range(10):
        crawler_list.append(communityCrawler.communityCrawler(relevant_url, i))

    for crawler in crawler_list:
        crawler.start()

    for crawler in crawler_list:
        crawler.join()

class Overview(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(overview())
