from utils.utils import parse_time
import dateutil.parser
import datetime


def is_onsite(job_stage):
    """
    Determines if a job_stage is an onsite interview.

    Args:
        job_stage: A Greenhouse job_stage object.
    """
    try:
        return job_stage["name"].lower().contains("onsite")
    except:
        return False


def application_is_onsite(application):
    try:
        is_not_prospect = application["prospect"] == False
        is_onsite = False
        if application["current_stage"]:
            is_onsite = "onsite" in application["current_stage"]["name"].lower()
        print(
            "application_is_onsite: id: {}, stage: {},".format(
                application["id"], application["current_stage"]["name"]
            )
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


def onsite_is_tomorrow(job_stage, interviews, timestamp):
    onsite_interviews = get_onsite_interviews(job_stage, interviews)
    print("Num onsite interviews in job stage: {}".format(len(onsite_interviews)))
    if len(onsite_interviews) == 0:
        return False

    onsite_first_interview_date = get_earliest_interview_datetime(onsite_interviews)
    onsite_first_interview_date = dateutil.parser.isoparse(onsite_first_interview_date)
    print("Onsite first interview date: {}".format(str(onsite_first_interview_date)))

    target_date = dateutil.parser.isoparse(timestamp)
    one_day_after_target_date = target_date + datetime.timedelta(days=1)
    print("Onsite target day: {}".format(str(one_day_after_target_date)))

    return (
        target_date.date().isoformat() < onsite_first_interview_date.date().isoformat()
        and onsite_first_interview_date.date().isoformat()
        <= one_day_after_target_date.date().isoformat()
    )


def get_recruiter_and_coordinator_ids(candidate):
    ids = []
    if candidate["recruiter"]:
        ids.append(candidate["recruiter"]["id"])
    if candidate["coordinator"]:
        ids.append(candidate["coordinator"]["id"])

    return ids


def get_interviewer_ids(interviews, onsite_interview_ids):
    # Should only fetch interviews for the onsite interview.
    ids = []
    for interview in interviews:
        is_scheduled = interview["status"] == "scheduled"

        if interview["interview"]["id"] not in onsite_interview_ids:
            continue

        if is_scheduled:
            for interviewer in interview["interviewers"]:
                ids.append(interviewer["id"])
    return ids


def combine_gh_ids(arr1, arr2, arr3):
    dedup = set()
    for item in arr1:
        dedup.add(item)
    for item in arr2:
        dedup.add(item)
    for item in arr3:
        dedup.add(item)
    return list(dedup)


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


def get_first_onsite_interview_date_from_scheduled_interviews(
    job_stage, interviews, timezone
):
    onsite_interviews = get_onsite_interviews(job_stage, interviews)
    date = get_earliest_interview_datetime(onsite_interviews)

    _, month, day, _, _ = parse_time(date, timezone)

    return "{}-{}".format(month, day)


def get_candidate_contact(candidate):
    email = get_candidate_email(candidate)
    phone = get_candidate_phone(candidate)

    if phone and email:
        return "{} and {}".format(email, phone)
    elif phone:
        return phone
    elif email:
        return email
    else:
        return "No contact info found for candidate."


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


def get_candidate_linkedin(candidate):
    # NOTE: Greenhouse does not store an explicitly labeled LinkedIn URL field.
    # To find it, we look through the social media URLs and website URLs for a LinkedIn style URL.
    social_media_addresses = candidate["social_media_addresses"]
    website_addresses = candidate["website_addresses"]

    all_urls = [item["value"] for item in social_media_addresses + website_addresses]
    for url in all_urls:
        if "linkedin.com" in url:
            return url

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
