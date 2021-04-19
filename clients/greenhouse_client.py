import requests
import dateutil.parser
import datetime


class GreenhouseClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://harvest.greenhouse.io/v1"

    def _print_response(self, resp):
        if resp.status_code >= 400:
            print(resp.text)
        else:
            print(resp.json())

    def get_job_stage(self, id):
        url = "{}/job_stages/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_applications(self, timestamp):
        """
        Fetch all active applications.

        Expected usage: Called each day to determine applications that may require
        actions.
        """
        applications = []
        url = "{}/applications".format(self.base_url)
        target_date = dateutil.parser.isoparse(timestamp)
        month_before_date = target_date - datetime.timedelta(weeks=4)
        payload = {
            "status": "active",
            "per_page": 500,
            "last_activity_after": month_before_date.isoformat(),
        }
        r = requests.get(url, params=payload, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        # TODO: Page through all applications.
        return r.json()

    def get_scheduled_interviews(self, application_id):
        url = "{}/applications/{}/scheduled_interviews".format(
            self.base_url, application_id
        )
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_candidate(self, id):
        url = "{}/candidates/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_users(self):
        users = []
        url = "{}/users".format(self.base_url)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        # TODO: Paginate through all users
        return r.json()

    def get_scorecards_for_application(self, application_id):
        url = "{}/applications/{}/scorecards".format(self.base_url, application_id)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()
