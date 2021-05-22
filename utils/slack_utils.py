def generate_new_onsite_channel_name(first_name, last_name, date):
    return "{}-{}-{}-{}".format(
        date,
        "onsite",
        first_name.lower().replace(" ", ""),
        last_name.lower().replace(" ", ""),
    )


def format_timestamp_for_slack(unix_ts, backup):
    """
    Slacks allows sending formatted times that will display in the user's timezone.
    https://api.slack.com/reference/surfaces/formatting#date-formatting
    """
    format_str = "<!date^{}^{{time}}|{}>".format(int(unix_ts), backup)
    return format_str
