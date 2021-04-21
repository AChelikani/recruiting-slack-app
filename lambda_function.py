from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from config.affinity_test import AffinityTest
import json


def lambda_handler(event, context):
    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
    return {"statusCode": 200, "body": json.dumps("Success")}
