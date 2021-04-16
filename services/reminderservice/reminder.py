class Reminder():
    '''
    The reminder service generates reminders for if:
    - A scorecard is late.
    '''
    def __init__(self, configs):
        self.configs = configs

    def _generate_scorecard_reminders(self):
        # For all the completed interviews that happened since the last pull.
        # Enqueue their IDs, application ID, as well as the time their SLA will be breached.
        #
        # Within the queue:
        #   - At the time of their SLA breach, pull scorecards of that application ID.
        #   - If scorecard for specified interview is not filled out, send reminder.
        #       - Enqueue reminder again for next SLA breach. 


        pass

    def run(self):
        pass