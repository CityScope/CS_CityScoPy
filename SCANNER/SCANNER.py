# /////////////////////////////////////////////////////////////////////////////
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

# /////////////////////////////////////////////////////////////////////////////

# CityScopePy SCANNER
# a simple decoder of 2d array made of LEGO bricks, parsing and sending for visualzation

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]

# raise SystemExit(0)

import math
import numpy as np
import cv2
import MODULES


# load the tags text file
tagsArray = np.loadtxt('tags.txt', dtype=str)

# load the keystone data from file
keyStoneData = np.loadtxt('../KEYSTONE/keystone.txt')

# define the video
webcam = cv2.VideoCapture(0)

# hardcode the locations of the scanners
scannersLocationArr = [
    15, 43, 85, 113, 155, 183,
    18, 46, 88, 116, 158, 186,
    21, 49, 91, 119, 161, 189
]

# define the video window
cv2.namedWindow('vid')

# set res. for vid
videoResX = 1200
videoResY = 600

# define the grid size
gridX = 6
gridY = 3

# define the number of grid pixel scanners
gridSize = gridX*gridY

# define the size for each scanner
cropSize = int(0.25 * videoResX/gridSize)

# array to collect the scanners
colorArr = np.zeros((gridSize*gridSize), dtype=np.int64)

# call colors dictionary
colors = MODULES.colDict

# equal divide of canvas
step = int(videoResX/gridSize)


def makeGridOrigins():

    # read video frames
    _, thisFrame = webcam.read()
    # warp the video based on keystone info
    distortVid = cv2.warpPerspective(
        thisFrame, keyStoneData, (videoResX, videoResY))

    c = 0
    for x in range(0, videoResX - int(videoResX/14), int(videoResX/14)):
        for y in range(0, videoResX-int(videoResX/8), int(videoResY/8)):
            #
            # check if this poistion is in hardcoded locations
            # array and if so get its position
            #
            if c in scannersLocationArr:
                cv2.circle(distortVid, (x, y), 20, (255, 0, 0),
                           thickness=1, lineType=8, shift=0)

                # create text display on bricks
                cv2.putText(distortVid, str(c),
                            (x-2, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.3, (0, 0, 255))

            c += 1
    # draw the video to screen
    cv2.imshow("vid", distortVid)



# run the video loop forever
while(True):
    makeGridOrigins()
    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break


'''
    # init counter for populating colors array
    counter = 0
    # read video frames
    _, thisFrame = webcam.read()
    # warp the video based on keystone info
    distortVid = cv2.warpPerspective(
        thisFrame, keyStoneData, (videoResX, videoResY))

    # if needed, implement max_rgb_filter
    # dst = MODULES.max_rgb_filter(dst)

    ########

    for x in range(0, gridX*step*3, step):
        for y in range(0, gridY*step*3, step):

            # set scanner crop box size and position
            # at x,y + crop box size
            crop = distortVid[y:y+cropSize, x:x+cropSize]

            # draw rects with mean value of color
            meanCol = cv2.mean(crop)

            # convert colors to rgb
            b, g, r, _ = np.uint8(meanCol)
            mCol = np.uint8([[[b, g, r]]])

            # select the right color based on sample
            scannerCol = MODULES.colorSelect(mCol)
            thisColor = colors[scannerCol]

            # draw rects with frame colored by range result
            cv2.rectangle(distortVid, (x-1, y-1),
                          (x+cropSize + 1, y+cropSize + 1),
                          thisColor, 1)

            # draw the mean color itself
            cv2.rectangle(distortVid, (x, y),
                          (x+cropSize, y+cropSize),
                          meanCol, -1)

            # create text display on bricks
            cv2.putText(distortVid, str(scannerCol),
                        (x + int(cropSize/3), y+cropSize), cv2.FONT_HERSHEY_SIMPLEX,
                        0.3, (0, 0, 0))

            # add colors to array for type analysis
            colorArr[counter] = scannerCol
            counter += 1

    # create the output colors array
    resultColorArray = colorArr.reshape(gridSize, gridSize).transpose()

    # draw the video to screen
    cv2.imshow("vid", distortVid)

    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break
'''


webcam.release()
cv2.destroyAllWindows()
