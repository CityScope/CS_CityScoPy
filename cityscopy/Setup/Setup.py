'''
##################################################
CityScope Python Scanner
Keystone, decode and send over UDP/HTTTP a 2d array
of uniquely tagged LEGO array
##################################################
'''
from ..helpers import parse_json_file, save_settings_to_file, get_folder_path
import requests
import json


class Setup:
    '''Setup a new for cityscopy instance'''

    def __init__(self, CITYSCOPE_PRJ_NAME):
        print('Setting up a new CityScoPy instance for project: "{}"...'.format(
            CITYSCOPE_PRJ_NAME))
        # load settings from json file
        self.table_settings = parse_json_file(CITYSCOPE_PRJ_NAME)
        self.CITYSCOPE_PRJ_NAME = CITYSCOPE_PRJ_NAME  # table name
        self.CITYIO_URL = self.table_settings['CITYIO_API_URL']

    ##################################################

    '''
    a generic function that gets a field from cityio and returns it
    '''

    def get_cityio_field(self, table_name, field_name):

        # print in a nice way the table name and the field name
        print('\n- Getting field: "{}" from table: "{}"'.format(
            field_name, table_name))

        url = self.CITYIO_URL + table_name + '/'
        headers = {'Content-Type': 'application/json'}
        req = requests.get(url+field_name, headers=headers)
        if req.status_code != 200:
            print("Error getting field from cityIO!")
        field = req.json()
        return (field)

    ##################################################
    '''
    a function that gets the types from cityio and returns a dictionary of types each type is a dictionary with the following fields:
    'name', 'id' and 'color'
    - the function also adds a new field called 'cityscopy_id' to each type
    - this field is a unique id for each type
    - the function also adds a new field called 'cityscopy_pattern' to each type
    - this field is a list of 16 0 and 1 values. This pattern is used to identify the type in the 2d array
    '''

    def get_cityio_types(self, table_name):

        types = self.get_cityio_field(table_name, 'GEOGRID/properties/types/')

        # from each type, remove all fields except 'name', 'id' and 'color'
        for idx, i in enumerate(types):
            types[i] = {k: types[i][k] for k in ('name', 'color', 'height')}
            # give each type a unique id in a new field called 'cityscopy_id'
            types[i]['cityscopy_id'] = idx

            # if the color is in hex format, convert it to a list of 3 values, i.e. [255, 255, 255]
            if types[i]['color'][0] == '#':
                types[i]['color'] = [int(types[i]['color'][1:3], 16), int(
                    types[i]['color'][3:5], 16), int(types[i]['color'][5:7], 16)]

            # for each type, add a pattern field that is a list of 16 0 and 1 values. This pattern is used to identify the type in the 2d array
            pattern = [int(x) for x in bin(idx)[2:].zfill(16)]
            #  convert the pattern to string
            pattern = ''.join(str(e) for e in pattern)
            types[i]['cityscopy_pattern'] = pattern
        # write the types to the settings object
        self.table_settings['types'] = types

    ##################################################
    '''
    a function that gets the 'header' from cityio and add it to the settings file. The header is a dictionary with the following fields:
      "nrows", "ncols"
    '''

    def get_cityio_header(self, table_name):
        header = self.get_cityio_field(
            table_name, 'GEOGRID/properties/header/')
        # write the header to the settings file
        self.table_settings['nrows'] = header['nrows']
        self.table_settings['ncols'] = header['ncols']

    ##################################################
    '''
    a function that gets the 'GEOGRIDDATA' from cityio 
    and save it to a file called 'GEOGRIDDATA.json' in the project folder
    '''

    def get_cityio_GEOGRIDDATA(self, table_name):
        GEOGRIDDATA = self.get_cityio_field(
            table_name, 'GEOGRIDDATA/')
        # write the GEOGRIDDATA to a file
        with open(get_folder_path() + 'settings/GEOGRIDDATA.json', 'w') as outfile:
            json.dump(GEOGRIDDATA, outfile)

    ##################################################
    # a function that gets the types cityio and write these types to the settings file in a new 'types' field

    def setup(self):
        # get the types from cityio
        self.get_cityio_types(self.table_settings['CITYSCOPE_PRJ_NAME'])
        # get the header from cityio
        self.get_cityio_header(self.table_settings['CITYSCOPE_PRJ_NAME'])

        # get the GEOGRIDDATA from cityio
        # and save it to a new file called 'GEOGRIDDATA.json'
        self.get_cityio_GEOGRIDDATA(self.table_settings['CITYSCOPE_PRJ_NAME'])

        # save the settings to file
        save_settings_to_file(
            self.CITYSCOPE_PRJ_NAME, self.table_settings)

        print("settings file log:\n", json.dumps(
            self.table_settings, indent=4))
