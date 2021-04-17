import os
import secrets
from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
from config.samsara_test import SamsaraTest
from services.applicationwatcherservice.application_watcher import ApplicationWatcher
# Set env variables for API tokens.
secrets.set_tokens()

slack_client = SlackClient(token=os.environ['SLACK_BOT_TOKEN'])
greenhouse_client = GreenhouseClient(token=os.environ['GREENHOUSE_SANDBOX_API_TOKEN'])

if __name__ == "__main__":
    # slack_client.create_private_channel("onsite-bob-jones-2")
    # print(greenhouse_client.get_job_stages())
    # greenhouse_client.get_applications("2021-01-01T13:00:28.038Z")
    config = [SamsaraTest]
    ap = ApplicationWatcher(config)
    ap.run("2021-04-16T00:00:00.000Z")