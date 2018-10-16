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

# CityScope Python Scanner - Modules
# Keystone, decode and send over UDP a 2d array
# of uniquely tagged LEGO array

##################################################

# imports packages
import numpy as np
import cv2
import socket
import json


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
        if len(i) > 1:
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


def listen_to_slider_interaction():
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
    f = open(filePath, 'w')
    np.savetxt(f, keystone_data_from_user_interaction)
    f.close()
    print("keystone points were saved in", filePath)

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
    # convert color to hsv for oclidian distance
    bgr_to_grayscale = cv2.cvtColor(mean_color_RGB, cv2.COLOR_BGR2GRAY)
    if int(bgr_to_grayscale) < 125:
        this_color = 0
    else:
        this_color = 1
    return this_color

##################################################


def send_over_UDP(udpPacket):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    # convert to string and encode the packet
    enocded_udp_packet = str(udpPacket).encode("utf-8")
    # debug
    print('\n', "UDP:", udpPacket)

    # open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(enocded_udp_packet, (UDP_IP, UDP_PORT))


##################################################


def find_type_in_tags_array(cellColorsArray, tagsArray, mapArray, rotationArray):
    typesArray = []
    # create np colors array with table struct
    npColsArr = np.reshape(cellColorsArray, (18, 9))
    # go through the results
    for thisResult in npColsArr:
        # look for this result in tags array from JSON
        # and return only where TRUE apears in results
        whichTag = np.where([(thisResult == tag).all()
                             for tag in tagsArray])[0]
        # if this tag is not found return -1
        if whichTag.size == 0:
            typesArray.append(-1)
        # else return the tag location in the list
        else:
            typesArray.append([mapArray[int(whichTag[0])],
                               rotationArray[int(whichTag[0])]])
    # finally, return this list to main program for UDP
    return typesArray


##################################################


def get_scanner_pixel_coordinates(video_res_x, crop_size):
    """Creates list of pixel coordinates for scanner.

    Steps:
        - Determine vritual points on the grid that will be the centers of blocks.
        - Transform those virtual points pixel coordinates and expand them into 3x3 clusters of pixel points

    Args:


    Returns list of [x, y] pixel coordinates for scanner to read.
    """

    # Point looks like [x, y]
    virtual_points = [
        # # First row
        [1, 1],
        [3, 1],
        [6, 1],
        [8, 1],
        [11, 1],
        [13, 1],
        # # Second row
        [1, 4],
        [3, 4],
        [6, 4],
        [8, 4],
        [11, 4],
        [13, 4],
        # # Third row
        [1, 7],
        [3, 7],
        [6, 7],
        [8, 7],
        [11, 7],
        [13, 7]
    ]

    number_of_cells = 14
    scale = int(video_res_x/number_of_cells)
    scanner_locations_array = transform_virtual_points_to_pixels(
        virtual_points, scale, crop_size)
    return scanner_locations_array

##################################################


def transform_virtual_points_to_pixels(points, scale, crop_size):
    """
    Transforms virtual [x, y] coordinate pairs to pixel representations
    for scanner.

    Returns list of [x, y] pixel coordinates for scanner.
    """
    pixel_coordinates_list = []
    for [x, y] in points:
        scaled_x = x*scale
        scaled_y = y*scale
        for i in range(0, 3):
            for j in range(0, 3):
                pixel_coordinates_list.append(
                    [scaled_x + (i*crop_size), scaled_y + (j*crop_size)])

    return pixel_coordinates_list


##################################################


'''
def checkForNewGrid():
if no change to results array, do nothing
else, compse the sliced submatrix of X*Y for each grid cell
'''
