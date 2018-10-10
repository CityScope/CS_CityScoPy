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


'''
# Debug only!
import sys
sys.exit()
'''


# load the tags text file
tagsArray = np.loadtxt('tags.txt', dtype=str)

print(tagsArray)

# load the keystone data from file
keyStoneData = np.loadtxt('../KEYSTONE/keystone.txt')
# define the video
webcam = cv2.VideoCapture(0)
# define the video window
# set res. for vid
cv2.namedWindow('vid')
videoRes = 600
# define the number of grid pixel scanners
gridSize = 24
# define the size for each scanner
cropSize = int(0.25 * videoRes/gridSize)
# array to collect the scanners
colorArr = np.zeros((gridSize*gridSize), dtype=np.int64)
colors = MODULES.colDict


# run the video loop forever
while(True):
    counter = 0
    _, frame = webcam.read()
    dst = cv2.warpPerspective(
        frame, keyStoneData, (videoRes, videoRes))

    # if needed, implement max_rgb_filter
    # dst = MODULES.max_rgb_filter(dst)

    step = int(videoRes/gridSize)
    for x in range(int(step/2), videoRes, step):
        for y in range(int(step/2), videoRes, step):
            crop = dst[y:y+cropSize, x:x+cropSize]
            # draw rects with mean value of color
            meanCol = cv2.mean(crop)
            b, g, r, _ = np.uint8(meanCol)
            mCol = np.uint8([[[b, g, r]]])
            scannerCol = MODULES.colorSelect(mCol)
            thisColor = colors[scannerCol]

            # draw rects with frame colored by range result
            cv2.rectangle(dst, (x-1, y-1), (x+cropSize + 1, y+cropSize + 1),
                          thisColor, 1)

            # draw the mean color itself
            cv2.rectangle(dst, (x, y), (x+cropSize,
                                        y+cropSize), meanCol, -1)

            cv2.putText(dst, str([counter, scannerCol]),
                        (x-2, y-2), cv2.FONT_HERSHEY_SIMPLEX,
                        0.2, (0, 0, 0), lineType=cv2.LINE_AA)
            # add colors to array for type analysis
            colorArr[counter] = scannerCol
            counter += 1

    # print the output colors array
    resultColorArray = colorArr.reshape(gridSize, gridSize).transpose()
    # print('\n', resultColorArray)

    # pseudo code here:
    # if no change to results array, do nothing
    # else, compse the sliced submatrix of X*Y for each grid cell

    for i in range(3, 24, 3):
        for j in range(3, 24, 3):
            mat_slice = np.array(resultColorArray[i, j]).flatten()
            print('\n', i, j, mat_slice, '\n')

    # resultColorArray = resultColorArray.copy(order='C')

    # send result over UDP

    # MODULES.sendOverUDP(mat_slice)

    # draw the video to screen
    cv2.imshow("vid", dst)

    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break

webcam.release()
cv2.destroyAllWindows()
