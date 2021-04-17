from utils.utils import parse_time

def is_onsite(job_stage):
    ''' 
    Determines if a job_stage is an onsite interview.

    Args:
        job_stage: A Greenhouse job_stage object.
    '''
    try:
        return job_stage["name"].lower().contains("onsite")
    except:
        return False


def application_is_onsite(application):
    try:
        is_active = application["status"] == "active"
        is_not_prospect = application["prospect"] == False
        is_onsite = False
        if application["current_stage"]:
            is_onsite = "onsite" in application["current_stage"]["name"].lower()
        
        return is_active & is_not_prospect & is_onsite
    except:
        return False

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
        interview_id_to_interview_kit_id[interview["id"]] = interview["interview_kit"]["id"]
    
    return interview_id_to_interview_kit_id


def construct_interview_kit_url(url_prefix, interview_kit_id, candidate_id, application_id):
    url = "https://{}.greenhouse.io/guides/{}/people/{}?application_id={}".format(url_prefix, interview_kit_id, candidate_id, application_id)
    return url

def get_interview_date_from_scheduled_interviews(interviews, timezone):
    date = "3021-01-01T00:00:00.000Z"
    
    for interview in interviews:
        if interview["start"]["date_time"] < date:
            date = interview["start"]["date_time"]

    _, month, day, _, _ = parse_time(date, timezone)

    return "{}-{}".format(month, day)