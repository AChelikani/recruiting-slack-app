class Config:
    def __init__(
        self,
        org_name,
        greenhouse_url_prefix,
        intro_msg,
        timezone,
        departments,
        greenhouse_token,
        slack_token,
        debug_slack_emails=[],
    ):
        self.org_name = org_name
        self.greenhouse_token = greenhouse_token
        self.slack_token = slack_token
        self.greenhouse_url_prefix = greenhouse_url_prefix
        self.intro_msg = intro_msg
        self.timezone = timezone
        self.departments = departments
        # Emails of the slack users to be added to every channel for debugging
        self.debug_slack_emails = debug_slack_emails
