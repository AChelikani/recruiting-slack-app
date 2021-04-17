from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
from config.config import Config
from config.samsara_test import SamsaraTest
import utils.greenhouse_utils as ghutils
import utils.slack_utils as slackutils
import utils.utils as utils

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

    def _poll_applications(self, config, last_run_timestamp, gh_client: GreenhouseClient, slack_client: SlackClient):
        # Get all applications with updates since the last run.
        apps = gh_client.get_applications(last_run_timestamp)
        gh_user_id_to_email_map = self._generate_gh_user_id_to_email_map(gh_client)

        for app in apps:
            # Handle a candidate moving into the onsite stage.
            if ghutils.application_is_onsite(app):
                self._handle_new_onsite(config, app, gh_user_id_to_email_map, gh_client, slack_client)

        return

    def _handle_new_onsite(self, config, application, gh_user_id_to_email_map, gh_client: GreenhouseClient, slack_client: SlackClient):
        # Get more information about the candidate.
        candidate = gh_client.get_candidate(application["candidate_id"])
        if candidate is None:
            return None

        # Get more information about scheduled interviews.
        interviews = gh_client.get_scheduled_interviews(application["id"])

        # Get more information about interview kits.
        job_stage_id = application["current_stage"]["id"]
        job_stage = gh_client.get_job_stage(job_stage_id)
        interview_id_to_interview_kit_id = ghutils.get_interview_kits_from_job_stage(job_stage)
        onsite_interview_ids = interview_id_to_interview_kit_id.keys()

        # Create new onsite channel for candidate.
        interview_date = ghutils.get_interview_date_from_scheduled_interviews(interviews)
        channel_name = slackutils.generate_new_onsite_channel_name(candidate["first_name"], candidate["last_name"], interview_date)
        channel_id = slack_client.create_private_channel(channel_name)

        # Invite participants to channel.
        gh_recruiter_ids = ghutils.get_recruiter_and_coordinator_ids(candidate)
        gh_interviwers_ids = ghutils.get_interviewer_ids(interviews, onsite_interview_ids)
        slack_user_ids = []

        for gh_id in ghutils.combine_gh_ids(gh_recruiter_ids, gh_interviwers_ids):
            email = gh_user_id_to_email_map[gh_id]
            slack_id = slack_client.lookup_user_by_email(email)
            if slack_id:
                slack_user_ids.append(slack_id)
        
        slack_client.invite_users_to_channel(channel_id, slack_user_ids)

        # Post introduction message into channel.
        blocks = self._construct_intro_message(config, candidate, interviews, application, interview_id_to_interview_kit_id, onsite_interview_ids)
        slack_client.post_message_to_channel(channel_id, blocks, "Unable to post message")
        return

    def _construct_intro_message(self, config, candidate, interviews, application, interview_id_to_interview_kit_id, onsite_interview_ids):
        resume_url = ""
        for attachment in application["attachments"]:
            if attachment["type"] == "resume":
                resume_url = attachment["url"]

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
                    "text": config.intro_msg + "\n\n Recruiter: *{}*\n Coordinator: *{}*".format(candidate["recruiter"]["name"], candidate["coordinator"]["name"])
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Resume",
                            "emoji": True
                        },
                        "url": resume_url,
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
            if interview["interview"]["id"] not in onsite_interview_ids:
                continue
            if interview["status"] != "scheduled":
                continue

            interviewers = []
            for interviewer in interview["interviewers"]:
                interviewers.append(interviewer["name"])

            interview_name = interview["interview"]["name"]
            start_time = interview["start"]["date_time"]
            _, month, day, _, _ = utils.parse_time(start_time)
            
            interview_kit_id = interview_id_to_interview_kit_id[interview["interview"]["id"]]
            interview_kit_url = ghutils.construct_interview_kit_url(config.greenhouse_url_prefix, interview_kit_id, candidate["id"], application["id"])

            display_time = "{}/{} {}".format(month, day, utils.format_time(start_time))
            display_interviewers = " & ".join(interviewers)
            interview_text = ":{}: {}{} |  {}  |  {}".format(NUMBER_TO_WORD[interview_counter], display_time, " " * (7 - len(display_time)), interview_name, display_interviewers)

            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": interview_text,
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Interview Kit",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": interview_kit_url,
                    "action_id": "button-action-{}".format(interview_counter)
                }
            }

            blocks.append(block)
            interview_counter += 1
            
        blocks.append({
			"type": "divider"
		})
        return blocks

    def run(self, timestamp):
        for config in self.configs:
            greenhouse_client = GreenhouseClient(config.greenhouse_token)
            slack_client = SlackClient(config.slack_token)

            self._poll_applications(config, timestamp, greenhouse_client, slack_client)
