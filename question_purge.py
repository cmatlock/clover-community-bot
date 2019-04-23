# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import pprint
from progress.bar import ShadyBar
import threading
import common

pp = pprint.PrettyPrinter(indent=4)

def create_sniffer(num):
    t = threading.Thread(name=("sniffer"+num), target=start_sniffer, args=(num,))
    sniffer_list.append(t)

def start_sniffer(num):
    questions = []

    if num == 1:
        questions = answerhub_response["list"]

    questions = get_page_of_questions(num)

    which_to_delete(questions)

def get_page_of_questions(num):
    return common.get_results(base_url + "&page=" + num)["list"]

def which_to_delete(page_question_list):
    for question in page_question_list:
        if (
            (common.timestamp_to_date(question["lastActiveDate"]).year <= 2018)
        ):
            with array_lock:
                ignored_questions.append(common.QuestionCard(question))

def delete_each_question():
    in_progress = True
    for question in ignored_questions:
        question.display_question()
        while in_progress:
            response = raw_input('Delete? y/n/answers/cancel: ').lower()

            if response == 'y':
                result = common.put_results(question_url['delete_url'])
                print 'Question deletion: {0}'.format(result)
                break
            elif response == 'n':
                print 'Question preserved'
                break
            elif response == 'answers':
                question.display_answers()
            elif response == 'cancel':
                print 'Operation cancelled. See ya later!'
                in_progress = False
                return False
            else:
                print 'Invalid response.'

        if in_progress == false:
            break

    return False

def delete_all_questions():
    for question in ShadyBar('Delete Progress').iter(ignored_questions):
        common.put_results(question['delete_url'])

def close_all_questions():
    for question in ignored_questions:
        print question.browser_url
        common.put_results(question.close_url)

array_lock = threading.Lock()
ignored_questions = []
base_url = "https://community.clover.com/services/v2/question.json?pageSize=50"

sniffer_list = []

def begin_purge():
    answerhub_response = common.get_results(base_url)
    page_count = answerhub_response["pageCount"]

    for i in range(page_count):
        create_sniffer(str(i))

    print '{0} pages found, so {1} sniffer(s) popped into existence.'.format(page_count, len(sniffer_list))

    for sniffer in sniffer_list:
        sniffer.start()

    print 'It begins...'

    for sniffer in sniffer_list:
        sniffer.join()

    print 'There are {0} questions found to be deleted.'.format(len(ignored_questions))

    running = True
    while running:
        response = raw_input('Delete or Close?: ').lower()
        if response == 'delete':
            response = raw_input('Continue to delete? y/n/all: ').lower()
            if response == 'y':
                print 'Begin deleting questions....'
                running = delete_each_question()
            elif response == 'n':
                print 'No questions deleted. Exiting...'
                running = False
            elif response == 'all':
                print 'Are you sure? This will delete all {0} questions in one go.'.format(len(ignored_questions))
                response = raw_input('Are you sure you\'re really sure??? y/n: ').lower()
                if response == 'y':
                    print 'Deleting all questions...'
                    running = delete_all_questions()
                else:
                    print 'Operation aborted. No questions deleted.'
                    running = False
        if response == 'close':
            running = close_all_questions()
        else:
            print 'Invalid response'

    print "Script completed!"

begin_purge()
