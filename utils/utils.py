def parse_time(time_str):
    '''
    Parse an RFC 3339 style time string into year, month, day, hour, minute.
    '''
    year = int(time_str[:4])
    month = int(time_str[5:7])
    day = int(time_str[8:10])
    hour = int(time_str[11:13])
    minute = time_str[14:16]

    return year, month, day, hour, minute

def format_time(time_str):
    '''
    Parse an RFC 3339 style time.
    '''
    year, month, day, hour, minute = parse_time(time_str)

    time_suffix = "am"
    if hour > 12:
        time_suffix = "pm"
        hour -= 12

    return "{}:{}{}".format(hour, minute, time_suffix)

