from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackClient:
    def __init__(self, token):
        self.slack_client = WebClient(token=token)

    def create_private_channel(self, name):
        try:
            resp = self.slack_client.conversations_create(name=name, is_private=False)
            return resp["channel"]["id"]
        except SlackApiError as e:
            print(e.response["error"])
            return None

    def invite_users_to_channel(self, channel, users):
        try:
            self.slack_client.conversations_invite(channel=channel)
        except SlackApiError as e:
            print(e.response["error"])
            return None

    def lookup_user_by_email(self, email):
        try:
            resp = self.slack_client.users_lookupByEmail(email=email)
            return resp["user"]["id"]
        except SlackApiError as e:
            print(e.response["error"])
            return None