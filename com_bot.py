# Following https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

import requests
import os
import time
import re
from slackclient import SlackClient
import json
import schedule
import config
from datetime import datetime
from datetime import timedelta

ANSWERHUB_USER = config.ANSWERHUB_USER
ANSWERHUB_PASS = config.ANSWERHUB_PASS
url = "https://community.clover.com/services/v2/question.json?unanswered=true&pageSize=100&sort=newest&includeOnly=id,slug,title,lastActiveDate"
base_url =  config.BASE_URL

slack_client = SlackClient(config.SLACK_BOT_TOKEN)
ccbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot command is found, this function returns a tuple of command and channel.
    If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
    Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    if command.startswith("newest"):
        response = daily_digest()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def check_for_command():
    command, channel = parse_bot_commands(slack_client.rtm_read())
    if command:
        handle_command(command, channel)


def daily_digest():
    web_response = json.loads(requests.get(url, auth=(ANSWERHUB_USER, ANSWERHUB_PASS)).text)
    response = "Daily Question List: "
    top_questions = top_ten_questions(web_response["list"])
    for question in top_questions:
        response += ("\n   • *[" + time_label(datetime.fromtimestamp(question["lastActiveDate"]/1e3)) + "]* <" + base_url + str(question["id"]) + "/" + question["slug"] + ".html|" + question["title"] + ">")

    return response

def top_ten_questions(question_list):
    sorted_web_response = sorted(question_list, key=lambda x_y: x_y["lastActiveDate"])

    chosen_ones = []
    for question in sorted_web_response:
        if all([older_than_two_days(question), younger_than_one_month(question)]):
            chosen_ones.append(question)
            if len(chosen_ones) == 10:
                break
    return chosen_ones

def time_label(question_time):
    age = datetime.now() - question_time
    return (str(age.days) + " days ago")

### Requirements for top questions

def older_than_two_days(question):
    return (datetime.fromtimestamp(question["lastActiveDate"]/1e3)) <= (datetime.now() - timedelta(days=2))

def younger_than_one_month(question):
    return (datetime.fromtimestamp(question["lastActiveDate"]/1e3)) >= (datetime.now() - timedelta(days=30))



if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        # Set the schedules
        schedule.every(1).second.do(check_for_command)
        schedule.every().day.at("8:30").do(daily_digest)
        while True:
            schedule.run_pending()
    else:
        print("Connection failed. Exception traceback printed above.")