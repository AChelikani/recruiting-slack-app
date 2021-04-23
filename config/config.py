class Config:
    def __init__(self):
        self.name = ""
        self.greenhouse_silo = ""
        self.intro_message = ""
        self.timezone = ""
        self.greenhouse_token = ""
        self.slack_token = ""
        self.departments = []
        # Emails of the slack users to be added to every channel for debugging
        self.debug_emails = []
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