from config.config import Config
import os
import secrets

secrets.set_tokens()

SamsaraTest = Config(
    "Samsara Test",
    "app2",
    ":wave: Thank you for helping to make Samsara a better place to work.",
    "US/Pacific",
    os.environ["GREENHOUSE_SANDBOX_API_TOKEN"],
    os.environ["SLACK_BOT_TOKEN"],
    departments=["Engineering"],
    debug_slack_emails=["advith.chelikani@samsara.com"],
)
