from config.config import Config
import os
import secrets

secrets.set_tokens()

AffinityTest = Config(
    "Affinity Test",
    "app3",
    ":wave: Thank you for helping to make Affinity a better place. Feel free to use this channel for coordination and Slack the next interviewer when you're done. As always, please submit your scorecards immediately after the interview. Thanks!",
    "US/Pacific",
    os.environ["GREENHOUSE_SANDBOX_API_TOKEN"],
    os.environ["SLACK_BOT_TOKEN"],
    debug_slack_emails=["advith.chelikani@gmail.com", "robert.km.eng@gmail.com"],
    include_recruiter=False,
)
