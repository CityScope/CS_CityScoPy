# ////////////////////////////////////////////////////////////////////////////////////
# {{ CityScopePy }}
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

# ////////////////////////////////////////////////////////////////////////////////////

# CityScopePy KEYSTONE
# Exports a selection of keystone points using WEBCAM GUI

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


import numpy as np
import cv2

# file path to save
FILE_PATH = "DATA/keystone.txt"

# make WEBCAM

# define the video stream
try:
    # try from a device 1 in list, not default webcam
    WEBCAM = cv2.VideoCapture(1)
    # if not exist, use device 0
    if not WEBCAM.isOpened():
        WEBCAM = cv2.VideoCapture(0)
finally:
    print(WEBCAM)

# video winodw
cv2.namedWindow('canvas', cv2.WINDOW_NORMAL)


# top left, top right, bottom left, bottom right
POINTS = [(0, 0), (0, 0), (0, 0), (0, 0)]
POINT_INDEX = 0
MOUSE_POSITION = (0, 0)


def selectFourPoints():
    # let users select 4 points on WEBCAM GUI

    global FRAME
    global POINT_INDEX

    print("select 4 points, by double clicking on each of them in the order: \n\
	top left, top right, bottom left, bottom right.")

    # loop until 4 clicks
    while POINT_INDEX != 4:

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False

        # wait for clicks
        cv2.setMouseCallback('canvas', save_this_point)

        # read the WEBCAM frames
        _, FRAME = WEBCAM.read()

        # draw mouse pos
        cv2.circle(FRAME, MOUSE_POSITION, 10, (0, 0, 255), 1)
        cv2.circle(FRAME, MOUSE_POSITION, 1, (0, 0, 255), 2)

        # draw clicked points
        for thisPnt in POINTS:
            cv2.circle(FRAME, thisPnt, 10, (255, 0, 0), 1)
        # show the video
        cv2.imshow('canvas', FRAME)

    return True


def save_this_point(event, x, y, flags, param):
    # saves this point to array

    # mouse callback function
    global FRAME
    global POINT_INDEX
    global POINTS
    global MOUSE_POSITION

    if event == cv2.EVENT_MOUSEMOVE:
        MOUSE_POSITION = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        # draw a ref. circle
        print('point  # ', POINT_INDEX, (x, y))
        # save this point to the array pts
        POINTS[POINT_INDEX] = (x, y)
        POINT_INDEX = POINT_INDEX + 1


# checks if finished selecting the 4 corners
if selectFourPoints():
    np.savetxt(FILE_PATH, POINTS)
    print("keystone initial points were saved")

WEBCAM.release()
cv2.destroyAllWindows()
