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
import tokens

tokens.set_tokens()

if __name__ == "__main__":
    with open("config/samsara_sandbox.json") as f:
        data = json.load(f)

    samsaraSandboxConfig = parse_config(data)
    configs = [samsaraSandboxConfig]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
