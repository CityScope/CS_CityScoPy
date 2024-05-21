import requests
import numpy as np
from datetime import timedelta
from datetime import datetime
import json


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

'''
import asyncio
import websockets
import json

async def send_data_over_websocket(url, data):
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(data))
        response = await websocket.recv()
        print(f"Response from server: {response}")

def create_data_json(scanner, shared_dict):
    url = scanner.CITYIO_URL.replace("http", "ws")  # Assuming WebSocket endpoint is similar to HTTP endpoint
    while True:
        data = {
            'table_name': scanner.CITYSCOPE_PRJ_NAME,
            'data': shared_dict['scan']
        }
        asyncio.run(send_data_over_websocket(url, data))
        time.sleep(1)  # Adjust as necessary for your scan frequency
'''


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
    print('CityScoPy grid attempted update at:', datetime.now(), 'to cityIO endpoint {',
          self.table_settings['CITYSCOPE_PRJ_NAME'], '}\n')

    if req.status_code != 200:
        # sad emoji for error
        print('😞', 'Error:', req.status_code, req.text)

##################################################
