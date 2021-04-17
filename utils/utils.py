import pytz
from datetime import datetime


def parse_time(time_str, timezone):
    '''
    Parse an RFC 3339 style time string into year, month, day, hour, minute.
    '''
    time_str = localize_time(time_str, timezone)

    year = int(time_str[:4])
    month = int(time_str[5:7])
    day = int(time_str[8:10])
    hour = int(time_str[11:13])
    minute = time_str[14:16]

    return year, month, day, hour, minute

def format_time(time_str, timezone):
    '''
    Parse an RFC 3339 style time.
    '''
    year, month, day, hour, minute = parse_time(time_str, timezone)

    time_suffix = "am"
    if hour > 12:
        time_suffix = "pm"
        hour -= 12

    return "{}:{}{}".format(hour, minute, time_suffix)


def localize_time(time_str, timezone):
    '''
    Localize a RFC 3339 style time string into a particular timezone.
    '''
    # Assume all times are in RFC 3339 UTC.
    date_format = '%Y-%m-%dT%H:%M:%S.%f'
    time_str = time_str[:time_str.find("Z")]

    # Time format: "YYYY-MM-DDTHH:MM:SS.000"
    datetime_object = datetime.strptime(time_str, date_format)
    datetime_object = pytz.utc.localize(datetime_object)

    my_timezone = pytz.timezone(timezone)
    localized_datetime = datetime_object.astimezone(my_timezone)

    return localized_datetime.strftime(date_format)
    