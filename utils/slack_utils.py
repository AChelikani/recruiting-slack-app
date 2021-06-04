def generate_new_onsite_channel_name(first_name, last_name, date):
    first_name = first_name.lower().replace(" ", "")
    last_name = last_name.lower().replace(" ", "")

    allowed_char_set = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    cleaned_first_name = ""
    cleaned_last_name = ""
    for char in first_name:
        if char in allowed_char_set:
            cleaned_first_name += char

    for char in last_name:
        if char in allowed_char_set:
            cleaned_last_name += char

    return "{}-{}-{}-{}".format(
        date,
        "onsite",
        cleaned_first_name,
        cleaned_last_name,
    )
