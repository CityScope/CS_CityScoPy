import os
import json
from datetime import datetime


##################################################
def get_folder_path():
    """
    gets the local folder
    return is as a string with '/' at the end
    """
    loc = str(os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))) + '/'
    return loc


##################################################


def save_settings_to_file(CITYSCOPE_PRJ_NAME, table_settings):
    # write the settings file to the json file
    SETTINGS_PATH = "./settings/" + CITYSCOPE_PRJ_NAME + ".json"
    # init array for json fields
    settings_file = get_folder_path() + SETTINGS_PATH
    with open(settings_file, 'w') as outfile:
        json.dump(table_settings, outfile)

    print('\n- Settings saved to file at:', datetime.now(), '\n')

##################################################


def parse_json_file(CITYSCOPE_PRJ_NAME):
    """
    get data from JSON settings files.

    Steps:
    - opens file
    - checks if field has objects longer than one char [such as the 'tags' field]
    - if so, converts them to numpy arrays

    Args:

    Returns the desired filed
    """
    SETTINGS_PATH = "./settings/" + CITYSCOPE_PRJ_NAME + ".json"
    # init array for json fields
    settings_file = get_folder_path() + SETTINGS_PATH

    # open json file
    with open(settings_file) as d:
        data = json.load(d)
    return (data)

##################################################
