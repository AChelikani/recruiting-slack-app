def is_onsite(job_stage):
    ''' 
    Determines if a job_stage is an onsite interview.

    Args:
        job_stage: A Greenhouse job_stage object.
    '''
    try:
        return job_stage["name"].lower().contains("onsite")
    else:
        return False