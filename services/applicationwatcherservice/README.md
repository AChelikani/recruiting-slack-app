# Application Watcher Service
Cron that runs each day and checks for any updates in applications.

If a candidate has been moved to the onsite stage since the last time the job has run:
- Create a private onsite channel for the candidate.
- Invite the recruiter and coordinator to the channel.
- If the candidates interviewers have been assigned.
    - Invite the interviewers into the channel.
- Post a message with details about the schedule, resume, etc.

If a candidate has received an offer since the last time the job has run:
- Rename the channel from `onsite-...` to `offer-...`.
- Post message into channel.
- (Optional) Post candidates email and encourage interviewers to send congradulatory note.


If a candidate accepts the offer, declines the offer, or is rejected after onsite since the last time the job has run:
- Archive the channel.