from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
from config.config import Config
from config.samsara_test import SamsaraTest
import utils.greenhouse_utils as ghutils
import utils.slack_utils as slackutils

NUMBER_TO_WORD = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
}

class ApplicationWatcher():
    '''
    The ApplicationWatcher runs periodically to determine if any candidates' applications
    have changed job stages.

    Candidate moved to onsite stage
    - Create a private onsite channel for the candidate.
    - Invite the recruiter and coordinator to the channel.
    - If the candidates interviews have been assigned, invite interviewers to channel.
    - Post a message with candidate details.

    Candidate received an offer
    - Rename the channel from onsite-... to offer-...
    - Post message into channel.
    - Post candidates email and encourage interviewers to send a note.


    Candidate accepts offer, declines offer, or is rejected after onsite
    - Send final message.
    - Archive channel.
    '''
    def __init__(self, configs):
        self.configs = configs

    def _generate_gh_user_id_to_email_map(self, gh_client: GreenhouseClient):
        user_id_to_email = {}
        users = gh_client.get_users()

        for user in users:
            user_id_to_email[user["id"]] = user["primary_email_address"]

        return user_id_to_email

    def _poll_applications(self, last_run_timestamp, gh_client: GreenhouseClient, slack_client: SlackClient):
        # Get all applications with updates since the last run.
        apps = gh_client.get_applications(last_run_timestamp)
        gh_user_id_to_email_map = self._generate_gh_user_id_to_email_map(gh_client)

        for app in apps:
            # Handle a candidate moving into the onsite stage.
            if ghutils.application_is_onsite(app):
                self._handle_new_onsite(app, gh_user_id_to_email_map, gh_client, slack_client)

        return

    def _handle_new_onsite(self, application, gh_user_id_to_email_map, gh_client: GreenhouseClient, slack_client: SlackClient):
        # Get more information about the candidate.
        candidate = gh_client.get_candidate(application["candidate_id"])
        if candidate is None:
            return None

        # Get more information about scheduled interviews.
        interviews = gh_client.get_scheduled_interviews(application["id"])

        # Create new onsite channel for candidate.
        channel_name = slackutils.generate_new_onsite_channel_name(candidate["first_name"], candidate["last_name"])
        channel_id = slack_client.create_private_channel(channel_name)

        # Invite participants to channel.
        gh_recruiter_ids = ghutils.get_recruiter_and_coordinator_ids(candidate)
        gh_interviwers_ids = ghutils.get_interviewer_ids(interviews)
        slack_user_ids = []

        for gh_id in ghutils.combine_gh_ids(gh_recruiter_ids, gh_interviwers_ids):
            email = gh_user_id_to_email_map[gh_id]
            print(email)
            slack_id = slack_client.lookup_user_by_email(email)
            if slack_id:
                slack_user_ids.append(slack_id)
        
        slack_client.invite_users_to_channel(channel_id, slack_user_ids)

        # Post introduction message into channel.
        blocks = self._construct_intro_message(candidate, interviews)
        slack_client.post_message_to_channel(channel_id, blocks, "Unable to post message")
        return

    def _construct_intro_message(self, candidate, interviews):
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Interview for {} {}".format(candidate["first_name"], candidate["last_name"]),
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":wave: Thank you for helping to make Samsara a better place to work.\n\n Candidate: *{} {}*".format(candidate["first_name"], candidate["last_name"])
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Greenhouse Profile",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "actionId-0"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Resume",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "actionId-1"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        interview_counter = 1
        for interview in interviews:
            # TODO: Verify interview is part of onsite job stage.
            if interview["status"] != "scheduled":
                continue

            interviewers = []
            for interviewer in interview["interviewers"]:
                interviewers.append(interviewer["name"])

            interview_name = interview["interview"]["name"]

            start_time = interview["start"]["date_time"]

            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":{}: {} | {} | {}".format(NUMBER_TO_WORD[interview_counter], interview_name, " & ".join(interviewers), start_time)
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "See question",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "action_id": "button-action-{}".format(interview_counter)
                }
            }

            blocks.append(block)
            interview_counter += 1
            
        blocks.append({
			"type": "divider"
		})
        
        print(blocks)
        return blocks

    def run(self, timestamp):
        for config in self.configs:
            greenhouse_client = GreenhouseClient(config.greenhouse_token)
            slack_client = SlackClient(config.slack_token)

            self._poll_applications(timestamp, greenhouse_client, slack_client)



if __name__ == "__main__":
    config = [SamsaraTest]
    ap = ApplicationWatcher(config)
    ap.run("2021-03-11T00:00:00.000Z")
        