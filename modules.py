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

# imports packages
import socket
import json
import time
import math
import numpy as np
import cv2


##################################################


def parse_json_file(field):
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
    json_field = []

    # open json file
    with open('DATA/tags.json') as json_data:

        jd = json.load(json_data)
    # return each item for this field
    for i in jd[field]:
        # if item length is more than 1 [tags]

        if field == 'tags':
            # parse this item as np array
            json_field.append(np.array([int(ch) for ch in i]))
        else:
            # otherwise send it as is
            json_field.append(i)
    return json_field

##################################################


def create_user_intreface(keystone_points_array, video_resolution_x, video_resolution_y):
    """
    Creates user interface and GUI.

    Steps:
    makes a list of sliders for interaction

    Args:

    Returns none
    """

    cv2.createTrackbar('Upper Left X', 'CityScopeScanner',
                       keystone_points_array[0][0], video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Upper Left Y', 'CityScopeScanner',
                       keystone_points_array[0][1], video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Upper Right X', 'CityScopeScanner',
                       keystone_points_array[1][0], video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Upper Right Y', 'CityScopeScanner',
                       keystone_points_array[1][1], video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Bottom Left X', 'CityScopeScanner',
                       keystone_points_array[2][0], video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Bottom Left Y', 'CityScopeScanner',
                       keystone_points_array[2][1], video_resolution_y, dont_return_on_ui)
    cv2.createTrackbar('Bottom Right X', 'CityScopeScanner',
                       keystone_points_array[3][0], video_resolution_x, dont_return_on_ui)
    cv2.createTrackbar('Bottom Right Y', 'CityScopeScanner',
                       keystone_points_array[3][1], video_resolution_y, dont_return_on_ui)


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

    ulx = cv2.getTrackbarPos('Upper Left X', 'CityScopeScanner')
    uly = cv2.getTrackbarPos('Upper Left Y', 'CityScopeScanner')
    urx = cv2.getTrackbarPos('Upper Right X', 'CityScopeScanner')
    ury = cv2.getTrackbarPos('Upper Right Y', 'CityScopeScanner')
    blx = cv2.getTrackbarPos('Bottom Left X', 'CityScopeScanner')
    bly = cv2.getTrackbarPos('Bottom Left Y', 'CityScopeScanner')
    brx = cv2.getTrackbarPos('Bottom Right X', 'CityScopeScanner')
    bry = cv2.getTrackbarPos('Bottom Right Y', 'CityScopeScanner')
    return np.asarray([(ulx, uly), (urx, ury), (blx, bly), (brx, bry)], dtype=np.float32)

##################################################


def save_keystone_to_file(keystone_data_from_user_interaction):
    """
    saves keystone data from user interaction.

    Steps:
    saves an array of points to file

    """

    filePath = "DATA/keystone.txt"
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


def find_type_in_tags_array(cellColorsArray, tagsArray, mapArray, rotationArray):
    """Get the right brick type out of the list of JSON types.

    Steps:
        - get the colors array from the scanners
        - get the JSON lists of type tags, mapping, rotations
        - parse the color data into an NP array of the table shape

    Args:
    Returns an array of found types in [T{ype},R{otation}] format
    """
    typesArray = []
    # create np colors array with table struct
    npColsArr = np.reshape(cellColorsArray, (18, 9))

    # go through the results
    for thisResult in npColsArr:
        # look for this result in tags array from JSON
        # and return only where TRUE appears in results
        whichTag = np.where([(thisResult == tag).all()
                             for tag in tagsArray])[0]
        # if this tag is not found return -1
        if whichTag.size == 0:
            typesArray.append([-1, -1])
        # else return the tag location in the list
        else:
            this_tag = int(whichTag[0])
            type_number = mapArray[this_tag]
            rotation_value = rotationArray[this_tag]

            typesArray.append([int(type_number), int(rotation_value)])
    # finally, return this list to main program for UDP
    return typesArray


##################################################


def get_scanner_pixel_coordinates(video_res_x, scale, scanner_square_size):
    """Creates list of pixel coordinates for scanner.

    Steps:
        - Determine virtual points on the grid that will be the centers of blocks.
        - Transform those virtual points pixel coordinates and expand them into 3x3 clusters of pixel points

    Args:

    Returns list of[x, y] pixel coordinates for scanner to read.
    """

    # Point looks like [x, y]
    virtual_points = [

        [0, 0],
        [2, 0],
        [5, 0],
        [7, 0],
        [10, 0],
        [12, 0],

        [0, 3],
        [2, 3],
        [5, 3],
        [7, 3],
        [10, 3],
        [12, 3],

        [0, 6],
        [2, 6],
        [5, 6],
        [7, 6],
        [10, 6],
        [12, 6]
    ]

    # call helper function to find location of each point
    scanner_locations_array = transform_virtual_points_to_pixels(
        virtual_points, scale, scanner_square_size)
    return scanner_locations_array

##################################################


def transform_virtual_points_to_pixels(points, scale, scanner_square_size):
    """
    Transforms virtual[x, y] coordinate pairs to pixel representations
    for scanner.

    Returns list of[x, y] pixel coordinates for scanner.
    """
    pixel_coordinates_list = []
    for [x, y] in points:
        scaled_x = x*scale
        scaled_y = y*scale
        for i in range(0, 3):
            for j in range(0, 3):
                pixel_coordinates_list.append(
                    [scaled_x + (i*scanner_square_size)
                     + int(scale/4),

                     scaled_y + (j*scanner_square_size)
                     + int(scale/4)
                     ])

    return pixel_coordinates_list

