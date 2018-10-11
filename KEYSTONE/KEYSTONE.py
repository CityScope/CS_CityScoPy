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
# Exports a selection of a transformed matrix from a webcam video using GUI

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
print('Webcam found at:', '\n', webcam)
# video winodw
cv2.namedWindow('canvas')


# top left, top right, bottom left, bottom right
pts = [(0, 0), (0, 0), (0, 0), (0, 0)]
pointIndex = 0
mousePos = (0, 0)

''' 
NOTE: Aspect ratio is fliped than in scanner
so that ASPECT_RATIO[0,1] will be ASPECT_RATIO[1,0]
in SCANNER tool
'''

ASPECT_RATIO = (600, 1200)
pts2 = np.float32([[0, 0], [ASPECT_RATIO[1], 0], [0, ASPECT_RATIO[0]], [
    ASPECT_RATIO[1], ASPECT_RATIO[0]]])


def selectFourPoints():
    global frame
    global pointIndex

    print("select 4 points, by double clicking on each of them in the order: \n\
	top left, top right, bottom left, bottom right.")
    while(pointIndex != 4):

        # wait for clicks
        cv2.setMouseCallback('canvas', saveThisPoint)

        # read the webcam frames
        _, frame = webcam.read()

        # draw mouse pos
        cv2.circle(frame, mousePos, 10, (0, 0, 255), 1)

        # draw clicked points
        for pt in pts:
            cv2.circle(frame, pt, 10, (255, 0, 0), 1)
        # show the video
        cv2.imshow('canvas', frame)

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False
    return True


def saveThisPoint(event, x, y, flags, param):
    # mouse callback function
    global frame
    global pointIndex
    global pts
    global mousePos

    if event == cv2.EVENT_MOUSEMOVE:
        mousePos = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        # draw a ref. circle
        print('point  # ', pointIndex, (x, y))
        # save this point to the array pts
        pts[pointIndex] = (x, y)
        pointIndex = pointIndex + 1


# checks if finished selecting the 4 corners
if(selectFourPoints()):
    # The four points in the canvas
    pts1 = np.float32([
        [pts[0][0], pts[0][1]],
        [pts[1][0], pts[1][1]],
        [pts[2][0], pts[2][1]],
        [pts[3][0], pts[3][1]]])

# perform the transformation
    M = cv2.getPerspectiveTransform(pts1, pts2)
    filePath = "../KEYSTONE/keystone.txt"
    np.savetxt(filePath, M)
    print("np array keystone pts was saved in ", filePath)

webcam.release()
cv2.destroyAllWindows()
