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
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


##################################################

# CityScope Python Scanner
# Keystone, decode and send over UDP a 2d array
# of uniquely tagged LEGO array

##################################################

# raise SystemExit(0)

import cv2
import numpy as np
import modules

'''
TO REMOVE LATER
'''
import random
import time
import math

##################################################
# define the grid size
grid_dimensions_x = 6
grid_dimensions_y = 3

# flag for camera
camera_flag = True

# load json file
array_of_tags_from_json = modules.parse_json_file('tags')
array_of_maps_form_json = modules.parse_json_file('map')
array_of_rotations_form_json = modules.parse_json_file('rotation')

# load the initial keystone data from file
keystone_points_array = np.loadtxt('DATA/keystone.txt', dtype=np.float32)

# define the video stream
try:
    # try from a device 1 in list, not default webcam
    video_capture = cv2.VideoCapture(1)
    # if not exist, use device 0
    if not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)
    else:
        camera_flag = False
finally:
    print("camera is: ", camera_flag, "at: ", video_capture)

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
modules.create_user_intreface(
    keystone_points_array, video_resolution_x, video_resolution_y)

# call colors dictionary
DICTIONARY_COLORS = {
    # black
    0: (0, 0, 0),
    # white
    1: (255, 255, 255)
}


# create the location  array of scanners
array_of_scanner_points_locations = modules.get_scanner_pixel_coordinates(
    video_resolution_x, one_module_scale,  scanner_square_size)

# holder of old cell colors array to check for new scan
OLD_CELL_COLORS_ARRAY = []

# holder of old slider for new one
OLD_SLIDER = 0.5


##################################################
###################MAIN LOOP######################
##################################################

# run the video loop forever
while True:

    # get a new matrix transformation every frame
    KEY_STONE_DATA = modules.keystone(
        video_resolution_x, video_resolution_y, modules.listen_to_slider_interaction())

    # zero an array to collect the scanners
    CELL_COLORS_ARRAY = []

    # read video frames
    _, THIS_FRAME = video_capture.read()

    # warp the video based on keystone info
    DISTORTED_VIDEO_STREAM = cv2.warpPerspective(
        THIS_FRAME, KEY_STONE_DATA, (video_resolution_x, video_resolution_y))

    ##################################################

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
        scannerCol = modules.select_color_by_mean_value(mean_color_RGB)

        # add colors to array for type analysis
        CELL_COLORS_ARRAY.append(scannerCol)

        # get color from dict
        thisColor = DICTIONARY_COLORS[scannerCol]

        # draw rects with frame colored by range result
        cv2.rectangle(DISTORTED_VIDEO_STREAM, (x, y),
                      (x+this_scanner_max_dimension,
                       y+this_scanner_max_dimension),
                      thisColor, 3)

        '''
        TO REMOVE LATER -- MAKES A GRADUAL SLIDER
        '''
        SLIDER = "{0:.2f}".format(math.sin(time.time()/5) ** 2)


##################################################

    # reduce unnecessary scan analysis and sending by comparing
    # the list of scanned cells to an old one
    # as well as checks for new slider position
    if CELL_COLORS_ARRAY != OLD_CELL_COLORS_ARRAY or SLIDER != OLD_SLIDER:

        # send array to check types
        TYPES_LIST = modules.find_type_in_tags_array(
            CELL_COLORS_ARRAY, array_of_tags_from_json,
            array_of_maps_form_json,
            array_of_rotations_form_json)

        # send using UDP
        modules.send_over_UDP(TYPES_LIST, SLIDER)

        # match the two
        OLD_CELL_COLORS_ARRAY = CELL_COLORS_ARRAY
        OLD_SLIDER = SLIDER
    else:
        # else skip this
        pass

    # add type and pos text
    cv2.putText(DISTORTED_VIDEO_STREAM, 'Types: ' + str(TYPES_LIST),
                (50, 50), cv2.FONT_HERSHEY_DUPLEX,
                0.5, (0, 0, 0), 1)

    # draw the video to screen
    cv2.imshow("CityScopeScanner", DISTORTED_VIDEO_STREAM)

    ##################################################
    #####################INTERACTION##################
    ##################################################

    # break video loop by pressing ESC
    KEY_STROKE = cv2.waitKey(1)
    if chr(KEY_STROKE & 255) == 'q':
        # break the loop
        break

    # # saves to file
    elif chr(KEY_STROKE & 255) == 's':
        modules.save_keystone_to_file(
            modules.listen_to_slider_interaction())

# close opencv
video_capture.release()
cv2.destroyAllWindows()
