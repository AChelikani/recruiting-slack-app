import os
import secrets
from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
from config.samsara_test import SamsaraTest
from config.affinity_test import AffinityTest
from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from datetime import date

# Set env variables for API tokens.
secrets.set_tokens()

if __name__ == "__main__":
    # configs = [SamsaraTest]
    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    today = date.today().isoformat()
    # job.run("2021-04-20T00:00:00.000Z")
    job.run(today)
