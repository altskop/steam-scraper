import sys
import datetime
import time


class ANSISequence:
    ERASE_LINE = '\x1b[2K\r'
    CURSOR_UP_ONE = '\x1b[1A'
    CURSOR_DOWN_ONE = '\033[1B'


# Helper class containing ANSI sequences to specify colors etc. for terminal output
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def seconds_to_string(seconds):
    return str(datetime.timedelta(seconds=seconds)).split(".", 1)[0]


def get_elapsed_time(start_time):
    return time.time()-start_time


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def str_to_bool(v):
    """Returns True if the passed string contains 'yes', 'true', 't' or 1."""
    return v.lower().lstrip() in ("yes", "true", "t", "1")


def printcolor(string, color):
    '''
    Helper function used to print text. Supports different text colors.
    :param string: text to print
    :param color: an instance of Color to use
    '''
    sys.stdout.write(color + string + Color.ENDC + "\n")
    sys.stdout.flush()


# Used to read the config.yml file and map its contents to the config dictionary
def read_config_file(file) -> dict:
    with open(file, "r") as file:
        config = {}
        lines = [line.rstrip('\n') for line in file]
        for line in lines:
            if len(line) > 0:
                try:
                    conf = line.split(": ", 1)
                    key = conf[0]
                    value = conf[1].split("#", 1)[0].strip()
                    config[key] = value
                except IndexError:
                    pass
        return config


def get_from_json(data, key):
    """
    Helper method to retrieve value from json
    :param data: json object
    :param key: key of value to retrieve
    :return: retrieved value if any, None otherwise
    """
    try:
        result = data[key]
        return result
    except KeyError:
        return None



