import math
import numpy as np
import cv2

# define range of blue color in HSV
lower_blue = np.array([110, 50, 50])
upper_blue = np.array([130, 255, 255])

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
print(colorArr)
# run the video loop forever
while(True):
    _, frame = webcam.read()
    dst = cv2.warpPerspective(
        frame, M, (vidRes, vidRes))

    for x in range(0, vidRes-cropSize, int(vidRes/gridSize)):
        for y in range(0, vidRes-cropSize, int(vidRes/gridSize)):
            crop = dst[y:y+cropSize, x:x+cropSize]
            # draw rects with mean value of color
            cvMeanCol = cv2.mean(crop)
            # if cvMeanCol cv2.inRange(hsv, lower_green, upper_green):
                pass
            # print('\n', cvMeanCol)
            # colorArr[x, y] = cvMeanCol
            # make frame around crop
            cv2.rectangle(dst, (x-1, y-1), (x+cropSize + 1, y+cropSize + 1),
                          (0, 255, 0), 1)
            # then draw the mean color itself
            cv2.rectangle(dst, (x, y), (x+cropSize,
                                        y+cropSize), cvMeanCol, -1)
            np.append(colorArr, cvMeanCol)

    # print('\n', colorArr)
    # draw the video to screen
    cv2.imshow("vid", dst)
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break


webcam.release()
cv2.destroyAllWindows()
