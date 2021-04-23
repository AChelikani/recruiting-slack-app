from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
import utils.greenhouse_utils as ghutils
import utils.slack_utils as slackutils
import utils.utils as utils

# NOTE: Slack only has default emojis of the form :number: for the first nine numbers.
NUMBER_TO_WORD = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}


class ApplicationWatcher:
    """
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
    """

    def __init__(self, config):
        self.config = config
        self.gh_client = GreenhouseClient(config.greenhouse_token)
        self.slack_client = SlackClient(config.slack_token)

    def _generate_gh_user_id_to_email_map(self):
        user_id_to_email = {}
        users = self.gh_client.get_users()

        for user in users:
            user_id_to_email[user["id"]] = user["primary_email_address"]

        return user_id_to_email

    def _poll_applications(self, timestamp):
        # Get all applications with updates since the last run.
        apps = self.gh_client.get_applications(timestamp)
        gh_user_id_to_email_map = self._generate_gh_user_id_to_email_map()

        jobs = self.gh_client.get_jobs()

        for app in apps:
            print("Processing ... Application ID: {}".format(app["id"]))

            # Discard applications that are for prospects, ie. not associated with a job.
            if app["prospect"]:
                continue

            # Verify application is in one of the enabled departments.
            job_id, _ = ghutils.get_job_id_and_name_from_application(app)
            job = [job for job in jobs if job["id"] == job_id][0]

            if self.config.departments:
                department = ghutils.get_department_name_from_job(job)
                if department not in self.config.departments:
                    continue

            # Handle a candidate moving into the onsite stage.
            if ghutils.application_is_onsite(app):
                # Get more information about scheduled interviews.
                interviews = self.gh_client.get_scheduled_interviews(app["id"])

                # Get more information about interview kits.
                job_stage_id = app["current_stage"]["id"]
                job_stage = self.gh_client.get_job_stage(job_stage_id)

                if ghutils.onsite_is_tomorrow(job_stage, interviews, timestamp):
                    self._handle_new_onsite(
                        app,
                        interviews,
                        job_stage,
                        job,
                        gh_user_id_to_email_map,
                    )

        return

    def _handle_new_onsite(
        self,
        application,
        interviews,
        job_stage,
        job,
        gh_user_id_to_email_map,
    ):
        # Get more information about the candidate.
        candidate = self.gh_client.get_candidate(application["candidate_id"])
        if candidate is None:
            return None

        print(
            "Processing: {} {} with onsite tomorrow...\n".format(
                candidate["first_name"], candidate["last_name"]
            )
        )

        interview_id_to_interview_kit_id = ghutils.get_interview_kits_from_job_stage(
            job_stage
        )
        onsite_interview_ids = interview_id_to_interview_kit_id.keys()

        # Create new onsite channel for candidate.
        interview_date = (
            ghutils.get_first_onsite_interview_date_from_scheduled_interviews(
                job_stage, interviews, self.config.timezone
            )
        )
        channel_name = slackutils.generate_new_onsite_channel_name(
            candidate["first_name"], candidate["last_name"], interview_date
        )
        channel_id = self.slack_client.create_private_channel(channel_name)

        # Invite: recruiter, recruiting coordinator, interviewers, and hiring managers.
        gh_recruiter_ids = []
        if self.config.include_recruiter:
            recruiter_id = ghutils.get_recruiter_id(candidate)
            if recruiter_id is not None:
                gh_recruiter_ids.append(recruiter_id)
        coordinator_id = ghutils.get_coordinator_id(candidate)
        if coordinator_id is not None:
            gh_recruiter_ids.append(coordinator_id)

        gh_interviwers_ids = ghutils.get_interviewer_ids(
            interviews, onsite_interview_ids
        )

        hiring_managers = ghutils.get_hiring_managers_from_job(job)

        slack_user_ids = []

        emails = [
            gh_user_id_to_email_map[gh_id]
            for gh_id in ghutils.combine_gh_ids(
                gh_recruiter_ids, gh_interviwers_ids, [m["id"] for m in hiring_managers]
            )
        ]
        emails.extend(self.config.debug_slack_emails)

        for email in emails:
            slack_id = self.slack_client.lookup_user_by_email(email)
            if slack_id:
                slack_user_ids.append(slack_id)

        self.slack_client.invite_users_to_channel(channel_id, slack_user_ids)

        # Post introduction message into channel.
        blocks = self._construct_intro_message(
            candidate,
            interviews,
            application,
            job,
            interview_id_to_interview_kit_id,
            onsite_interview_ids,
        )

        self.slack_client.post_message_to_channel(
            channel_id, blocks, "Unable to post message"
        )
        return

    def _construct_intro_message(
        self,
        candidate,
        interviews,
        application,
        job,
        interview_id_to_interview_kit_id,
        onsite_interview_ids,
    ):

        candidate_contact = ghutils.get_candidate_contact(candidate)

        hiring_managers = ghutils.get_hiring_managers_from_job(job)

        # Populate buttons.
        action_elements = []

        resume_url = ghutils.get_application_resume(application)

        if resume_url:
            action_elements.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Resume", "emoji": True},
                    "url": resume_url,
                    "value": "click_me_1",
                    "action_id": "actionId-1",
                }
            )

        linkedin_url = ghutils.get_candidate_linkedin(candidate)

        if linkedin_url:
            action_elements.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "LinkedIn", "emoji": True},
                    "url": linkedin_url,
                    "value": "click_me_2",
                    "action_id": "actionId-2",
                }
            )

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Interview {} {} for {}".format(
                        candidate["first_name"], candidate["last_name"], job["name"]
                    ),
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": self.config.intro_message
                    + "\n\n Recruiter: *{}*\n Coordinator: *{}*\n Hiring Manager: *{}*\n\n Candidate contact: {}".format(
                        candidate["recruiter"]["name"],
                        candidate["coordinator"]["name"],
                        " & ".join([m["name"] for m in hiring_managers]),
                        candidate_contact,
                    ),
                },
            },
            {
                "type": "actions",
                "elements": action_elements,
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Note: All times below are in *{}*".format(
                            self.config.timezone
                        ),
                    }
                ],
            },
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
            end_time = interview["end"]["date_time"]
            _, month, day, _, _ = utils.parse_time(start_time, self.config.timezone)

            interview_kit_id = interview_id_to_interview_kit_id[
                interview["interview"]["id"]
            ]
            interview_kit_url = ghutils.construct_interview_kit_url(
                self.config.greenhouse_silo,
                interview_kit_id,
                candidate["id"],
                application["id"],
            )

            display_time = "{}/{} {}-{}".format(
                month,
                day,
                utils.format_time(start_time, self.config.timezone),
                utils.format_time(end_time, self.config.timezone),
            )
            display_interviewers = " & ".join(interviewers)
            interview_text = ":{}: {}{} |  {}  |  {}".format(
                NUMBER_TO_WORD[interview_counter],
                display_time,
                " " * (7 - len(display_time)),
                interview_name,
                display_interviewers,
            )

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
                    "action_id": "button-action-{}".format(interview_counter),
                },
            }

            blocks.append(block)
            interview_counter += 1

        blocks.append({"type": "divider"})
        return blocks

    def run(self, timestamp):
        self._poll_applications(timestamp)
