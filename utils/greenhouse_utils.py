import utils.utils as utils
import dateutil.parser
import datetime
import validators


def filter_applications(applications):
    if not applications:
        return []
    filtered_apps = []
    for app in applications:
        # Discard applications that are for prospects, ie. not associated with a job.
        if app["prospect"]:
            continue

        filtered_apps.append(app)

    return filtered_apps


def get_onsite_applications(applications):
    onsite_apps = []
    for app in applications:
        if application_is_onsite(app):
            onsite_apps.append(app)

    return onsite_apps


def application_is_onsite(application):
    try:
        is_not_prospect = application["prospect"] == False
        is_onsite = False
        if application["current_stage"]:
            # TODO: Add department->onsite name/id map to config to determine if interview is onsite that needs channel.
            is_onsite = "onsite" in application["current_stage"]["name"].lower()
            is_onsite = (
                is_onsite or "on-site" in application["current_stage"]["name"].lower()
            )

        return is_not_prospect and is_onsite
    except:
        return False


def get_onsite_interviews(job_stage, interviews):
    interview_type_ids = [interview["id"] for interview in job_stage["interviews"]]
    return [
        interview
        for interview in interviews
        if interview["interview"]["id"] in interview_type_ids
    ]


def valid_onsite_is_tomorrow(
    job_stage, interviews, timestamp, min_interviews_for_channel
):
    """
    1. Onsite (single job stage) is across one or multiple days, but all interviews are scheduled upfront
        - Only one channel will be made the night before the day of the first onsite. All interviews (including those for future days)
        will show up in channel.

    2. Onsite (single job stage) is across multiple days, but only some of the interviews are scheduled upfront
        - Only one channel will be made the night before the day of the first scheduled onsite. The non-scheduled interviews will not appear
        and will not be populated even once scheduled. Once the remaining interviews are scheduled, a new channel will not be created.

    3. Onsite (multiple job stages) and each job stage (ex. onsite #1 and onsite #2) interviews are scheduled as the candidate reaches that stage
        - One channel will be made the night before each job stage, containing the set of already scheduled interviews for that stage.

    4. Onsite (single job stage) interviews are scheduled and rescheduled (before channel creation aka. before night before)
        - One channel will be made the night before the first scheduled interview containing the most recent information.

    5. Onsite (single job stage) interviews are scheduled and rescheduled day-of or in the middle of a multi day onsite (after channel creation).
        - A new channel will not be created. One channel will be created the night before the first scheduled onsite. Any reschedules after the
        channel is made will not be reflected in the channel schedule. Any reschedules (within the same job stage) will not cause a new channel
        to be created.
    """
    if interviews is None:
        print("No interviews ...")
        return False

    onsite_interviews = get_onsite_interviews(job_stage, interviews)
    # Do not create onsite channel if there are too few interviews.
    if len(onsite_interviews) < min_interviews_for_channel:
        return False

    onsite_first_interview_date = get_earliest_interview_datetime(onsite_interviews)
    onsite_first_interview_date = dateutil.parser.isoparse(onsite_first_interview_date)

    target_date = dateutil.parser.isoparse(timestamp)
    one_day_after_target_date = target_date + datetime.timedelta(days=1)

    # Earliest scheduled interview must be tomorrow for channel to be created.
    return (
        target_date.date().isoformat() < onsite_first_interview_date.date().isoformat()
        and onsite_first_interview_date.date().isoformat()
        <= one_day_after_target_date.date().isoformat()
    )


def get_recruiter(candidate):
    if candidate["recruiter"]:
        return {
            "id": candidate["recruiter"]["id"],
            "name": candidate["recruiter"]["name"],
        }

    return None


def get_coordinator(candidate):
    if candidate["coordinator"]:
        return {
            "id": candidate["coordinator"]["id"],
            "name": candidate["coordinator"]["name"],
        }

    return None


def get_interviewers(interviews, onsite_interview_ids):
    # Should only fetch interviews for the onsite interview.
    interviewers = []
    for interview in interviews:
        is_scheduled = interview["status"] == "scheduled"

        if interview["interview"]["id"] not in onsite_interview_ids:
            continue

        if is_scheduled:
            for interviewer in interview["interviewers"]:
                # External users (those without id and name) can be added
                # to Greenhouse interview panels. So some of these values may be null.
                interviewers.append(
                    {
                        "id": interviewer["id"],
                        "name": interviewer["name"],
                        "email": interviewer["email"],
                    }
                )
    return interviewers


def get_interview_kits_from_job_stage(job_stage):
    interview_id_to_interview_kit_id = {}
    for interview in job_stage["interviews"]:
        interview_id_to_interview_kit_id[interview["id"]] = interview["interview_kit"][
            "id"
        ]

    return interview_id_to_interview_kit_id


def construct_interview_kit_url(
    url_prefix, interview_kit_id, candidate_id, application_id
):
    url = "https://{}.greenhouse.io/guides/{}/people/{}?application_id={}".format(
        url_prefix, interview_kit_id, candidate_id, application_id
    )
    return url


def get_earliest_interview_datetime(interviews):
    date = "3021-01-01T00:00:00.000Z"

    if len(interviews) == 0:
        return None

    for interview in interviews:
        if interview["start"]["date_time"] < date:
            date = interview["start"]["date_time"]

    return date


