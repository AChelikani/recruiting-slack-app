import tokens

# Set env variables for API tokens.
tokens.set_tokens()

from config.config import parse_config
from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from datetime import date
import json
import os

tokens.set_tokens()

if __name__ == "__main__":
    with open("config/samsara_test.json") as f:
        data = json.load(f)

    samsaraTestConfig = parse_config(data)
    configs = [samsaraTestConfig]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
