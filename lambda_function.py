from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from config.affinity_test import AffinityTest
from datetime import date
import json


def lambda_handler(event, context):
    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    today = date.today().isoformat()
    job.run(today)
    return {"statusCode": 200, "body": json.dumps("Success")}
