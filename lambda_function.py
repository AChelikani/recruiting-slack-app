from services.applicationwatcherservice.all_orgs_application_watcher import (
    AllOrgsApplicationWatcher,
)
from config.config import parse_config
import json
import boto3


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket="olive-configs", Key="samsara_test.json")
    config_bytes = obj["Body"].read().decode()
    json_config = json.loads(config_bytes)

    configs = [parse_config(json_config)]
    job = AllOrgsApplicationWatcher(configs)
    job.run()
    return {"statusCode": 200, "body": json.dumps("Success")}
