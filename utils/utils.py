def format_time(time_str):
    '''
    Parse an RFC 3339 style time.
    '''
    year = int(time_str[:4])
    month = int(time_str[5:7])
    day = int(time_str[8:10])
    hour = int(time_str[11:13])
    minute = time_str[14:16]

    time_suffix = "am"
    if hour > 12:
        time_suffix = "pm"
        hour -= 12

    return "{}:{}{}".format(hour, minute, time_suffix)

