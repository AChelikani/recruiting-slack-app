class Config:
    def __init__(
        self,
        org_name,
        greenhouse_url_prefix,
        intro_msg,
        timezone,
        greenhouse_token,
        slack_token,
        departments=None,
        debug_slack_emails=None,
        include_recruiter=True,
    ):
        self.org_name = org_name
        self.greenhouse_token = greenhouse_token
        self.slack_token = slack_token
        self.greenhouse_url_prefix = greenhouse_url_prefix
        self.intro_msg = intro_msg
        self.timezone = timezone
        self.departments = [] if departments is None else departments
        # Emails of the slack users to be added to every channel for debugging
        self.debug_slack_emails = (
            [] if debug_slack_emails is None else debug_slack_emails
        )

        self.include_recruiter = include_recruiter
