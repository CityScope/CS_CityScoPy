
# grid maker imports
import requests
import cv2
import numpy as np
import math
from datetime import date
from datetime import timedelta
from datetime import datetime
import time
import json
import sys
import os
import socket
from multiprocessing import Process, Manager
from subprocess import Popen
import random
from grid_geojson.module import grid_geojson


class Cityscopy:

    ##################################################

    def __init__(self):
        # load info from json file
        self.SETTINGS_PATH = 'cityio.json'
        # get the table settings
        self.table_settings = self.parse_json_file('table')
        print('getting settings for CityScopy')

        if self.table_settings['objects']['cityscopy']['makeGrid'] == True:
            # make geojson grid
            self.gridMaker()

        if self.table_settings['objects']['cityscopy']['scan'] == True:
            # get init keystones
            self.init_keystone = self.get_init_keystone()
            # init corners
            self.selected_corner = None
            self.corner_direction = None
            # start the multi proccess
            self.start_multiproccess()

    ##################################################

    def start_multiproccess(self):
        # define global list manager
        MANAGER = Manager()
        # create shared global list to work with both processes
        self.multiprocess_shared_dict = MANAGER.dict()

        # init a dict with rand data to be shared among procceses
        self.multiprocess_shared_dict['scan'] = [-1, -1]

        # defines a multiprocess for sending the data
        self.process_send_packet = Process(target=self.create_data_json,
                                           args=([self.multiprocess_shared_dict]))
        # start porcess
        self.process_send_packet.start()
        # start camera on main thread due to multiprocces issue
        self.scanner_function(self.multiprocess_shared_dict)
        # join the two processes
        self.process_send_packet.join()

    ##################################################

    def get_init_keystone(self):

     # load the initial keystone data from file
        keystone_points_array = np.loadtxt(
            self.get_folder_path()+'keystone.txt', dtype=np.float32)

        # break it to points
        ulx = keystone_points_array[0][0]
        uly = keystone_points_array[0][1]
        urx = keystone_points_array[1][0]
        ury = keystone_points_array[1][1]
        blx = keystone_points_array[2][0]
        bly = keystone_points_array[2][1]
        brx = keystone_points_array[3][0]
        bry = keystone_points_array[3][1]
        # init keystone
        init_keystone = [ulx, uly, urx, ury, blx, bly, brx, bry]
        return init_keystone

    ##################################################

    def scanner_function(self, multiprocess_shared_dict):

        # define the table params
        grid_dimensions_x = self.table_settings['header']['spatial']['nrows']
        grid_dimensions_y = self.table_settings['header']['spatial']['ncols']

        array_of_tags_from_json = self.np_string_tags(
            self.table_settings['objects']['cityscopy']['tags'])

        array_of_maps_form_json = self.table_settings['header']['mapping']['type']

        # init type list array
        TYPES_LIST = []

        # holder of old cell colors array to check for new scan
        OLD_CELL_COLORS_ARRAY = []

        # define the video stream
        try:
            # try from a device 1 in list, not default webcam
            video_capture = cv2.VideoCapture(1)
            print('no camera in pos 0')
            time.sleep(1)
            # if not exist, use device 0
            if not video_capture.isOpened():
                video_capture = cv2.VideoCapture(0)
                time.sleep(1)

        finally:
            print('got video at: ', video_capture)

        if grid_dimensions_y < grid_dimensions_x:
            # get the smaller of two grid ratio x/y or y/x
            grid_ratio = grid_dimensions_y / grid_dimensions_x
            video_resolution_x = int(video_capture.get(3))
            video_resolution_y = int(video_capture.get(3)*grid_ratio)
        else:
            # get the smaller of two grid ratio x/y or y/x
            grid_ratio = grid_dimensions_x / grid_dimensions_y
            video_resolution_x = int(video_capture.get(3)*grid_ratio)
            video_resolution_y = int(video_capture.get(3))

            # video_resolution_y = int(video_capture.get(3))

            # define the video window
        cv2.namedWindow('scanner_gui_window', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('scanner_gui_window', 400, 400)
        cv2.moveWindow('scanner_gui_window', 10, 100)

        # call colors dictionary
        DICTIONARY_COLORS = {
            # black
            0: (0, 0, 0),
            # white
            1: (255, 255, 255)
        }

        # define the size for each scanner
        x_ratio = int(video_resolution_x/(grid_dimensions_x*4))
        y_ratio = int(video_resolution_y/(grid_dimensions_y*4))
        scanner_square_size = np.minimum(x_ratio, y_ratio)

        # create the location  array of scanners
        array_of_scanner_points_locations = self.get_scanner_pixel_coordinates(
            grid_dimensions_x, grid_dimensions_y, video_resolution_x,
            video_resolution_y, scanner_square_size)

    # run the video loop forever
        while True:
            # get a new matrix transformation every frame
            KEY_STONE_DATA = self.keystone(
                video_resolution_x, video_resolution_y, self.listen_to_UI_interaction(self.init_keystone))

            # zero an array to collect the scanners
            CELL_COLORS_ARRAY = []

            # read video frames
            _, THIS_FRAME = video_capture.read()
            # mirror camera
            if self.table_settings['objects']['cityscopy']['mirror_cam'] is 1:
                THIS_FRAME = cv2.flip(THIS_FRAME, 1)

            # warp the video based on keystone info
            DISTORTED_VIDEO_STREAM = cv2.warpPerspective(
                THIS_FRAME, KEY_STONE_DATA, (video_resolution_x, video_resolution_y))

            # cell counter
            count = 0
            # run through locations list and make scanners
            for this_scanner_location in array_of_scanner_points_locations:

                # set x and y from locations array
                x = this_scanner_location[0]
                y = this_scanner_location[1]

                # use this to control reduction of scanner size
                this_scanner_max_dimension = int(scanner_square_size)
                scanner_reduction = int(scanner_square_size/4)
                # short vars
                x_red = x + this_scanner_max_dimension-scanner_reduction
                y_red = y + this_scanner_max_dimension-scanner_reduction

                # set scanner crop box size and position
                # at x,y + crop box size

                this_scanner_size = DISTORTED_VIDEO_STREAM[y+scanner_reduction:y_red,
                                                           x+scanner_reduction:x_red]

                # draw rects with mean value of color
                mean_color = cv2.mean(this_scanner_size)

                # convert colors to rgb
                color_b, color_g, color_r, _ = np.uint8(mean_color)
                mean_color_RGB = np.uint8([[[color_b, color_g, color_r]]])

                # select the right color based on sample
                scannerCol = self.select_color_by_mean_value(mean_color_RGB)

                # add colors to array for type analysis
                CELL_COLORS_ARRAY.append(scannerCol)

                # get color from dict
                thisColor = DICTIONARY_COLORS[scannerCol]

                # ? only draw vis if settings has 1 in gui
                if self.table_settings['objects']['cityscopy']['gui'] is 1:
                    # draw rects with frame colored by range result
                    cv2.rectangle(DISTORTED_VIDEO_STREAM,
                                  (x+scanner_reduction,
                                   y+scanner_reduction),
                                  (x_red,
                                      y_red),
                                  thisColor, 1)
                # cell counter
                count = count + 1

            # reduce unnecessary scan analysis and sending by comparing
            # the list of scanned cells to an old one
            if CELL_COLORS_ARRAY != OLD_CELL_COLORS_ARRAY:

                # send array to method for checking types
                TYPES_LIST = self.find_type_in_tags_array(
                    CELL_COLORS_ARRAY, array_of_tags_from_json,
                    array_of_maps_form_json,
                    grid_dimensions_x, grid_dimensions_y)

                # match the two
                OLD_CELL_COLORS_ARRAY = CELL_COLORS_ARRAY

                # [!] Store the type list results in the multiprocess_shared_dict
                multiprocess_shared_dict['scan'] = TYPES_LIST

            else:
                # else don't do it
                pass

            if self.table_settings['objects']['cityscopy']['gui'] is 1:
                # draw the video to screen
                cv2.imshow("scanner_gui_window", DISTORTED_VIDEO_STREAM)

        # close opencv
        video_capture.release()
        cv2.destroyAllWindows()

    ##################################################

    def get_scanner_pixel_coordinates(self, grid_dimensions_x, grid_dimensions_y, video_res_x, video_res_y, scanner_square_size):
        """Creates list of pixel coordinates for scanner.

        Steps:
            - Determine virtual points on the grid that
            will be the centers of blocks.
            - Transforms virtual[x, y] coordinate pairs to
            pixel representations for scanner.
            - Transform those virtual points pixel coordinates
            and expand them into 3x3 clusters of pixel points

        Args:

        Returns list of[x, y] pixel coordinates for scanner to read.
        """

        # calc the half of the ratio between
        # screen size and the x dim of the grid
        # to center the grid in both Y & X
        grid_x_offset = int(0.5 *
                            (video_res_x - (grid_dimensions_x*scanner_square_size*4)))
        grid_y_offset = int(0.5 *
                            (video_res_y - (grid_dimensions_y*scanner_square_size*4)))

        # create the list of points
        pixel_coordinates_list = []

        # define a cell gap for grided cases [plexi table setup]
        cells_gap = self.table_settings['objects']['cityscopy']['cell_gap']

        # create the 4x4 sub grid cells
        for y in range(0, grid_dimensions_y):
            for x in range(0, grid_dimensions_x):

                x_positions = x * ((scanner_square_size*4)+cells_gap)
                y_positions = y * ((scanner_square_size*4)+cells_gap)

                # make the actual location for the 4x4 scanner points
                for i in range(0, 4):
                    for j in range(0, 4):
                        # add them to list
                        pixel_coordinates_list.append(
                            # x value of this scanner location
                            [grid_x_offset+x_positions + (i*scanner_square_size),
                             # y value of this scanner location
                             grid_y_offset+y_positions + (j*scanner_square_size)])
        return pixel_coordinates_list

    ##################################################

    def np_string_tags(self, json_data):
        # return each item for this field
        d = []
        for i in json_data:
            d.append(np.array([int(ch) for ch in i]))
        return d

    ##################################################

    # 2nd proccess to
    def create_data_json(self, multiprocess_shared_dict):
        self.table_settings = self.parse_json_file('table')
        SEND_INTERVAL = self.table_settings['objects']['cityscopy']['interval']
        # initial dummy value for old grid
        old_scan_results = [-1]
        SEND_INTERVAL = timedelta(milliseconds=SEND_INTERVAL)
        last_sent = datetime.now()

        while True:
            scan_results = multiprocess_shared_dict['scan']
            from_last_sent = datetime.now() - last_sent
            if (scan_results != old_scan_results) and from_last_sent > SEND_INTERVAL:
                try:
                    # convert to json
                    json_struct = self.table_settings
                    json_struct['grid'] = scan_results
                    if self.table_settings['objects']['cityscopy']['cityio'] is True:
                        cityIO_json = json.dumps(json_struct)
                        self.send_json_to_cityIO(cityIO_json)
                    else:
                        self.send_json_to_UDP(scan_results)
                except Exception as e:
                    print(e)

                # match the two grid after send
                old_scan_results = scan_results
                last_sent = datetime.now()

                # debug print
                print('\n', 'CityScopy grid sent at:', datetime.now())

    ##################################################

    def send_json_to_cityIO(self, cityIO_json):
        # defining the api-endpoint
        API_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/" + \
            self.table_settings['header']['name']
        # sending post request and saving response as response object
        req = requests.post(url=API_ENDPOINT, data=cityIO_json)
        if req.status_code != 200:
            print("cityIO might be down. so sad.")
        print(req)

    ##################################################

    def send_json_to_UDP(self, scan_results):
        # defining the udp endpoint
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(str(scan_results).encode('utf-8'), (UDP_IP, UDP_PORT))
        except Exception as e:
            print(e)

    ##################################################

    def parse_json_file(self, field):
        """
        get data from JSON settings files.

        Steps:
        - opens file
        - checks if field has objects longer than one char [such as the 'tags' field]
        - if so, converts them to numpy arrays

        Args:

        Returns the desired filed
        """

        # init array for json fields
        settings_file = self.get_folder_path()+self.SETTINGS_PATH
        # open json file
        with open(settings_file) as d:
            data = json.load(d)
        return(data[field])

    ##################################################

    def get_folder_path(self):
        """
        gets the local folder
        return is as a string with '/' at the ednd
        """
        loc = str(os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))) + '/'
        return loc

    ##################################################

    def listen_to_UI_interaction(self, init_keystone):
        """
        listens to user interaction.

        Steps:
        listen to UI

        Args:

        Returns 4x2 array of points location for key-stoning
        """

        # selected_corner = self.selected_corner
        # corner_direction = self.corner_direction
        # INTERACTION
        corner_keys = ['1', '2', '3', '4']
        move_keys = ['w', 'a', 's', 'd']

        KEY_STROKE = cv2.waitKey(1)
        if chr(KEY_STROKE & 255) in corner_keys:
            self.selected_corner = chr(KEY_STROKE & 255)
        if self.selected_corner != None and chr(KEY_STROKE & 255) in move_keys:
            self.corner_direction = chr(KEY_STROKE & 255)

            if self.selected_corner == '1':
                if self.corner_direction == 'd':
                    init_keystone[0] = init_keystone[0] - 1
                elif self.corner_direction == 'a':
                    init_keystone[0] = init_keystone[0] + 1
                elif self.corner_direction == 'w':
                    init_keystone[1] = init_keystone[1] + 1
                elif self.corner_direction == 's':
                    init_keystone[1] = init_keystone[1] - 1

            elif self.selected_corner == '2':
                if self.corner_direction == 'd':
                    init_keystone[2] = init_keystone[2] - 1
                elif self.corner_direction == 'a':
                    init_keystone[2] = init_keystone[2] + 1
                elif self.corner_direction == 'w':
                    init_keystone[3] = init_keystone[3] + 1
                elif self.corner_direction == 's':
                    init_keystone[3] = init_keystone[3] - 1

            elif self.selected_corner == '3':
                if self.corner_direction == 'd':
                    init_keystone[4] = init_keystone[4] - 1
                elif self.corner_direction == 'a':
                    init_keystone[4] = init_keystone[4] + 1
                elif self.corner_direction == 'w':
                    init_keystone[5] = init_keystone[5] + 1
                elif self.corner_direction == 's':
                    init_keystone[5] = init_keystone[5] - 1

            elif self.selected_corner == '4':
                if self.corner_direction == 'd':
                    init_keystone[6] = init_keystone[6] - 1
                elif self.corner_direction == 'a':
                    init_keystone[6] = init_keystone[6] + 1
                elif self.corner_direction == 'w':
                    init_keystone[7] = init_keystone[7] + 1
                elif self.corner_direction == 's':
                    init_keystone[7] = init_keystone[7] - 1
        #  saves to file
        elif chr(KEY_STROKE & 255) == 'k':
            self.save_keystone_to_file(
                self.listen_to_UI_interaction(init_keystone))

        ulx = init_keystone[0]
        uly = init_keystone[1]
        urx = init_keystone[2]
        ury = init_keystone[3]
        blx = init_keystone[4]
        bly = init_keystone[5]
        brx = init_keystone[6]
        bry = init_keystone[7]

        return np.asarray([(ulx, uly), (urx, ury), (blx, bly), (brx, bry)], dtype=np.float32)

    ##################################################

    def save_keystone_to_file(self, keystone_data_from_user_interaction):
        """
        saves keystone data from user interaction.

        Steps:
        saves an array of points to file

        """

        filePath = self.get_folder_path() + "keystone.txt"
        np.savetxt(filePath, keystone_data_from_user_interaction)
        print("[!] keystone points were saved in", filePath)

    ##################################################

    def keystone(self, video_resolution_x, video_resolution_y, keyStonePts):
        '''
        NOTE: Aspect ratio must be flipped
        so that aspectRat[0,1] will be aspectRat[1,0]
        '''

        # inverted screen ratio for np source array
        video_aspect_ratio = (video_resolution_y, video_resolution_x)
        # np source points array
        keystone_origin_points_array = np.float32(
            [
                [0, 0],
                [video_aspect_ratio[1], 0],
                [0, video_aspect_ratio[0]],
                [video_aspect_ratio[1], video_aspect_ratio[0]]
            ])
        # make the 4 pnts matrix perspective transformation
        transfromed_matrix = cv2.getPerspectiveTransform(
            keyStonePts, keystone_origin_points_array)

        return transfromed_matrix

    ##################################################

    def select_color_by_mean_value(self, mean_color_RGB):
        '''
        convert color to hsv for oclidian distance
        '''
        bgr_to_grayscale = cv2.cvtColor(mean_color_RGB, cv2.COLOR_BGR2GRAY)
        if int(bgr_to_grayscale) < 125:
            this_color = 0
        else:
            this_color = 1
        return this_color

    ##################################################

    def find_type_in_tags_array(self, cellColorsArray, tagsArray, mapArray,
                                grid_dimensions_x, grid_dimensions_y):
        """Get the right brick type out of the list of JSON types.

        Steps:
            - get the colors array from the scanners
            - get the JSON lists of type tags, mapping, rotations
            - parse the color data into an NP array of the table shape

        Args:
        Returns an array of found types
        """
        scan_results_array = []
        # create np colors array with table struct
        np_array_of_scanned_colors = np.reshape(
            cellColorsArray, (grid_dimensions_x * grid_dimensions_y, 16))

        # go through the results
        for this_16_bits in np_array_of_scanned_colors:
            result_tag = self.brick_rotation_check(
                this_16_bits, tagsArray, mapArray)
            # if no results were found
            if result_tag == None:
                result_tag = [-1, -1]
            # add a list of results to the array
            scan_results_array.append(result_tag)
        # finally, return this list to main program for UDP
        return scan_results_array

    ##################################################

    def brick_rotation_check(self, this_16_bits, tagsArray, mapArray):
        tags_array_counter = 0
        for this_tag in tagsArray:
            # if this 16 bits equal the tag as is
            if np.array_equal(this_16_bits, this_tag):
                return [tags_array_counter, 0]
            # convert list of 16 bits to 4x4 matrix for rotation
            brk_4x4 = np.reshape(this_16_bits, (4, 4))
            # rotate once
            brk_4x4_270 = np.reshape((np.rot90(brk_4x4)), 16)
            if np.array_equal(brk_4x4_270, this_tag):
                return [tags_array_counter, 1]
            # rotate once
            brk_4x4_180 = np.reshape((np.rot90(np.rot90(brk_4x4))), 16)
            if np.array_equal(brk_4x4_180, this_tag):
                return [tags_array_counter, 2]
            # rotate once
            brk_4x4_90 = np.reshape(
                (np.rot90(np.rot90(np.rot90(brk_4x4)))), 16)
            if np.array_equal(brk_4x4_90, this_tag):
                return [tags_array_counter, 3]
            else:
                # if no rotation was found go to next tag
                # in tag list
                tags_array_counter = tags_array_counter+1

    ##################################################

    #  method to create a geojson grid on init

    def gridMaker(self):
        print('\n', '______making GeoJson active and full table grids_______', '\n')
        # make full table grid
        top_left_lon = self.table_settings['objects']['cityscopy']['grid_full_table']['longitude']
        top_left_lat = self.table_settings['objects']['cityscopy']['grid_full_table']['latitude']
        nrows = self.table_settings['objects']['cityscopy']['grid_full_table']['nrows']
        ncols = self.table_settings['objects']['cityscopy']['grid_full_table']['ncols']
        rotation = self.table_settings['objects']['cityscopy']['grid_full_table']['rotation']
        cell_size = self.table_settings['objects']['cityscopy']['grid_full_table']['cellSize']
        crs_epsg = str(self.table_settings['objects']
                       ['cityscopy']['grid_full_table']['projection'])
        properties = {
            'id': [i for i in range(nrows*ncols)],
            'usage': [0 for i in range(nrows*ncols)],
            'height': [-100 for i in range(nrows*ncols)],
            'pop_density': [2 for i in range(nrows*ncols)]
        }
        results_grid = grid_geojson.Grid(top_left_lon, top_left_lat, rotation,
                                         crs_epsg, cell_size, nrows, ncols)
        grid_geo = results_grid.get_grid_geojson(properties)
        grid_interactive_area = json.dumps(grid_geo)
        API_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/" + \
            self.table_settings['header']['name'] + "/grid_full_table/"
        self.sendGrid(grid_interactive_area, API_ENDPOINT)

        # make interactive grid
        top_left_lon = self.table_settings['header']['spatial']['longitude']
        top_left_lat = self.table_settings['header']['spatial']['latitude']
        nrows = self.table_settings['header']['spatial']['nrows']
        ncols = self.table_settings['header']['spatial']['ncols']
        rotation = self.table_settings['header']['spatial']['rotation']
        cell_size = self.table_settings['header']['spatial']['cellSize']
        crs_epsg = str(self.table_settings['header']['spatial']['projection'])
        properties = {
            'id': [i for i in range(nrows*ncols)],
            'usage': [0 for i in range(nrows*ncols)],
            'height': [-100 for i in range(nrows*ncols)],
            'pop_density': [2 for i in range(nrows*ncols)]
        }
        results_grid = grid_geojson.Grid(top_left_lon, top_left_lat, rotation,
                                         crs_epsg, cell_size, nrows, ncols)
        grid_geo = results_grid.get_grid_geojson(properties)
        grid_interactive_area = json.dumps(grid_geo)
        API_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/" + \
            self.table_settings['header']['name'] + "/grid_interactive_area/"
        self.sendGrid(grid_interactive_area, API_ENDPOINT)
    ##################################################

    #  send geojson grid  to cityIO
    def sendGrid(self, data, API_ENDPOINT):
        req = requests.post(url=API_ENDPOINT, data=data)
        if req.status_code != 200:
            print("cityIO might be down. so sad.")
        print(req)

    ##################################################

    def udf_listener(self):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5000

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
        print("Starting UDP listener at:", UDP_IP, ' port: ', UDP_PORT, sock)

        while True:
            data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print('\n', data.decode())