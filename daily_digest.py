# pylint: disable=missing-docstring
# pylint: disable=wrong-import-position

import json
import webapp2
import common


def daily_digest():
    web_response = common.get_results(
        common.QUESTION_JSON_URL + "?" + common.PAGE_SIZE_100 +
        "&" + common.SORT_NEWEST + "&" + common.ONLY_UNANSWERED + "&" + common.INCLUDED_VALUES
    )

    response = ""
    top_questions = top_ten_questions(web_response["list"])
    for question in top_questions:
        response += (
            "\n- *[" + common.create_time_label(question["lastActiveDate"]) +
            "]* <" + common.create_question_url(question) + "|" +
            question["title"] + ">"
        )
    return response

def top_ten_questions(question_list):
    sorted_web_response = sorted(question_list, key=lambda x_y: x_y["lastActiveDate"])

    chosen_ones = []
    for question in sorted_web_response:
        if all([
                common.older_than_two_days(question["lastActiveDate"]),
                common.younger_than_one_month(question["lastActiveDate"])
        ]):
            chosen_ones.append(question)
            if len(chosen_ones) >= 10:
                break
    return chosen_ones

class DailyDigest(webapp2.RequestHandler):
    def post(self):
        text = "Here you go!"
        fallback = "Your Daily Digest."
        color = "#2eb886"
        pretext = "Your Daily Digest."
        attachments = [{
            "fallback": fallback,
            "color": color,
            "pretext": pretext,
            "text": daily_digest()
        }]
        slack_response = {
            "text": text,
            "attachments": attachments
        }
        response_object = webapp2.Response(json.dumps(slack_response))
        response_object.content_type = "application/json"

        return response_object

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('GET DailyDigest')
