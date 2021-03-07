import os
import secrets
from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient

# Set env variables for API tokens.
secrets.set_tokens()

slack_client = SlackClient(token=os.environ['SLACK_BOT_TOKEN'])
greenhouse_client = GreenhouseClient(token=os.environ['GREENHOUSE_SANDBOX_API_TOKEN'])

if __name__ == "__main__":
    # slack_client.create_private_channel("onsite-bob-jones-2")
    print(greenhouse_client.get_job_stages())
    # greenhouse_client.get_applications()