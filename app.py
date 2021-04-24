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


if __name__ == "__main__":
    with open("config/samsara_test.json") as f:
        data = json.load(f)

    affinityConfig = parse_config(data)
    affinityConfig.set_greenhouse_token(os.environ["GREENHOUSE_SANDBOX_API_TOKEN"])
    affinityConfig.set_slack_token(os.environ["SLACK_BOT_TOKEN"])
    configs = [affinityConfig]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
