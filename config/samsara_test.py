from config.config import Config
import secrets 
import os

secrets.set_tokens()

SamsaraTest = Config("Samsara Test", "app2", os.environ['GREENHOUSE_SANDBOX_API_TOKEN'], os.environ['SLACK_BOT_TOKEN'])