# {{ CityScope Python Scanner }}
# Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com", "http://twitter.com/relno",
# https://github.com/RELNO]


##################################################

# CityScope Python Scanner - Modules
# Keystone, decode and send over UDP a 2d array
# of uniquely tagged LEGO array

##################################################

import socket
import os
import sys
import json
import time
from datetime import datetime
from datetime import timedelta
from datetime import date
import math
import numpy as np
import cv2
import requests

##################################################
# MAIN FUNCTIONS
##################################################


def scanner_function(multiprocess_shared_dict):
    # define the table params
    grid_dimensions_x = table_settings['header']['spatial']['nrows']
    grid_dimensions_y = table_settings['header']['spatial']['ncols']

    array_of_tags_from_json = np_string_tags(
        table_settings['objects']['cityscopy']['tags'])

    array_of_maps_form_json = table_settings['header']['mapping']['type']
    array_of_rotations_form_json = table_settings['header']['mapping']['rotation']

    # load the initial keystone data from file
    keystone_points_array = np.loadtxt(
        get_folder_path()+'keystone.txt', dtype=np.float32)

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
    cv2.namedWindow('sliders_gui_window', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('sliders_gui_window', 800, 400)
    cv2.moveWindow('sliders_gui_window', 550, 100)

    # make the sliders GUI
    create_user_intreface(
        keystone_points_array, video_resolution_x, video_resolution_y)

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
    array_of_scanner_points_locations = get_scanner_pixel_coordinates(
        grid_dimensions_x, grid_dimensions_y, video_resolution_x,
        video_resolution_y, scanner_square_size)

   ##################################################
   ###################MAIN LOOP######################
   ##################################################

   # run the video loop forever
    while True:

        # get a new matrix transformation every frame
        KEY_STONE_DATA = keystone(
            video_resolution_x, video_resolution_y, listen_to_UI_interaction())

        # zero an array to collect the scanners
        CELL_COLORS_ARRAY = []

        # read video frames
        _, THIS_FRAME = video_capture.read()
        # mirror camera
        if table_settings['objects']['cityscopy']['mirror_cam'] is 1:
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
            scannerCol = select_color_by_mean_value(mean_color_RGB)

            # add colors to array for type analysis
            CELL_COLORS_ARRAY.append(scannerCol)

            # get color from dict
            thisColor = DICTIONARY_COLORS[scannerCol]

            # ? only draw vis if settings has 1 in gui
            if table_settings['objects']['cityscopy']['gui'] is 1:
                # draw rects with frame colored by range result
                cv2.rectangle(DISTORTED_VIDEO_STREAM,
                              (x+scanner_reduction,
                               y+scanner_reduction),
                              (x_red,
                               y_red),
                              thisColor, 1)
                '''
                # put grid text
                cv2.putText(DISTORTED_VIDEO_STREAM, str(count),
                            (x_red,
                             y_red), cv2.FONT_HERSHEY_DUPLEX,
                            .3, (0, 0, 255), 1)
                '''
            # cell counter
            count = count + 1

        # reduce unnecessary scan analysis and sending by comparing
        # the list of scanned cells to an old one
        if CELL_COLORS_ARRAY != OLD_CELL_COLORS_ARRAY:

            # send array to method for checking types
            TYPES_LIST = find_type_in_tags_array(
                CELL_COLORS_ARRAY, array_of_tags_from_json,
                array_of_maps_form_json,
                grid_dimensions_x, grid_dimensions_y)

            # match the two
            OLD_CELL_COLORS_ARRAY = CELL_COLORS_ARRAY

            # [!] Store the type list results in the multiprocess_shared_dict
            multiprocess_shared_dict['scan'] = TYPES_LIST

        else:
                # else skip this
            pass

        if table_settings['objects']['cityscopy']['gui'] is 1:
            # add type and pos text
            '''
            cv2.putText(DISTORTED_VIDEO_STREAM, 'Types: ' + str(TYPES_LIST),
                        (50, 50), cv2.FONT_HERSHEY_DUPLEX,
                        0.5, (0, 0, 0), 1)
            '''
            # draw the video to screen
            cv2.imshow("scanner_gui_window", DISTORTED_VIDEO_STREAM)

    # close opencv
    video_capture.release()
    cv2.destroyAllWindows()

##################################################


def get_scanner_pixel_coordinates(grid_dimensions_x, grid_dimensions_y, video_res_x, video_res_y, scanner_square_size):
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
    cells_gap = table_settings['objects']['cityscopy']['cell_gap']

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


def np_string_tags(json_data):
    # return each item for this field
    d = []
    for i in json_data:
        d.append(np.array([int(ch) for ch in i]))
    return d

##################################################
##################################################
# HELPER FUNCTIONS
##################################################
##################################################


def create_data_json(multiprocess_shared_dict):

        # load info from json file
    PATH = 'cityio.json'
    table_settings = parse_json_file('table', PATH)
    SEND_INTERVAL = table_settings['objects']['cityscopy']['interval']
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
                json_struct = table_settings
                json_struct['grid'] = scan_results

                if table_settings['objects']['cityscopy']['cityio'] is 1:
                    cityIO_json = json.dumps(json_struct)
                    #! print('sending to cityIO...')
                    send_json_to_cityIO(cityIO_json)
                else:
                    #! print('sending UDP...')
                    send_json_to_UDP(scan_results)

            except Exception as e:
                print(e)

            # match the two grid after send
            old_scan_results = scan_results
            last_sent = datetime.now()

            # debug print
            print('\n', 'sent at: ', datetime.now())

##################################################

##################################################


def send_json_to_cityIO(cityIO_json):
    # defining the api-endpoint
    API_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/" + \
        table_settings['header']['name']
    # sending post request and saving response as response object
    req = requests.post(url=API_ENDPOINT, data=cityIO_json)
    print(req)

##################################################


def send_json_to_UDP(scan_results):
    # defining the udp endpoint
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(str(scan_results).encode('utf-8'), (UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)


##################################################

def parse_json_file(field, PATH):
    """
    get data from JSON settings files.

    Steps:
    - opens file
    - checks if field has objects longer than one char [such as the 'tags' field]
    - if so, converts them to numpy arrays

    Args:

    Returns the desired filed
    """

    print('getting setting for:', field)

    # init array for json fields
    c = get_folder_path()+PATH
    # open json file
    with open(c) as d:
        data = json.load(d)
    return(data[field])

##################################################


def get_folder_path():
    """
    gets the local folder
    return is as a string with '/' at the ednd
    """
    loc = str(os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))) + '/'
    return loc

