# pylint: disable=missing-docstring

import webapp2
import threading
import common

array_lock = threading.Lock()
CLOVER_IDs = []

def overview():
    CLOVER_IDs = CLOVER_IDs or get_clover_ids

    relevant_url = (
        common.QUESTION_JSON_URL + "?" + common.APP_MARKET_SPACE + "&"+ common.ONLY_UNANSWERED +
        "&" + common.PAGE_SIZE_10 + "&" + common.INCLUDED_VALUES
    )

    # question_list = common.get_results(
    #     common.QUESTION_JSON_URL + "?" + common.APP_MARKET_SPACE + "&"+ common.ONLY_UNANSWERED +
    #     "&" + common.PAGE_SIZE_100 + "&" + common.INCLUDED_VALUES
    # )["list"]
    
    question_list = release_the_sniffers(relevant_url)

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

    clover_questions, user_questions = separate_by_last_active_user(question_list, clover_ids)

    response += "<h2>Last Response From Users</h2>"
    response += populate_cards(sorted(user_questions, key=lambda x_y: x_y["lastActiveDate"]))

    response += "<h2>Last Response From Clover</h2>"
    response += populate_cards(sorted(clover_questions, key=lambda x_y: x_y["lastActiveDate"]))

    response += overview_end + common.WEB_PAGE_END

    return response

def get_clover_ids():
    clover_users = common.get_results(common.CLOVER_USERS_URL)["list"]
    ids = []

    for user in clover_users:
        ids.append(user.get("id"))
    return ids

def question_header(question, status):
    response = ""

    question_title_start = "<div class='card-header font-weight-bold text-truncate bg-" + status + "'>"
    question_title_end = "</div>"

    response += question_title_start
    response += question["title"]
    response += question_title_end

    return response

def question_body(question):
    response = "<div class='card-body bg-transparent'>"

    response += all_users_comments(common.create_question_comments_api(question))
    response += all_users_answers(common.create_question_answers_api(question))

    return response + "</div>"

def question_footer(question, status):
    response = ""

    question_footer_start = "<div class='card-footer font-italic border-" + status + "'>"
    question_footer_end = "</div>"

    response += question_footer_start
    response += "<div class='float-left'>" + common.create_time_label(question["lastActiveDate"]) + "</div>"
    response += "<a href='" + common.create_question_url(question) + "' class='btn btn-sm btn-dark float-right' target='_blank'> View </a>"
    response += question_footer_end

    return response

def question_status(question):
    # returns Bootstrap keyword for color/formatting

    if question["marked"]:
        return "success"

    # Not an accurate representation; find a better indicator
    if (len(question["childrenIds"])) == 0:
        return "danger"

    return "warning"

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

def separate_by_last_active_user(question_list, id_list):
    clovers_questions = []
    users_questions = []

    for question in question_list:
        if question["lastActiveUserId"] in id_list:
            clovers_questions.append(question)
        else:
            users_questions.append(question)

    return clovers_questions, users_questions

def populate_card_deck():
    # start the deck of cards section
    response = "<div class='card-deck'>"

    return response + "</div>"

def prepare_cards(questions):
    
    
    for question in questions:
        status = question_status(question)

        question_card_start = "<div class='card question border-" + status + "'>"
        question_card_end = "</div>"

        response += question_card_start
        response += question_header(question, status)
        response += question_body(question)
        response += question_footer(question, status)
        response += question_card_end

def create_sniffer(num, base_url):
    t = threading.Thread(name=("sniffer"+num), target=start_sniffers, args=(num, base_url))
    return t

def start_sniffers(num, base_url):
    print ">>>sniffer " + num + " started "
    questions = []

    if int(num) > 1:
        questions = common.get_page_of_questions(num, base_url)

    clover_questions, user_questions = separate_by_last_active_user(questions, CLOVER_IDs)
    

    for question in questions:
        with array_lock:
            RETURNED_QUESTIONS.append(question)

    print "<<sniffer " + num + " completed"

def release_the_sniffers(relevant_url):
    sniffer_list = []

    web_response = common.get_results(relevant_url)

    page_count = web_response["pageCount"]

    if int(page_count) > 10:
        page_count = 10

    RETURNED_QUESTIONS.extend(web_response["list"])

    for i in range(page_count):
        sniffer_list.append(create_sniffer(str(i+1), relevant_url))

    print 'So, {0} pages found, so {1} sniffer(s) popped into existence.'.format(page_count, len(sniffer_list))
    print 'No threads started yet.'

    for sniffer in sniffer_list:
        sniffer.start()

    for sniffer in sniffer_list:
        sniffer.join()

    print " final question length: " + str(len(RETURNED_QUESTIONS))
    return RETURNED_QUESTIONS

class Overview(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(overview())
