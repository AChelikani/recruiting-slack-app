from config.config import Config
import secrets 
import os

secrets.set_tokens()

SamsaraTest = Config("Samsara Test", "app2", ":wave: Thank you for helping to make Samsara a better place to work.", os.environ['GREENHOUSE_SANDBOX_API_TOKEN'], os.environ['SLACK_BOT_TOKEN'])