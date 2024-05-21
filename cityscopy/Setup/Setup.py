##################################################
# CityScope Python Scanner
# Keystone, decode and send over UDP/HTTP a 2d array
# of uniquely tagged LEGO array
##################################################

from ..utils import parse_json_file, save_settings_to_file, get_folder_path
import requests
import json


class Setup:
    '''Setup a new CityScoPy instance'''

    def __init__(self, CITYSCOPE_PRJ_NAME):
        """
        Initialize a new CityScoPy instance.

        Args:
            CITYSCOPE_PRJ_NAME (str): The name of the CityScope project.
        """
        print(
            f'Setting up a new CityScoPy instance for project: "{CITYSCOPE_PRJ_NAME}"...')
        self.table_settings = parse_json_file(CITYSCOPE_PRJ_NAME)
        self.CITYSCOPE_PRJ_NAME = CITYSCOPE_PRJ_NAME  # table name
        self.CITYIO_URL = self.table_settings['CITYIO_API_URL']
        self.initial_data = self.get_initial_data()

    def get_initial_data(self):
        """
        Fetch all required data from the CityIO API in a single call.

        Returns:
            dict: A dictionary containing the response data from the CityIO API.
        """
        url = self.CITYIO_URL + self.CITYSCOPE_PRJ_NAME + '/'
        headers = {'Content-Type': 'application/json'}
        req = requests.get(url, headers=headers)

        if req.status_code != 200:
            print(
                f'\n- Error: Failed to get data for table: "{self.CITYSCOPE_PRJ_NAME}"')
            return {}

        return req.json()

    def get_cityio_types(self):
        """
        Process and store the types data from the initial API response.

        The types data is modified to include a unique cityscopy_id and a binary pattern
        used for identifying the type in the 2D array.
        """
        types = self.initial_data.get('GEOGRID', {}).get(
            'properties', {}).get('types', {})

        for idx, i in enumerate(types):
            types[i] = {k: types[i][k] for k in ('name', 'color', 'height')}
            types[i]['cityscopy_id'] = idx
            if types[i]['color'][0] == '#':
                types[i]['color'] = [int(types[i]['color'][1:3], 16), int(
                    types[i]['color'][3:5], 16), int(types[i]['color'][5:7], 16)]
            pattern = [int(x) for x in bin(idx)[2:].zfill(16)]
            pattern = ''.join(str(e) for e in pattern)
            types[i]['cityscopy_pattern'] = pattern

        self.table_settings['types'] = types

    def get_cityio_header(self):
        """
        Process and store the header data from the initial API response.

        The header data contains information about the number of rows and columns in the GEOGRID.
        """
        header = self.initial_data.get('GEOGRID', {}).get(
            'properties', {}).get('header', {})
        self.table_settings['nrows'] = header.get('nrows')
        self.table_settings['ncols'] = header.get('ncols')

    def get_cityio_GEOGRIDDATA(self):
        """
        Process and save the GEOGRIDDATA from the initial API response to a JSON file.
        """
        GEOGRIDDATA = self.initial_data.get('GEOGRIDDATA', {})
        with open(get_folder_path() + 'settings/GEOGRIDDATA.json', 'w') as outfile:
            json.dump(GEOGRIDDATA, outfile)

    def setup(self):
        """
        Execute the setup process for the CityScoPy instance.

        This method fetches and processes the types, header, and GEOGRIDDATA from the initial API response,
        and saves the updated settings to a file.
        """
        self.get_cityio_types()
        self.get_cityio_header()
        self.get_cityio_GEOGRIDDATA()
        save_settings_to_file(self.CITYSCOPE_PRJ_NAME, self.table_settings)
        print(
            f'\n- Settings saved successfully for project: "{self.CITYSCOPE_PRJ_NAME}"')
        print(
            f'\n- CityScoPy instance for project: "{self.CITYSCOPE_PRJ_NAME}" is ready!')
