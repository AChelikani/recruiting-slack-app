from config.config import Config
import os

SamsaraTest = Config(
    "Samsara Test",
    "app2",
    ":wave: Thank you for helping to make Samsara a better place to work.",
    "US/Pacific",
    os.environ["GREENHOUSE_SANDBOX_API_TOKEN"],
    os.environ["SLACK_BOT_TOKEN"],
    debug_slack_emails=["advith.chelikani@samsara.com"],
)
