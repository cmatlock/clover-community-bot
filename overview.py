# pylint: disable=missing-docstring

import webapp2
import common

def overview():
    web_response = common.get_results(
        common.QUESTION_JSON_URL + "?" + common.ONLY_UNANSWERED + "&" +
        common.PAGE_SIZE_15 + "&" + common.SORT_HOTTEST
    )

    overview_start = "<div class='container'><h1>Community Overview</h1>"
    overview_end = "</div>"

    questions_section_start = "<div class='card-deck'>"
    questions_section_end = "</div>"

    # Meant to be on a webpage, so building HTML
    response = common.WEB_PAGE_START + overview_start + questions_section_start
    top_questions = top_twenty_questions(web_response["list"])

    for question in top_questions:
        question_card_start = "<div class='card question " + question_status(question) + "'>"
        question_card_end = "</div>"

        response += question_card_start
        response += question_header(question)
        response += question_body(question)
        response += question_footer(question)
        response += question_card_end

    response += questions_section_end + overview_end + common.WEB_PAGE_END

    return response

def question_header(question):
    response = ""

    question_title_start = "<div class='card-header text-truncate'>"
    question_title_end = "</div>"

    response += question_title_start
    response += question["title"]
    response += question_title_end

    return response

def question_body(question):
    response = ""
    question_body_start = "<div class='card-body'>"
    question_body_end = "</div>"

    response += question_body_start
    response += all_users_comments(common.create_question_comments_api(question))
    response += all_users_answers(common.create_question_answers_api(question))
    response += question_body_end

    return response

def question_footer(question):
    response = ""
    question_footer_start = "<div class='card-footer'>"
    question_footer_end = "</div>"

    response += question_footer_start
    response += "<a href='" + common.create_question_url(question) + "' class='btn btn-link btn-block btn-sm' target='_blank'> Here </a>"
    response += question_footer_end
    return response

def question_status(question):

    if question["marked"]:
        return "answered"

    if question["answerCount"] + len(question["commentIds"]) == 0:
        return "untouched"

    # bootstrap already uses 'progress' so...
    return "inprogress"

def all_users_comments(question):
    user_list = "<dt>Commenting Users:</dt>"
    unique_names = []
    comments = common.get_results(question)["list"]
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

def all_users_answers(question):
    user_list = "<dt>Answering Users: </dt>"
    unique_names = []
    answers = common.get_results(question)["list"]
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

def top_twenty_questions(question_list):
    chosen_ones = []
    for question in question_list:
        if all([
                common.younger_than_one_month(question["lastActiveDate"])
        ]):
            chosen_ones.append(question)
            if len(chosen_ones) >= 50:
                break
    return chosen_ones


class Overview(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(overview())