##################################################


def create_user_intreface(keystone_points_array, video_resolution_x, video_resolution_y):
    """
    Creates user interface and keystone sliders

    Steps:
    makes a list of sliders for interaction

    Args:

    Returns none
    """

    cv2.createTrackbar('Upper Left X', 'sliders_gui_window',
                       -video_resolution_x, video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Upper Left Y', 'sliders_gui_window',
                       -video_resolution_y, video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Upper Right X', 'sliders_gui_window',
                       -video_resolution_x, video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Upper Right Y', 'sliders_gui_window',
                       -video_resolution_y, video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Bottom Left X', 'sliders_gui_window',
                       -video_resolution_x, video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Bottom Left Y', 'sliders_gui_window',
                       -video_resolution_y, video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Bottom Right X', 'sliders_gui_window',
                       -video_resolution_x, video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Bottom Right Y', 'sliders_gui_window',
                       -video_resolution_y, video_resolution_y, dont_return_on_ui)

    # now set the sliders position based on the saved values
    cv2.setTrackbarPos('Upper Left X', 'sliders_gui_window',
                       keystone_points_array[0][0])
    cv2.setTrackbarPos('Upper Left Y', 'sliders_gui_window',
                       keystone_points_array[0][1])
    cv2.setTrackbarPos('Upper Right X', 'sliders_gui_window',
                       keystone_points_array[1][0])
    cv2.setTrackbarPos('Upper Right Y', 'sliders_gui_window',
                       keystone_points_array[1][1])
    cv2.setTrackbarPos('Bottom Left X', 'sliders_gui_window',
                       keystone_points_array[2][0])
    cv2.setTrackbarPos('Bottom Left Y', 'sliders_gui_window',
                       keystone_points_array[2][1])
    cv2.setTrackbarPos('Bottom Right X', 'sliders_gui_window',
                       keystone_points_array[3][0])
    cv2.setTrackbarPos('Bottom Right Y', 'sliders_gui_window',
                       keystone_points_array[3][1])


def dont_return_on_ui(event):
    pass


