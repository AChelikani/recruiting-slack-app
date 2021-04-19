from config.config import Config
from services.applicationwatcherservice.application_watcher import ApplicationWatcher


class AllOrgsApplicationWatcher:
    """
    The AllOrgsApplicationWatcher runs everyday to kick off the Application Watchers
    for each org's config.
    """

    def __init__(self, configs):
        self.configs = configs

    def run(self, timestamp):
        for config in self.configs:
            ap = ApplicationWatcher(config)
            ap.run(timestamp)
