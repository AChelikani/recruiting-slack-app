from config.config import Config
import secrets
import os

secrets.set_tokens()

Affinity = Config(
    "Affinity",
    "app3",
    ":wave: Thank you for helping to make Affinity a better place. Feel free to use this channel for coordination and Slack the next interviewer when you're done. As always, please submit your scorecards immediately after the interview. Thanks!",
    "US/Pacific",
    [],
    os.environ["GREENHOUSE_SANDBOX_API_TOKEN"],
    os.environ["SLACK_BOT_TOKEN"],
    ["reng@affinity.co"],
)
