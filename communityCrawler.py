import threading
import common

class communityCrawler(threading.Thread):
    def __init__(self, url, num):
        threading.Thread.__init__(self)
        self.name = "Crawler " + str(num)
        self.pageURL = url + "&page=" + str(num + 1)
        self.fetched_questions = []
        self.clover_questions = []
        self.user_questions = []

    def run(self):
        self.fetched_questions = common.get_results(self.pageURL)["list"]

        self.separate_by_last_active_user(self.fetched_questions)

    def separate_by_last_active_user(self, question_list):
        CLOVER_IDs = common.get_clover_ids()

        for question in question_list:
            if question["lastActiveUserId"] in CLOVER_IDs:
                common.add_to_clover_questions(common.QuestionCard(question))
            else:
                common.add_to_user_questions(common.QuestionCard(question))
