class Config:
    def __init__(self):
        self.org_name = ""
        self.greenhouse_url_prefix = ""
        self.intro_msg = ""
        self.timezone = ""
        self.greenhouse_token = ""
        self.slack_token = ""
        self.departments = []
        # Emails of the slack users to be added to every channel for debugging
        self.debug_slack_emails = []
        self.include_recruiter = True

    def set_org_name(self, org_name):
        self.org_name = org_name

    def set_greenhouse_url_prefix(self, greenhouse_url_prefix):
        self.greenhouse_url_prefix = greenhouse_url_prefix

    def set_intro_msg(self, intro_msg):
        self.intro_msg = intro_msg

    def set_timezone(self, timezone):
        self.timezone = timezone

    def set_greenhouse_token(self, greenhouse_token):
        self.greenhouse_token = greenhouse_token

    def set_slack_token(self, slack_token):
        self.slack_token = slack_token

    def set_departments(self, departments):
        self.departments = departments

    def set_debug_slack_emails(self, debug_slack_emails):
        self.debug_slack_emails = debug_slack_emails

    def set_include_recruiter(self, include_recruiter):
        self.include_recruiter = include_recruiter


def parse_config(json):
    """
    Parse a config from a loaded JSON into a Config object.
    """
    config = Config()
    if "name" in json:
        config.set_org_name(json["name"])

    if "greenhouseSilo" in json:
        config.set_greenhouse_url_prefix(json["greenhouseSilo"])

    if "introMessage" in json:
        config.set_intro_msg(json["introMessage"])

    if "timezone" in json:
        config.set_timezone(json["timezone"])

    if "greenhouseToken" in json:
        config.set_greenhouse_token(json["greenhouseToken"])

    if "slackToken" in json:
        config.set_slack_token(json["slackToken"])

    if "departments" in json:
        config.set_departments(json["departments"])

    if "debugEmails" in json:
        config.set_debug_slack_emails(json["debugEmails"])

    if "includeRecruiter" in json:
        config.set_include_recruiter(json["includeRecruiter"])

    return config