from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
import utils.greenhouse_utils as ghutils
import utils.slack_utils as slackutils
import utils.utils as utils
import time

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
        """
        Generate a map of Greenhouse user IDs to their emails.
        """
        user_id_to_email = {}
        users = self.gh_client.get_users()

        for user in users:
            user_id_to_email[user["id"]] = user["primary_email_address"]

        return user_id_to_email

    def _poll_applications(self, timestamp):
        # Get IDs of enabled departments.
        department_ids = []
        departments = self.gh_client.get_departments()
        if self.config.departments:
            department_ids = ghutils.get_department_ids_from_names(
                self.config.departments, departments
            )
        else:
            for department in departments:
                department_ids.append(department["id"])

        print("Department IDs: {}".format(department_ids))

        # Get all open jobs from enabled departments.
        job_id_to_job = {}
        if department_ids:
            for id in department_ids:
                jobs = self.gh_client.get_jobs(department_id=id)
                print("Fetched {} jobs for department {}".format(len(jobs), id))
                for job in jobs:
                    if ghutils.is_job_excluded(job, self.config.exclude_jobs):
                        continue
                    job_id_to_job[job["id"]] = job

        # Get all applications for open jobs with updates in last month.
        apps = []
        for job_id in job_id_to_job:
            apps_for_job = self.gh_client.get_applications_by_job(timestamp, job_id)
            print(
                "Fetched {} applications for job {}".format(len(apps_for_job), job_id)
            )

            # Filter applications to those who are not prospects.
            apps.extend(ghutils.filter_applications(apps_for_job))

        print("Total active candidate applications to analyze: {}".format(len(apps)))

        gh_user_id_to_email_map = self._generate_gh_user_id_to_email_map()

        # Filter applications to those in onsite stage.
        apps = ghutils.get_onsite_applications(apps)
        print("Total apps in onsite stage: {}\n".format(len(apps)))

        job_stage_id_to_job_stage_map = {}
        for app in apps:
            print("Application processing... ID: {}\n".format(app["id"]))

            # Get more information about scheduled interviews.
            interviews = self.gh_client.get_scheduled_interviews(app["id"])

            # Load the job information.
            job_id, _ = ghutils.get_job_id_and_name_from_application(app)
            job = job_id_to_job[job_id]

            # Get more information about interview kits.
            job_stage_id = app["current_stage"]["id"]
            if job_stage_id not in job_stage_id_to_job_stage_map:
                job_stage_id_to_job_stage_map[
                    job_stage_id
                ] = self.gh_client.get_job_stage(job_stage_id)
            job_stage = job_stage_id_to_job_stage_map[job_stage_id]

            if ghutils.onsite_is_tomorrow(job_stage, interviews, timestamp):
                self._handle_new_onsite(
                    app,
                    interviews,
                    job_stage,
                    job,
                    gh_user_id_to_email_map,
                )

            else:
                print("No onsite tomorrow.")

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
            print("Couldn't fetch candidate...")
            return None

        print(
            "Onsite tomorrow ... Candidate: {} {}".format(
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
        print("Channel created... Channel Name: {}".format(channel_name))

        # Invite: recruiter, recruiting coordinator, interviewers, and hiring managers.
        gh_recruiters = []
        if self.config.include_recruiter:
            recruiter = ghutils.get_recruiter(candidate)
            if recruiter is not None:
                gh_recruiters.append(recruiter)
        coordinator = ghutils.get_coordinator(candidate)
        if coordinator is not None:
            gh_recruiters.append(coordinator)

        gh_interviwers = ghutils.get_interviewers(interviews, onsite_interview_ids)
        gh_hiring_managers = ghutils.dedup_hiring_managers(
            gh_interviwers, ghutils.get_hiring_managers_from_job(job)
        )
        panel = gh_recruiters + gh_interviwers + gh_hiring_managers
        panel = ghutils.panel_with_emails(panel, gh_user_id_to_email_map)

        panel.extend(
            [{"email": email, "name": "DEBUG"} for email in self.config.debug_emails]
        )

        slack_user_ids = []
        persons_not_found = []
        for person in panel:
            email = person["email"]
            slack_id = self.slack_client.lookup_user_by_email(email)
            if slack_id:
                slack_user_ids.append(slack_id)
            else:
                # User has no associated slack account.
                persons_not_found.append(person)

        self.slack_client.invite_users_to_channel(channel_id, slack_user_ids)
        print("Panel invited... Members: {}".format([p["name"] for p in panel]))

        # Post invite missing persons into channel message.
        if persons_not_found:
            blocks = self._construct_missing_persons_message(persons_not_found)
            self.slack_client.post_message_to_channel(
                channel_id, blocks, "Unable to invite some users."
            )

        # Post introduction message into channel.
        blocks = self._construct_intro_message(
            candidate,
            interviews,
            application,
            job,
            interview_id_to_interview_kit_id,
            onsite_interview_ids,
            gh_hiring_managers,
        )

        self.slack_client.post_message_to_channel(
            channel_id, blocks, "Unable to post schedule message."
        )
        print("Schedule posted...")
        print("\n")
        return

    def _construct_missing_persons_message(self, persons_not_found):
        names = [p["name"] for p in persons_not_found]
        msg = "Please invite {} to channel manually.".format(", ".join(names))
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": msg,
                },
            }
        ]
        return blocks

    def _construct_intro_message(
        self,
        candidate,
        interviews,
        application,
        job,
        interview_id_to_interview_kit_id,
        onsite_interview_ids,
        hiring_managers,
    ):

        candidate_contact = ghutils.get_candidate_contact(candidate)

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

        linkedin_url = ghutils.get_candidate_linkedin(candidate, application)

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
                        candidate["first_name"].capitalize(),
                        candidate["last_name"].capitalize(),
                        job["name"],
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
                        "text": "Note: All times below are in *{}*.".format(
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
