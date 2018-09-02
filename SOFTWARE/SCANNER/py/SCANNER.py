import math
import numpy as np
import cv2

# define range of  color in HSV
ORANGE_MIN = np.array([5, 50, 50], np.uint8)
ORANGE_MAX = np.array([15, 255, 255], np.uint8)

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

    for x in range(0, vidRes-cropSize, int(vidRes/gridSize)):
        for y in range(0, vidRes-cropSize, int(vidRes/gridSize)):
            crop = dst[y:y+cropSize, x:x+cropSize]
            # draw rects with mean value of color
            meanCol = cv2.mean(crop)
            cropOne = dst[y:y+1, x:x+1]
            bgrToHsv = cv2.cvtColor(cropOne, cv2.COLOR_BGR2HSV)
            inRange = cv2.inRange(bgrToHsv, ORANGE_MIN, ORANGE_MAX)
            inRange = int(inRange)
            # print(inRange, type(inRange))
            #########
            cv2.rectangle(dst, (x-1, y-1), (x+cropSize + 1, y+cropSize + 1),
                          (inRange, inRange, inRange), 1)
            # then draw the mean color itself
            cv2.rectangle(dst, (x, y), (x+cropSize,
                                        y+cropSize), meanCol, -1)
            np.append(colorArr, meanCol)

    # print('\n', colorArr)
    # draw the video to screen
    cv2.imshow("vid", dst)

    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break


webcam.release()
cv2.destroyAllWindows()
