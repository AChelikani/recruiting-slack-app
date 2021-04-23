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
        # JSON: timezone (string)
        self.timezone = ""

        # Greenhouse API token.
        # JSON: greenhouseToken (string)
        self.greenhouse_token = ""

        # Slack bot API token.
        # JSON: slackToken (string)
        self.slack_token = ""

        # Departments for which the bot is enabled.
        # JSON: departments (array of strings)
        self.departments = []

        # Emails of the slack users to be added to every channel for debugging.
        # JSON: debugEmails (array of strings)
        self.debug_emails = []

        # Whether or not the recruiter should be invited to the channel.
        # JSON: includeRecruiter (boolean)
        self.include_recruiter = True

    def set_name(self, name):
        self.name = name

    def set_greenhouse_silo(self, greenhouse_silo):
        self.greenhouse_silo = greenhouse_silo

    def set_intro_message(self, intro_message):
        self.intro_message = intro_message

    def set_timezone(self, timezone):
        self.timezone = timezone

    def set_greenhouse_token(self, greenhouse_token):
        self.greenhouse_token = greenhouse_token

    def set_slack_token(self, slack_token):
        self.slack_token = slack_token

    def set_departments(self, departments):
        self.departments = departments

    def set_debug_emails(self, debug_emails):
        self.debug_emails = debug_emails

    def set_include_recruiter(self, include_recruiter):
        self.include_recruiter = include_recruiter


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

    if "timezone" in json:
        config.set_timezone(json["timezone"])

    if "greenhouseToken" in json:
        config.set_greenhouse_token(json["greenhouseToken"])

    if "slackToken" in json:
        config.set_slack_token(json["slackToken"])

    if "departments" in json:
        config.set_departments(json["departments"])

    if "debugEmails" in json:
        config.set_debug_emails(json["debugEmails"])

    if "includeRecruiter" in json:
        config.set_include_recruiter(json["includeRecruiter"])

    return config