import secrets
from config.affinity_test import AffinityTest
from config.samsara_test import SamsaraTest
from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from datetime import date

# Set env variables for API tokens.
secrets.set_tokens()

if __name__ == "__main__":
    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
