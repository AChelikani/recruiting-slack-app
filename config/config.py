import os


class Config:
    def __init__(self):
        # Name of the organization.
        # JSON: name
        self.name = ""

        # Silo the greenhouse data is, ex. app2.
        # This is also the prefix of the organizations greenhouse URLs.
        # JSON: greenhouseSilo (string)
        self.greenhouse_silo = ""

        # Organization specific introduction message that is used as part
        # of the larger first slack message.
        # JSON: introMessage (string)
        self.intro_message = ""

        # Timezone the organization schedules interviews in.
        # Should be a valid pytz timezone, ex. "US/Pacific".
        # JSON: defaultTimezone (string)
        self.default_timezone = ""

        # Greenhouse API token.
        # JSON: greenhouseToken (string)
        self.greenhouse_token = ""

        # Slack bot API token.
        # JSON: slackToken (string)
        self.slack_token = ""

        # Slack bot admin API token.
        # JSON: adminSlackToken (string)
        self.admin_slack_token = ""

        # Departments for which the bot is enabled.
        # JSON: departments (array of strings)
        self.departments = []

        # Offices for which the bot is enabled.
        # JSON: offices (array of strings)
        self.offices = []

        # Emails of the slack users to be added to every channel for debugging.
        # JSON: debugEmails (array of strings)
        self.debug_emails = []

        # Whether or not the recruiter should be invited to the channel.
        # JSON: includeRecruiter (boolean)
        self.include_recruiter = True

        # Job title substrings that should be excluded.
        # JSON: excludeJobs (array of string)
        self.exclude_jobs = []

        # Job title substrings that should be included, regardless if they are in exclude_jobs.
        # JSON: includeJobs (array of string)
        self.include_jobs = []

        # Minimum number of interviews in an onsite to create a channel.
        # JSON: minInterviewsForChannel (number)
        self.min_interviews_for_channel = 1

        # Workspace IDs for org-wide installed apps in Enterprise Grid. First ID is the workspace in which the channel is originally created.
        # JSON: workspaceIds (array of string)
        self.workspace_ids = []

    def set_name(self, name):
        self.name = name

    def set_greenhouse_silo(self, greenhouse_silo):
        self.greenhouse_silo = greenhouse_silo

    def set_intro_message(self, intro_message):
        self.intro_message = intro_message

    def set_default_timezone(self, default_timezone):
        self.default_timezone = default_timezone

    def set_greenhouse_token(self, greenhouse_token):
        self.greenhouse_token = greenhouse_token

    def set_slack_token(self, slack_token):
        self.slack_token = slack_token

    def set_admin_slack_token(self, admin_slack_token):
        self.admin_slack_token = admin_slack_token

    def set_departments(self, departments):
        self.departments = departments

    def set_offices(self, offices):
        self.offices = offices

    def set_debug_emails(self, debug_emails):
        self.debug_emails = debug_emails

    def set_include_recruiter(self, include_recruiter):
        self.include_recruiter = include_recruiter

    def set_exclude_jobs(self, exclude_jobs):
        self.exclude_jobs = exclude_jobs

    def set_include_jobs(self, include_jobs):
        self.include_jobs = include_jobs

    def set_min_interviews_for_channel(self, min_interviews_for_channel):
        self.min_interviews_for_channel = min_interviews_for_channel

    def set_workspace_ids(self, workspace_ids):
        self.workspace_ids = workspace_ids


def parse_config(json):
    """
    Parse a config from a loaded JSON into a Config object.
    """
    config = Config()
    if "name" in json:
        config.set_name(json["name"])

    if "greenhouseSilo" in json:
        config.set_greenhouse_silo(json["greenhouseSilo"])

    if "introMessage" in json:
        config.set_intro_message(json["introMessage"])

    if "defaultTimezone" in json:
        config.set_default_timezone(json["defaultTimezone"])

    if "greenhouseToken" in json:
        # NOTE: Value in config JSON is env variable key.
        config.set_greenhouse_token(os.environ[json["greenhouseToken"]])

    if "slackToken" in json:
        # NOTE: Value in config JSON is env variable key.
        config.set_slack_token(os.environ[json["slackToken"]])

    if "adminSlackToken" in json:
        # NOTE: Value in config JSON is env variable key.
        config.set_admin_slack_token(os.environ[json["adminSlackToken"]])

    if "departments" in json:
        config.set_departments(json["departments"])

    if "offices" in json:
        config.set_offices(json["offices"])

    if "debugEmails" in json:
        config.set_debug_emails(json["debugEmails"])

    if "includeRecruiter" in json:
        config.set_include_recruiter(json["includeRecruiter"])

    if "excludeJobs" in json:
        config.set_exclude_jobs(json["excludeJobs"])

    if "includeJobs" in json:
        config.set_include_jobs(json["includeJobs"])

    if "minInterviewsForChannel" in json:
        config.set_min_interviews_for_channel(json["minInterviewsForChannel"])

    if "workspaceIds" in json:
        config.set_workspace_ids(json["workspaceIds"])

    return config
