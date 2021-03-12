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


def get_interviewer_ids(interviews):
    # Should only fetch interviews for the onsite interview.
    ids = []
    for interview in interviews:
        is_scheduled = interview["status"] == "scheduled"

        # TODO: Fetch interviews for this job stage and match on interview["interview"]["id"].
        # This is to make sure that only those scheduled for interviews that are part of the 
        # onsite stage are invited to the channel.
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
