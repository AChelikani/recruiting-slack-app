from config.config import Config
from services.applicationwatcherservice.application_watcher import ApplicationWatcher
import pytz
import datetime


class AllOrgsApplicationWatcher:
    """
    The AllOrgsApplicationWatcher runs everyday to kick off the Application Watchers
    for each org's config.
    """

    def __init__(self, configs):
        self.configs = configs

    def run(self):
        for config in self.configs:
            print("Processing... {}".format(config.name))
            ap = ApplicationWatcher(config)
            today = datetime.datetime.now(
                pytz.timezone(config.default_timezone)
            ).isoformat()
            print("Today: {}\n".format(str(today)))
            ap.run(today)
