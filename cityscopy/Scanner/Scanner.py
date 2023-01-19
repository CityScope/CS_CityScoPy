'''
##################################################
CityScope Python Scanner
Keystone, decode and send over UDP/HTTTP a 2d array
of uniquely tagged LEGO array
##################################################
'''


import cv2
import numpy as np
import time
from multiprocessing import Process, Manager
from ..helpers import parse_json_file, create_data_json, get_init_keystone, np_string_tags, get_folder_path
from ..ui_tools import listen_to_UI_interaction, ui_selected_corner
import json


class Scanner:

    '''Keystone for cityscopy'''

    def __init__(self, CITYSCOPE_PRJ_NAME):

        # load settings from json file
        self.table_settings = parse_json_file(
            CITYSCOPE_PRJ_NAME)
        self.GEOGRIDDATA = self.load_GEOGRIDDATA()
        self. CITYSCOPE_PRJ_NAME = CITYSCOPE_PRJ_NAME  # table name
        self.CITYIO_URL = self.table_settings['CITYIO_API_URL']
        self.keystone_points_list = self.table_settings['keystone_points_list']

        # init corners variables
        self.selected_corner = None
        self.corner_direction = None
        # init keystone variables
        self.FRAME = None
        self.POINT_INDEX = None
        self.POINTS = None
        self.MOUSE_POSITION = None
        # init distance [px] variable
        self.distance_value = 5

    ##################################################
    def load_GEOGRIDDATA(self):
        # read to memory the the GEOGRIDDATA json file
        with open(get_folder_path() + 'settings/GEOGRIDDATA.json') as d:
            print('GEOGRIDDATA.json loaded to memory')
            return json.load(d)

    ##################################################
    def scan(self):
        # define global list manager
        MANAGER = Manager()
        # create shared global list to work with both processes
        self.multiprocess_shared_dict = MANAGER.dict()

        # init a dict with some data to be shared among process
        self.multiprocess_shared_dict['scan'] = [[-1, -1]]

        # defines a multiprocess for sending the data
        self.process_send_packet = Process(target=create_data_json,
                                           args=([self, self.multiprocess_shared_dict]))
        # start porcess
        self.process_send_packet.start()
        # start camera on main thread due to multiprocces issue
        self.scanner_function(self.multiprocess_shared_dict)

    ##################################################

    def scanner_function(self, multiprocess_shared_dict):

        # get init keystones
        self.init_keystone = get_init_keystone(self)
        # define the table params
        grid_dimensions_x = self.table_settings['ncols']
        grid_dimensions_y = self.table_settings['nrows']

        # go over the 'types' object in the json file
        # and create a list of tags strings from the
        # 'cityscopy_pattern' field in this
        # table's json settings file
        binary_tags_list = []
        array_of_maps_form_json = []
        for i in self.table_settings['types']:
            binary_tags_list.append(
                self.table_settings['types'][i]['cityscopy_pattern'])
            array_of_maps_form_json.append(
                self.table_settings['types'][i]['name'])

        # convert the list of binary tags to a list of np strings
        array_of_tags_from_json = np_string_tags(self, binary_tags_list)

        cell_gap = self.table_settings['cell_gap']

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
            grid_dimensions_x, grid_dimensions_y, cell_gap, video_resolution_x,
            video_resolution_y, scanner_square_size)

        # resize video resolution if cell gaps are used:
        video_resolution_x = video_resolution_x + grid_dimensions_x * cell_gap
        video_resolution_y = video_resolution_y + grid_dimensions_y * cell_gap

    # run the video loop forever
        while True:
            # get a new matrix transformation every frame
            keystone_data = self.transform_matrix(
                video_resolution_x, video_resolution_y, listen_to_UI_interaction(self, self.init_keystone))

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
                ui_selected_corner(self,
                                   video_resolution_x, video_resolution_y, keystoned_video)
                # draw the video to screen
                cv2.imshow("scanner_gui_window", keystoned_video)

    ##################################################

    def get_scanner_pixel_coordinates(self, grid_dimensions_x, grid_dimensions_y, cell_gap, video_res_x, video_res_y, scanner_square_size):
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

        # create the 4x4 sub grid cells
        for y in range(0, grid_dimensions_y):
            for x in range(0, grid_dimensions_x):

                x_positions = x * (scanner_square_size*4+cell_gap)
                y_positions = y * (scanner_square_size*4+cell_gap)

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

    def transform_matrix(self, video_resolution_x, video_resolution_y, keyStonePts):
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
