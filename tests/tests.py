from clients.greenhouse_client import GreenhouseClient
import utils.greenhouse_utils as ghutils
import pytz
import datetime
import os


def TestOnsiteIsTomorrow(gh_token):
    test_cases = [
        {
            "description": "blah",
            "appId": 192611055,
            "timestamp": datetime.datetime(
                2021, 5, 5, 0, 0, 0, 0, pytz.timezone("US/Pacific")
            ).isoformat(),
            "result": True,
        }
    ]

    ghclient = GreenhouseClient(gh_token)

    for test_case in test_cases:
        app = ghclient.get_application(test_case["appId"])
        job_stage = ghclient.get_job_stage(app["current_stage"]["id"])
        interviews = ghclient.get_scheduled_interviews(app["id"])

        is_onsite_tomorrow = ghutils.onsite_is_tomorrow(
            job_stage, interviews, test_case["timestamp"]
        )
        assert is_onsite_tomorrow == test_case["result"], test_case["description"]
