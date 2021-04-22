from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from config.affinity_test import AffinityTest
import json
import boto3


def lambda_handler(event, context):
    # s3 = boto3.client("s3")

    # obj = s3.get_object(Bucket="olive-configs", Key="affinity_config.json")
    # text = obj["Body"].read().decode()
    # print(text)

    configs = [AffinityTest]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
    return {"statusCode": 200, "body": json.dumps("Success")}
