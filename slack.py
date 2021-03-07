from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackClient:
    def __init__(self, token):
        self.slack_client = WebClient(token=token)

    def create_private_channel(self, name):
        try:
            self.slack_client.conversations_create(name=name, is_private=False)
        except SlackApiError as e:
            print(e.response["error"])