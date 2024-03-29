from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    def __init__(self, token):
        self.slack_client = WebClient(token=token)

    def create_private_channel(self, name):
        try:
            resp = self.slack_client.conversations_create(name=name, is_private=True)
            return resp["channel"]["id"]
        except SlackApiError as e:
            print(e.response["error"])
            return None

    def create_private_channel_in_workspace(self, name, workspace_id):
        try:
            resp = self.slack_client.conversations_create(
                name=name, is_private=True, team_id=workspace_id
            )
            return resp["channel"]["id"]
        except SlackApiError as e:
            print(e.response["error"])
            return None

    def post_message_to_channel(self, channel, blocks, fallback_text):
        try:
            resp = self.slack_client.chat_postMessage(
                channel=channel, blocks=blocks, text=fallback_text
            )
            return resp["ok"]
        except SlackApiError as e:
            print(e.response["error"])
            return None

    def invite_users_to_channel(self, channel, users):
        try:
            self.slack_client.conversations_invite(channel=channel, users=users)
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

    def set_teams(self, channel_id, team_id, target_team_ids):
        try:
            self.slack_client.admin_conversations_setTeams(
                channel_id=channel_id, team_id=team_id, target_team_ids=target_team_ids
            )
        except SlackApiError as e:
            print(e.response["error"])
            return None
