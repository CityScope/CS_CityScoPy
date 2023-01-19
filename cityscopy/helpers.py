import requests
import numpy as np
from datetime import timedelta
from datetime import datetime
import json
import os


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


def np_string_tags(self, data):
    # return each item for this field
    d = []
    for i in data:
        d.append(np.array([int(ch) for ch in i]))
    return d

##################################################


# find the type name in the settings JSON file
    # 'types' field and add it to the array
    #

##################################################

def find_type_in_types_obj(types_obj, scan_cell_id):

    for this_type in types_obj:
        this_type_ID = types_obj[this_type]['cityscopy_id']
        if this_type_ID == scan_cell_id:
            return this_type

##################################################


def create_GEOGRIDDATA_json(self, scan_results):
    new_GEOGRIDDATA = []

    types_obj = self.table_settings['types']

    for grid_cell in scan_results:
        # get the type name from the types object
        # and add it to the result tag
        scan_cell_id = int(grid_cell[0]) if type(grid_cell) == list else -1

        this_type = find_type_in_types_obj(types_obj,  scan_cell_id)
        if this_type:
            # print(types_obj[this_type])
            new_GEOGRIDDATA.append(types_obj[this_type])
        else:
            new_GEOGRIDDATA.append({
                "name": "Err",
                "color": [0, 0, 0, 10],
                "cityscopy_id": -1,
                "height": [0, 1, 1]
            })

    return (new_GEOGRIDDATA)


##################################################

def create_data_json(self, multiprocess_shared_dict):
    # 2nd process to json

    SEND_INTERVAL = self.table_settings['interval']
    # initial dummy value for old grid
    old_scan_results = [-1]
    SEND_INTERVAL = timedelta(milliseconds=SEND_INTERVAL)
    last_sent = datetime.now()
    while True:
        scan_results = multiprocess_shared_dict['scan']

        time_since_last_sent = datetime.now() - last_sent
        if (scan_results != old_scan_results) and time_since_last_sent > SEND_INTERVAL:

            # create GEOGRIDDATA json for cityIO and send it
            new_GEOGRIDDATA = create_GEOGRIDDATA_json(self, scan_results)

            try:
                # send to cityIO
                cityio_data_dump = json.dumps(
                    {"GEOGRIDDATA": new_GEOGRIDDATA})

                # if TOGGLE_SEND_TO_CITYIO is on send to cityIO
                if self.table_settings['TOGGLE_SEND_TO_CITYIO']:
                    send_json_to_cityIO(self, cityio_data_dump)
                # else log to console the results and mention that it's not sent
                else:
                    print(
                        '\n[!] CityScoPy grid not sent to cityIO. `TOGGLE_SEND_TO_CITYIO` is off\n')

            # handle errors
            except Exception as ERR:
                print(ERR)
            # match the two grid after send
            old_scan_results = scan_results
            last_sent = datetime.now()

##################################################


def send_json_to_cityIO(self, cityIO_json):
    '''
    sends the grid to cityIO
    '''

    # defining the api-endpoint
    API_ENDPOINT = self.CITYIO_URL + \
        self.table_settings['CITYSCOPE_PRJ_NAME'] + "/"
    # sending post request and saving response as response object
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    req = requests.post(
        url=API_ENDPOINT,
        data=cityIO_json,
        headers=headers
    )
    # debug print
    print('CityScoPy grid sent at:', datetime.now(), 'to cityIO endpoint {',
          self.table_settings['CITYSCOPE_PRJ_NAME'], '}\n')

    if req.status_code != 200:
        print("cityIO might be down. so sad.")

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


def get_folder_path():
    """
    gets the local folder
    return is as a string with '/' at the end
    """
    loc = str(os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))) + '/'
    return loc


##################################################


def get_init_keystone(self):
    # get init keystone from the setting file and return it as a matrix
    keystone_points_list = np.matrix(self.keystone_points_list).reshape(4, 2)
    # convert to np array
    keystone_points_list = np.array(keystone_points_list)
    # break it to points
    ulx = keystone_points_list[0][0]
    uly = keystone_points_list[0][1]
    urx = keystone_points_list[1][0]
    ury = keystone_points_list[1][1]
    blx = keystone_points_list[2][0]
    bly = keystone_points_list[2][1]
    brx = keystone_points_list[3][0]
    bry = keystone_points_list[3][1]
    # init keystone
    init_keystone = [ulx, uly, urx, ury, blx, bly, brx, bry]
    return init_keystone
##################################################
