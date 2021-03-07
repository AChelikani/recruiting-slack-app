import requests

class GreenhouseClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://harvest.greenhouse.io/v1"

    def _print_response(self, resp):
        if resp.status_code >= 400:
            print(resp.text)
        else:
            print(resp.json())

    def get_job_stages(self):
        url = "{}/job_stages".format(self.base_url)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return
        
        return r.json()

    def get_applications(self, last_activity_after):
        '''
        Fetch applications that have been updated since the last_activity_after timestamp.

        Expected usage: Called each day to determine applications that may require actions. 
        '''
        applications = []
        url = "{}/applications?last_activity_after={}".format(self.base_url, last_activity_after)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return

        # Page through all applications.

        print(r.json())
        print(r.headers)
        return r.json()

    def get_scorecards_for_application(self, application_id):
        url = "{}/applications/{}/scorecards".format(self.base_url, application_id)
        r = requests.get(url, auth=(self.token, ""))
        if r.status_code >= 400:
            print(r.text)
            return

        return r.json()