def listen_to_UI_interaction():
    """
    listens to user interaction.

    Steps:
    listen to a list of sliders

    Args:

    Returns 4x2 array of points location for key-stoning
    """

    ulx = cv2.getTrackbarPos('Upper Left X', 'sliders_gui_window')
    uly = cv2.getTrackbarPos('Upper Left Y', 'sliders_gui_window')
    urx = cv2.getTrackbarPos('Upper Right X', 'sliders_gui_window')
    ury = cv2.getTrackbarPos('Upper Right Y', 'sliders_gui_window')
    blx = cv2.getTrackbarPos('Bottom Left X', 'sliders_gui_window')
    bly = cv2.getTrackbarPos('Bottom Left Y', 'sliders_gui_window')
    brx = cv2.getTrackbarPos('Bottom Right X', 'sliders_gui_window')
    bry = cv2.getTrackbarPos('Bottom Right Y', 'sliders_gui_window')

    global selected_corner
    global corner_direction
    # INTERACTION
    corner_keys = ['1', '2', '3', '4']
    move_keys = ['w', 'a', 's', 'd']

    KEY_STROKE = cv2.waitKey(1)
    #  saves to file
    if chr(KEY_STROKE & 255) == 'k':
        save_keystone_to_file(
            listen_to_UI_interaction())
    elif chr(KEY_STROKE & 255) in corner_keys:
        selected_corner = chr(KEY_STROKE & 255)
    if selected_corner != None and chr(KEY_STROKE & 255) in move_keys:
        corner_direction = chr(KEY_STROKE & 255)

        print(selected_corner, corner_direction)

        if selected_corner == '1':
            if corner_direction == 'd':
                ulx = ulx - 1
            elif corner_direction == 'a':
                ulx = ulx + 1
            elif corner_direction == 'w':
                uly = uly + 1
            elif corner_direction == 's':
                uly = uly - 1

        elif selected_corner == '2':
            if corner_direction == 'd':
                urx = urx - 1
            elif corner_direction == 'a':
                urx = urx + 1
            elif corner_direction == 'w':
                ury = ury + 1
            elif corner_direction == 's':
                ury = ury - 1

        elif selected_corner == '3':
            if corner_direction == 'd':
                blx = blx - 1
            elif corner_direction == 'a':
                blx = blx + 1
            elif corner_direction == 'w':
                bly = bly + 1
            elif corner_direction == 's':
                bly = bly - 1

        elif selected_corner == '4':
            if corner_direction == 'd':
                brx = brx - 1
            elif corner_direction == 'a':
                brx = brx + 1
            elif corner_direction == 'w':
                bry = bry + 1
            elif corner_direction == 's':
                bry = bry - 1

        # now set the sliders position based on the saved values
    cv2.setTrackbarPos('Upper Left X', 'sliders_gui_window', ulx)
    cv2.setTrackbarPos('Upper Left Y', 'sliders_gui_window', uly)
    cv2.setTrackbarPos('Upper Right X', 'sliders_gui_window', urx)
    cv2.setTrackbarPos('Upper Right Y', 'sliders_gui_window', ury)
    cv2.setTrackbarPos('Bottom Left X', 'sliders_gui_window', blx)
    cv2.setTrackbarPos('Bottom Left Y', 'sliders_gui_window', bly)
    cv2.setTrackbarPos('Bottom Right X', 'sliders_gui_window', brx)
    cv2.setTrackbarPos('Bottom Right Y', 'sliders_gui_window', bry)

    return np.asarray([(ulx, uly), (urx, ury), (blx, bly), (brx, bry)], dtype=np.float32)

##################################################


def save_keystone_to_file(keystone_data_from_user_interaction):
    """
    saves keystone data from user interaction.

    Steps:
    saves an array of points to file

    """

    filePath = get_folder_path() + "keystone.txt"
    np.savetxt(filePath, keystone_data_from_user_interaction)
    print("[!] keystone points were saved in", filePath)

##################################################


def keystone(video_resolution_x, video_resolution_y, keyStonePts):
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


def select_color_by_mean_value(mean_color_RGB):
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


def find_type_in_tags_array(cellColorsArray, tagsArray, mapArray,
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
        result_tag = brick_rotation_check(this_16_bits, tagsArray, mapArray)
        # if no results were found
        if result_tag == None:
            result_tag = [-1, -1]
        # add a list of results to the array
        scan_results_array.append(result_tag)
    # finally, return this list to main program for UDP
    return scan_results_array

##################################################


def brick_rotation_check(this_16_bits, tagsArray, mapArray):
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
        brk_4x4_90 = np.reshape((np.rot90(np.rot90(np.rot90(brk_4x4)))), 16)
        if np.array_equal(brk_4x4_90, this_tag):
            return [tags_array_counter, 3]
        else:
            # if no rotation was found go to next tag
            # in tag list
            tags_array_counter = tags_array_counter+1


##################################################
# load info from json file
PATH = 'cityio.json'
table_settings = parse_json_file('table', PATH)

#! ugly way to store keystroke vals between loops.
selected_corner = None
corner_direction = None
