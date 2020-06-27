'''
>>>>>>>>>>>>> Starting CityScope Scanner >>>>>>>>>>>>


                    |||||||||||
                    |||||||||||
                            |||
                            |||
                            |||
                    |||      ||||||||||||
                    |||      ||||||||||||
                    |||               |||
                    |||               |||
                    |||               |||
                    ||||||||||||      |||
                    ||||||||||||      |||


>>>>>>>>>>>>> Starting CityScope Scanner >>>>>>>>>>>>

Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

"@context": "https://github.com/CityScope/", "@type": "Person", "address": {
"@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
"Cambridge", "addressRegion": "MA",},
"jobTitle": "Research Scientist", "name": "Ariel Noyman",
"alumniOf": "MIT", "url": "http://arielnoyman.com",
"https://www.linkedin.com/", "http://twitter.com/relno",
https://github.com/RELNO]


##################################################
CityScope Python Scanner
Keystone, decode and send over UDP/HTTTP a 2d array
of uniquely tagged LEGO array
##################################################
'''


import requests
import cv2
import numpy as np
from datetime import timedelta
from datetime import datetime
import time
import json
import os
import socket
from multiprocessing import Process, Manager
import random


class Cityscopy:
    '''sacnner for CityScope'''

    ##################################################

    def __init__(self, path):
        '''init function '''
        # load info from json file
        self.SETTINGS_PATH = path
        # get the table settings. This is used bu many metohds
        self.table_settings = self.parse_json_file('cityscopy')
        print('getting settings for CityScopy...')

        # init corners variables
        self.selected_corner = None
        self.corner_direction = None

        # init keystone variables
        self.FRAME = None
        self.POINT_INDEX = None
        self.POINTS = None
        self.MOUSE_POSITION = None

    ##################################################

    def scan(self):

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
        # get init keystones
        self.init_keystone = self.get_init_keystone()
        # define the table params
        grid_dimensions_x = self.table_settings['nrows']
        grid_dimensions_y = self.table_settings['ncols']
        array_of_tags_from_json = self.np_string_tags(
            self.table_settings['tags'])

        array_of_maps_form_json = self.table_settings['type']

        # init type list array
        TYPES_LIST = []

        # holder of old cell colors array to check for new scan
        OLD_CELL_COLORS_ARRAY = []

        # serial num of camera, to switch between cameras
        camPos = self.table_settings['camId']
        # try from a device 1 in list, not default webcam
        video_capture = cv2.VideoCapture(camPos)
        time.sleep(1)

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
            keystone_data = self.transfrom_matrix(
                video_resolution_x, video_resolution_y, self.listen_to_UI_interaction(self.init_keystone))

            # zero an array to collect the scanners
            CELL_COLORS_ARRAY = []

            # read video frames
            RET, this_frame = video_capture.read()
            if RET is False:
                pass
            # else if camera capture is ok
            else:
                # mirror camera
                if self.table_settings['mirror_cam'] is True:
                    this_frame = cv2.flip(this_frame, 1)
                    # warp the video based on keystone info
                keystoned_video = cv2.warpPerspective(
                    this_frame, keystone_data, (video_resolution_x, video_resolution_y))

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

                this_scanner_size = keystoned_video[y+scanner_reduction:y_red,
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
                if self.table_settings['gui'] is True:
                    # draw rects with frame colored by range result
                    cv2.rectangle(keystoned_video,
                                  (x+scanner_reduction,
                                   y+scanner_reduction),
                                  (x_red, y_red),
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

            if self.table_settings['gui'] is True:
                # draw arrow to interaction area
                self.ui_selected_corner(
                    video_resolution_x, video_resolution_y, keystoned_video)
                # draw the video to screen
                cv2.imshow("scanner_gui_window", keystoned_video)

        # close opencv
        video_capture.release()
        cv2.destroyAllWindows()

    ##################################################

    def ui_selected_corner(self, x, y, vid):
        """prints text on video window"""

        mid = (int(x/2), int(y/2))
        if self.selected_corner is None:
            # font
            font = cv2.FONT_HERSHEY_SIMPLEX

            # fontScale
            fontScale = 1.2
            # Blue color in BGR
            color = (0, 0, 255)
            # Line thickness of 2 px
            thickness = 2
            cv2.putText(vid, 'select corners using 1,2,3,4 and move using A/W/S/D',
                        (5, int(y/2)), font,
                        fontScale, color, thickness, cv2.LINE_AA)
        else:
            case = {
                '1': [(0, 0), mid],
                '2':  [(x, 0), mid],
                '3':  [(0, y), mid],
                '4':  [(x, y), mid],
            }

            # print(type(self.selected_corner))
            cv2.arrowedLine(
                vid, case[self.selected_corner][0],
                case[self.selected_corner][1],
                (0, 0, 255), 2)

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
        cells_gap = self.table_settings['cell_gap']

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
        self.table_settings = self.parse_json_file('cityscopy')
        SEND_INTERVAL = self.table_settings['interval']
        # initial dummy value for old grid
        old_scan_results = [-1]
        SEND_INTERVAL = timedelta(milliseconds=SEND_INTERVAL)
        last_sent = datetime.now()
        while True:
            scan_results = multiprocess_shared_dict['scan']
            from_last_sent = datetime.now() - last_sent
            if (scan_results != old_scan_results) and from_last_sent > SEND_INTERVAL:
                try:
                    if self.table_settings['cityio'] is True:
                        self.send_json_to_cityIO(json.dumps(scan_results))
                    else:
                        self.send_json_to_UDP(scan_results)
                except Exception as ERR:
                    print(ERR)
                # match the two grid after send
                old_scan_results = scan_results
                last_sent = datetime.now()

                # debug print
                print('\n', 'CityScopy grid sent at:', datetime.now())

    ##################################################

    def send_json_to_cityIO(self, cityIO_json):
        '''
        sends the grid to cityIO 
        '''
        # defining the api-endpoint
        API_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/" + \
            self.table_settings['cityscope_project_name'] + "/grid/"
        # sending post request and saving response as response object
        req = requests.post(url=API_ENDPOINT, data=cityIO_json)
        if req.status_code != 200:
            print("cityIO might be down. so sad.")
        print("sending grid to", API_ENDPOINT,  req)

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
            # reset selected corner
            self.selected_corner = None
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

    def transfrom_matrix(self, video_resolution_x, video_resolution_y, keyStonePts):
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

    def udp_listener(self):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5000

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
        print("Starting UDP listener at:", UDP_IP, ' port: ', UDP_PORT, sock)

        while True:
            data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print('\n', data.decode())

    ##################################################

    def keystone(self):
        # file path to save
        self.KEYSTONE_PATH = self.get_folder_path() + '/'+"keystone.txt"
        print('keystone path:', self.KEYSTONE_PATH)

        # serial num of camera, to switch between cameras
        camPos = self.table_settings['camId']
        # try from a device 1 in list, not default webcam
        WEBCAM = cv2.VideoCapture(camPos)
        time.sleep(1)

        # video winodw
        cv2.namedWindow('canvas', cv2.WINDOW_NORMAL)

        # top left, top right, bottom left, bottom right
        self.POINTS = [(0, 0), (0, 0), (0, 0), (0, 0)]
        self.POINT_INDEX = 0
        self.MOUSE_POSITION = (0, 0)

        def selectFourPoints():
            # let users select 4 points on WEBCAM GUI
            print("select 4 points, by double clicking on each of them in the order: \n\
            up right, up left, bottom right, bottom left.")

            # loop until 4 clicks
            while self.POINT_INDEX != 4:
                key = cv2.waitKey(20) & 0xFF
                if key == 27:
                    return False
                # wait for clicks
                cv2.setMouseCallback('canvas', save_this_point)
                # read the WEBCAM frames
                _, self.FRAME = WEBCAM.read()
                if self.table_settings['mirror_cam'] is True:
                    self.FRAME = cv2.flip(self.FRAME, 1)
                # draw mouse pos
                cv2.circle(self.FRAME, self.MOUSE_POSITION, 10, (0, 0, 255), 1)
                cv2.circle(self.FRAME, self.MOUSE_POSITION, 1, (0, 0, 255), 2)
                # draw clicked points
                for thisPnt in self.POINTS:
                    cv2.circle(self.FRAME, thisPnt, 10, (255, 0, 0), 1)
                # show the video
                cv2.imshow('canvas', self.FRAME)
            # when done selecting 4 pnts return
            return True

        def save_this_point(event, x, y, flags, param):
            # mouse callback function
            if event == cv2.EVENT_MOUSEMOVE:
                self.MOUSE_POSITION = (x, y)
            elif event == cv2.EVENT_LBUTTONUP:
                # draw a ref. circle
                print('point  # ', self.POINT_INDEX, (x, y))
                # save this point to the array pts
                self.POINTS[self.POINT_INDEX] = (x, y)
                self.POINT_INDEX = self.POINT_INDEX + 1
        # checks if finished selecting the 4 corners
        if selectFourPoints():
            np.savetxt(self.KEYSTONE_PATH, self.POINTS)
            print("keystone initial points were saved")

        WEBCAM.release()
        cv2.destroyAllWindows()
