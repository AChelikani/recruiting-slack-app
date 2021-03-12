class Config:
    def __init__(self, org_name, greenhouse_url_prefix, greenhouse_token, slack_token):
        self.org_name = org_name
        self.greenhouse_token = greenhouse_token
        self.slack_token = slack_token
        self.greenhouse_url_prefix = greenhouse_url_prefix