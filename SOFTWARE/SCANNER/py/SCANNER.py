import math
import numpy as np
import cv2
import MODULES

# load the keystone data from file
M = np.loadtxt('keystone.txt')
# define the video
webcam = cv2.VideoCapture(0)
# define the video window
cv2.namedWindow('vid')
# set res. for vid
vidRes = 600
# define the number of grid scanners
gridSize = 10
# define the size for each scanner
cropSize = 10
# array to collect the scanners
colorArr = np.tile(np.array([0.]), (gridSize, gridSize))

# run the video loop forever
while(True):
    _, frame = webcam.read()
    dst = cv2.warpPerspective(
        frame, M, (vidRes, vidRes))

    # if needed, implement max_rgb_filter
    # dst = MODULES.max_rgb_filter(dst)

    for x in range(0, vidRes-cropSize, int(vidRes/gridSize)):
        for y in range(0, vidRes-cropSize, int(vidRes/gridSize)):
            crop = dst[y:y+cropSize, x:x+cropSize]
            # draw rects with mean value of color
            # meanCol = cv2.mean(crop)
            b, g, r, _ = np.uint8(cv2.mean(crop))
            mCol = np.uint8([[[b, g, r]]])
            thisColor = MODULES.colorSelect(mCol, x, y)
            # # draw rects with frame colored by range result
            cv2.rectangle(dst, (x-1, y-1), (x+cropSize + 1, y+cropSize + 1),
                          (thisColor, thisColor, thisColor), 1)
            # # draw the mean color itself
            # cv2.rectangle(dst, (x, y), (x+cropSize,
            #                             y+cropSize), meanCol, -1)

            # add colors to array for type analysis
            # np.append(colorArr, meanCol)
    # print the output
    # print('\n', colorArr)
    # draw the video to screen
    cv2.imshow("vid", dst)

    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break

webcam.release()
cv2.destroyAllWindows()