##################################################


def slider_listener(multiprocess_shared_dict):
    while True:
        """
        Listen to physical slider input and return a [0-1] value
        """
        slider = "{0:.2f}".format(math.sin(time.time()/5) ** 2)
        multiprocess_shared_dict['slider'] = str(slider)


##################################################


def send_over_UDP(multiprocess_shared_dict):
    while True:
        print(multiprocess_shared_dict)

    # UDP_IP = "127.0.0.1"
    # UDP_PORT = 5005

    # pre_json = '{"grid":'.encode("utf-8")
    # # convert to string and encode the packet
    # types_json = str(TYPES_LIST).encode("utf-8")
    # slider_json = str(SLIDER).encode("utf-8")
    # post_udp = "}".encode("utf-8")

    # udp_message = pre_json + types_json + \
    #     ',"slider":['.encode("utf-8") + \
    #     slider_json + ']'.encode("utf-8") +\
    #     post_udp

    # # debug
    # print('\n', "UDP:", udp_message)

    # # open UDP socket
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.sendto(udp_message, (UDP_IP, UDP_PORT))


##################################################


def scanner_function(multiprocess_shared_dict):

    print('d')
    TYPES_LIST = []

    # holder of old cell colors array to check for new scan
    OLD_CELL_COLORS_ARRAY = []

    # define the grid size
    grid_dimensions_x = 6
    grid_dimensions_y = 3

    # load json file
    array_of_tags_from_json = parse_json_file('tags')
    array_of_maps_form_json = parse_json_file('map')
    array_of_rotations_form_json = parse_json_file('rotation')

    # load the initial keystone data from file
    keystone_points_array = np.loadtxt('DATA/keystone.txt', dtype=np.float32)

    # define the video stream
    try:
        # try from a device 1 in list, not default webcam
        video_capture = cv2.VideoCapture(1)
        # if not exist, use device 0
        if not video_capture.isOpened():
            video_capture = cv2.VideoCapture(0)
    finally:
        print(video_capture)

    # get video resolution from webcam
    video_resolution_x = int(video_capture.get(3))
    video_resolution_y = int(video_capture.get(4))

    # number of overall modules in the table x dimension
    number_of_table_modules = 14

    # scale of one module in actual pixel size over the x axis
    one_module_scale = int(video_resolution_x/number_of_table_modules)

    # define the size for each scanner
    scanner_square_size = int(one_module_scale/2)

    # define the video window
    cv2.namedWindow('CityScopeScanner', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('CityScopeScanner', 1000, 1000)

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

    # create the location  array of scanners
    array_of_scanner_points_locations = get_scanner_pixel_coordinates(
        video_resolution_x, one_module_scale,  scanner_square_size)

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

        # warp the video based on keystone info
        DISTORTED_VIDEO_STREAM = cv2.warpPerspective(
            THIS_FRAME, KEY_STONE_DATA, (video_resolution_x, video_resolution_y))

        # run through locations list and make scanners
        for this_scanner_location in array_of_scanner_points_locations:

            # set x and y from locations array
            x = this_scanner_location[0]
            y = this_scanner_location[1]

            # use this to control reduction of scanner size
            this_scanner_max_dimension = int(scanner_square_size/2)

            # set scanner crop box size and position
            # at x,y + crop box size
            this_scanner_size = DISTORTED_VIDEO_STREAM[y:y + this_scanner_max_dimension,
                                                       x:x + this_scanner_max_dimension]

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

            # draw rects with frame colored by range result
            cv2.rectangle(DISTORTED_VIDEO_STREAM, (x, y),
                          (x+this_scanner_max_dimension,
                           y+this_scanner_max_dimension),
                          thisColor, 3)

        # reduce unnecessary scan analysis and sending by comparing
        # the list of scanned cells to an old one
        if CELL_COLORS_ARRAY != OLD_CELL_COLORS_ARRAY:

            # send array to check types
            TYPES_LIST = find_type_in_tags_array(
                CELL_COLORS_ARRAY, array_of_tags_from_json,
                array_of_maps_form_json,
                array_of_rotations_form_json)

            # match the two
            OLD_CELL_COLORS_ARRAY = CELL_COLORS_ARRAY

            # [!] Store the type list results in the multiprocess_shared_dict
            multiprocess_shared_dict['grid'] = str(TYPES_LIST)

        else:
            # else skip this
            pass

        # add type and pos text
        cv2.putText(DISTORTED_VIDEO_STREAM, 'Types: ' + str(TYPES_LIST),
                    (50, 50), cv2.FONT_HERSHEY_DUPLEX,
                    0.5, (0, 0, 0), 1)

        # draw the video to screen
        cv2.imshow("CityScopeScanner", DISTORTED_VIDEO_STREAM)

        # INTERACTION
        # break video loop by pressing ESC
        KEY_STROKE = cv2.waitKey(1)
        if chr(KEY_STROKE & 255) == 'q':
            # break the loop
            break

        # # saves to file
        elif chr(KEY_STROKE & 255) == 's':
            save_keystone_to_file(
                listen_to_UI_interaction())

    # close opencv
    video_capture.release()
    cv2.destroyAllWindows()
