from config.config import Config
import secrets 
import os

secrets.set_tokens()

AffinityTest = Config("Affinity Test", "app3", ":wave: Thank you for helping to make Affinity a better place to work.", "US/Pacific", os.environ['GREENHOUSE_SANDBOX_API_TOKEN'], os.environ['SLACK_BOT_TOKEN'])