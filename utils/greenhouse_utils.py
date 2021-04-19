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

        return is_not_prospect and is_onsite
    except:
        return False


def onsite_is_tomorrow(interviews, timestamp, timezone):
    scheduled_interviews = [
        interview for interview in interviews if interview["status"] == "scheduled"
    ]

    if len(scheduled_interviews) == 0:
        return False

    upcoming_interview_date = get_earliest_interview_datetime(scheduled_interviews)
    upcoming_interview_date = dateutil.parser.isoparse(upcoming_interview_date)

    target_date = dateutil.parser.isoparse(timestamp)
    one_day_after_target_date = target_date + datetime.timedelta(days=1)

    return (
        upcoming_interview_date.date().isoformat()
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


def combine_gh_ids(arr1, arr2):
    dedup = set()
    for item in arr1:
        dedup.add(item)
    for item in arr2:
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


def get_interview_date_from_scheduled_interviews(interviews, timezone):
    date = get_earliest_interview_datetime(interviews)

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
        return "No contact info found."


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


def get_job_from_application(application):
    # Candidate applications have exactly 1 job.
    job = application["jobs"][0]["name"]
    return job
