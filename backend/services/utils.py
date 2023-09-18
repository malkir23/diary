import datetime
import re

def utc_now(date_format=''):
    now = datetime.datetime.now()
    if not date_format: return now
    return now.strftime(date_format)


def remove_nulls_from_dict(dict_value):
    return {k: v for k, v in dict_value.items() if v is not None}


def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Value not found


def is_number(value):
    if isinstance(value, str):
        # Regex pattern to match integer or float
        pattern = r'^[-+]?[0-9]+(\.[0-9]+)?$'
        return bool(re.match(pattern, value))
    elif isinstance(value, int) or isinstance(value, float):
        return True
    return False