# Get hyphen delimited datestring for onsite interviews.
# Ex. 6-10-6-12 if the interviews are on 6-10 and 6-12.
def get_onsite_date_string(job_stage, interviews, timezone):
    dates = set([])
    onsite_interviews = get_onsite_interviews(job_stage, interviews)
    for interview in onsite_interviews:
        date = interview["start"]["date_time"]
        _, month, day, _, _ = utils.parse_time(date, timezone)
        dates.add((month, day))

    dates = sorted(dates)
    dates = list(map(lambda x: "{}-{}".format(x[0], x[1]), dates))

    return "-".join(dates)


def get_formatted_candidate_contact(candidate):
    email = get_candidate_email(candidate)
    phone = get_candidate_phone(candidate)

    if phone and email:
        return "{} and {}".format(email, phone)
    elif phone:
        return phone
    elif email:
        return email
    else:
        return "Not Found"


def get_candidate_phone(candidate):
    # Choose first phone number unless mobile number is present.
    phone = None
    for phone_number in candidate["phone_numbers"]:
        if not phone:
            phone = phone_number["value"]
        if phone_number["type"] == "mobile":
            phone = phone_number["value"]

    return phone


def get_candidate_email(candidate):
    # Choose first email unless personal email is present.
    email = None
    for email_address in candidate["email_addresses"]:
        if not email:
            email = email_address["value"]
        if email_address["type"] == "personal":
            email = email_address["value"]

    return email


def clean_url(url):
    # Slack blocks only accept URLs that are well formed.
    # Specifically, This means the URL needs to start with a https://www.

    # If URL doesn't start with http or https add that prefix.
    if not url:
        return None

    if not url.startswith("https://") and not url.startswith("http://"):
        url = "https://" + url

    # If URL is still invalid, abandon it.
    if not validators.url(url):
        return None

    return url


def get_candidate_linkedin(candidate, application):
    # NOTE: Greenhouse does not store an explicitly labeled LinkedIn URL field.
    # To find it, we look through the social media URLs and website URLs for a LinkedIn style URL.
    # If we don't find it there, we look inside the answers to an orgs custom questions.
    # If a custom question contains "LinkedIn" in it, we use the answer to that question as the candidates LinkedIn URL.
    social_media_addresses = candidate["social_media_addresses"]
    website_addresses = candidate["website_addresses"]

    all_urls = [item["value"] for item in social_media_addresses + website_addresses]
    for url in all_urls:
        if "linkedin.com" in url:
            cleaned_url = clean_url(url)
            if cleaned_url:
                return cleaned_url
            return None

    for item in application["answers"]:
        if "linkedin" in item["question"].lower():
            cleaned_url = clean_url(item["answer"])
            if cleaned_url:
                return cleaned_url
            return None

    return None


def get_application_resume(application):
    resume_url = None
    for attachment in application["attachments"]:
        if attachment["type"] == "resume":
            resume_url = attachment["url"]

    return resume_url


def get_job_id_and_name_from_application(application):
    # Candidate applications have exactly 1 job.
    job_name = application["jobs"][0]["name"]
    job_id = application["jobs"][0]["id"]
    return job_id, job_name


def get_hiring_managers_from_job(job):
    hiring_managers = []

    for manager in job["hiring_team"]["hiring_managers"]:
        hiring_managers.append({"id": manager["id"], "name": manager["name"]})

    return hiring_managers


def get_department_ids_from_names(department_names, departments):
    ids = []
    for department in departments:
        if department["name"] in department_names:
            ids.append(department["id"])

    return ids


def get_office_ids_from_names(office_names, offices):
    ids = []
    for office in offices:
        if office["name"] in office_names:
            ids.append(office["id"])

    return ids


def dedup_hiring_managers(interviewers, hiring_managers):
    # If there is more than one hiring manager, only list the one on the panel.
    if len(hiring_managers) == 1:
        return hiring_managers

    for hiring_manager in hiring_managers:
        if hiring_manager["id"] in [person["id"] for person in interviewers]:
            return [hiring_manager]

    return hiring_managers


def panel_with_emails(panel_without_emails, user_id_to_email_map):
    # Some members on the panel may have emails already populated.
    panel_ids = set()
    panel = []

    for person in panel_without_emails:
        id = person.get("id")
        name = person.get("name", "Not Found") or "Not Found"
        email = person.get("email", "Not Found") or "Not Found"

        if id in panel_ids:
            continue

        if id:
            panel_ids.add(id)
            email = user_id_to_email_map.get(id) or "Not Found"

        panel.append(
            {
                "id": id or "Not Found",
                "name": name,
                "email": email,
            }
        )

    return panel


# Exclude any jobs that have substrings from exclude_jobs, unless those substrings are in include_jobs.
def is_job_excluded(job, exclude_jobs, include_jobs):
    if len(exclude_jobs) == 0:
        return False

    for exclude_job_substring in exclude_jobs:
        if exclude_job_substring in job["name"]:
            for include_job_substring in include_jobs:
                if include_job_substring in job["name"]:
                    return False
            return True

    return False
