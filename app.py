import secrets

# Set env variables for API tokens.
secrets.set_tokens()

from config.affinity_test import AffinityTest
from config.affinity import Affinity
from config.samsara_test import SamsaraTest
from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from datetime import date


if __name__ == "__main__":
    # configs = [Affinity]
    configs = [AffinityTest]
    # configs = [SamsaraTest]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
