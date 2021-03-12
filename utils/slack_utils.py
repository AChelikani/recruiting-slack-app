def generate_new_onsite_channel_name(first_name, last_name):
    return "onsite-" + first_name.lower().replace(" ", "") + "-" + last_name.lower().replace(" ", "")