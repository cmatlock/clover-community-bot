# pylint: disable=missing-docstring

import webapp2
import common

def overview():

    web_response = common.get_results(
        common.QUESTION_JSON_URL + "?" + common.PAGE_SIZE_5 + "&" + common.SORT_HOTTEST
    )

    BODY_START = "<body>"
    BODY_END = "</body>"

    PAGE_DIV_START = "<div class='grid-frame grid-padding-x'>"
    PAGE_DIV_END = "</div>"

    GRID_HEADER = "<div class='cell shrink header'><h1>Header Here</h1></div>"
    GRID_FOOTER = "<div class='cell shrink footer'><h3>Hitlist returned!</h3></div>"

    QUESTIONS_SECTION_START = "<div class='cell'><div class='grid-x grid-padding-x'>"
    QUESTIONS_SECTION_END = "</div></div>"

    QUESTION_START = "<div class='cell small-4'><div class='card question small-cell-block-y'>"
    QUESTION_END = "</div></div>"
    # Meant to be on a webpage, so building HTML
    response = common.PAGE_HEADER + BODY_START + PAGE_DIV_START + GRID_HEADER + QUESTIONS_SECTION_START
    top_questions = top_twenty_questions(web_response["list"])

    for question in top_questions:
        response += QUESTION_START
        response += question["title"] + "<br>"
        response += all_users_comments(common.create_question_comments_api(question))
        response += all_users_answers(common.create_question_answers_api(question))
        response += QUESTION_END

    response += QUESTIONS_SECTION_END + GRID_FOOTER + PAGE_DIV_END + BODY_END + common.END_HTML
    return response

def all_users_comments(question):
    user_list = "Commenting Users: <ul>"
    unique_names = []
    comments = common.get_results(question)["list"]
    for comment in comments:
        name = comment["author"]["username"]
        if name not in unique_names:
            unique_names.append(name)
            user_list += (
                "<li>Name: " + str(name) + "</li>"
            )

    if not unique_names:
        user_list += "No one has commented..."

    return user_list + "</ul>"

def all_users_answers(question):
    user_list = "Answering Users: <ul>"
    unique_names = []
    answers = common.get_results(question)["list"]
    for answer in answers:
        name = answer["author"]["username"]
        if name not in unique_names:
            unique_names.append(name)
            user_list += (
                "<li>Name: " + str(name) + "</li>"
            )

    if not unique_names:
        user_list += "No one has answered..."

    return user_list + "</ul>"

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


class Overview(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(overview())
