import os
import secrets
from clients.greenhouse_client import GreenhouseClient
from clients.slack_client import SlackClient
from config.samsara_test import SamsaraTest
from config.affinity_test import AffinityTest
from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)

# Set env variables for API tokens.
secrets.set_tokens()

if __name__ == "__main__":
    # configs = [SamsaraTest]
    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    job.run("2021-04-18T00:00:00.000Z")
