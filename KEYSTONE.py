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
# Exports a selection of keystone points using webcam GUI

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


import numpy as np
import cv2

# make webcam
webcam = cv2.VideoCapture(0)
# video winodw
cv2.namedWindow('canvas')


# top left, top right, bottom left, bottom right
points = [(0, 0), (0, 0), (0, 0), (0, 0)]
pointIndex = 0
mousePos = (0, 0)


def selectFourPoints():
    # let users select 4 points on webcam GUI

    global frame
    global pointIndex

    print("select 4 points, by double clicking on each of them in the order: \n\
	top left, top right, bottom left, bottom right.")

    # loop until 4 clicks
    while(pointIndex != 4):

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False

        # wait for clicks
        cv2.setMouseCallback('canvas', saveThisPoint)

        # read the webcam frames
        _, frame = webcam.read()

        # draw mouse pos
        cv2.circle(frame, mousePos, 10, (0, 0, 255), 1)
        cv2.circle(frame, mousePos, 1, (0, 0, 255), 2)

        # draw clicked points
        for thisPnt in points:
            cv2.circle(frame, thisPnt, 10, (255, 0, 0), 1)
        # show the video
        cv2.imshow('canvas', frame)

    return True


def saveThisPoint(event, x, y, flags, param):
    # saves this point to array

    # mouse callback function
    global frame
    global pointIndex
    global points
    global mousePos

    if event == cv2.EVENT_MOUSEMOVE:
        mousePos = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        # draw a ref. circle
        print('point  # ', pointIndex, (x, y))
        # save this point to the array pts
        points[pointIndex] = (x, y)
        pointIndex = pointIndex + 1


# checks if finished selecting the 4 corners
if(selectFourPoints()):

    filePath = "DATA/keystone.txt"
    f = open(filePath, 'w')
    np.savetxt(f, points)
    f.close()
    print("keystone initial points were saved in ", filePath)

webcam.release()
cv2.destroyAllWindows()
