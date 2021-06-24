import requests
import dateutil.parser
import datetime
import utils.utils as utils


class GreenhouseClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://harvest.greenhouse.io/v1"

    def _get_paginated_items(self, url, payload={}):
        items = []
        has_next_page = True
        page = 1
        while has_next_page:
            full_payload = {
                "per_page": 500,
                "page": page,
                **payload,
            }
            r = requests.get(url, params=full_payload, auth=(self.token, ""))
            self._handle_rate_limit(r)
            if r.status_code >= 400:
                print(r.text)
                return None

            page_items = r.json()
            items.extend(page_items)

            if len(page_items) == 0:
                has_next_page = False
            page += 1
        return items

    def _print_response(self, resp):
        if resp.status_code >= 400:
            print(resp.text)
        else:
            print(resp.json())

    def _handle_rate_limit(self, resp):
        headers = resp.headers
        if "X-RateLimit-Remaining" in headers:
            remainingReqs = int(headers["X-RateLimit-Remaining"])
            # Any time we get too close to the rate limit, sleep and let the limit reset.
            if remainingReqs < 5:
                utils.inject_throttle_delay(10)
        return

    def get_job_stage(self, id):
        url = "{}/job_stages/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_jobs(self, department_id=None, office_id=None):
        extra_payload = {"status": "open"}
        if department_id:
            extra_payload["department_id"] = department_id
        if office_id:
            extra_payload["office_id"] = office_id
        url = "{}/jobs".format(self.base_url)
        return self._get_paginated_items(url, payload=extra_payload)

    def get_job(self, id):
        url = "{}/jobs/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_application(self, id):
        url = "{}/applications/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_applications_by_job(self, timestamp, job_id):
        """
        Fetch all active applications.

        Expected usage: Called each day to determine applications that may require
        actions.
        """
        target_date = dateutil.parser.isoparse(timestamp)
        month_before_date = target_date - datetime.timedelta(weeks=4)

        payload = {
            "status": "active",
            "last_activity_after": month_before_date.isoformat(),
            "job_id": job_id,
        }
        url = "{}/applications".format(self.base_url)
        return self._get_paginated_items(url, payload)

    def get_scheduled_interviews(self, application_id):
        url = "{}/applications/{}/scheduled_interviews".format(
            self.base_url, application_id
        )
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_all_scheduled_interviews(self, starts_after, ends_before):
        extra_payload = {"starts_after": starts_after, "ends_before": ends_before}
        url = "{}/scheduled_interviews".format(self.base_url)
        return self._get_paginated_items(url, payload=extra_payload)

    def get_candidate(self, id):
        url = "{}/candidates/{}".format(self.base_url, id)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_users(self):
        url = "{}/users".format(self.base_url)
        return self._get_paginated_items(url)

    def get_departments(self):
        url = "{}/departments".format(self.base_url)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()

    def get_offices(self):
        url = "{}/offices".format(self.base_url)
        r = requests.get(url, auth=(self.token, ""))
        self._handle_rate_limit(r)
        if r.status_code >= 400:
            print(r.text)
            return None

        return r.json()
