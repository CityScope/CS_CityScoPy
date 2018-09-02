# import the necessary packages
import numpy as np
import argparse
import cv2


colRangeDict = {'RED': [np.array([0, 70, 50], np.uint8),
                        np.array([10, 255, 255], np.uint8)],
                'BLACK': [np.array([0, 0, 0], np.uint8),
                          np.array([0, 0, 50], np.uint8)],
                'WHITE': [np.array([0, 0, 50], np.uint8),
                          np.array([0, 0, 100], np.uint8)]}

colDict = {'RED': (0, 0, 255),
           'BLACK': (0, 0, 0),
           'WHITE': (255, 255, 255)}


def max_rgb_filter(image):
    # split the image into its BGR components
    (B, G, R) = cv2.split(image)
    # find the maximum pixel intensity values for each
    # (x, y)-coordinate,, then set all pixel values less
    # than M to zero
    M = np.maximum(np.maximum(R, G), B)
    R[R < M] = 0
    G[G < M] = 0
    B[B < M] = 0
    # merge the channels back together and return the image
    return cv2.merge([B, G, R])


def colorSelect(meanColor, x, y):

    # convert color to hsv for oclidian distance
    bgrToHsv = cv2.cvtColor(meanColor, cv2.COLOR_BGR2HSV)
    bgrToGray = cv2.cvtColor(meanColor, cv2.COLOR_BGR2GRAY)
    # # try to find if this color is in range [0 or 255]

    colRange = int(cv2.inRange(
        bgrToHsv, colRangeDict['RED'][0], colRangeDict['RED'][1]))
    if colRange == 255:
        colResult = 'RED'
    elif colRange != 255:
        if int(bgrToGray) < 125:
            colResult = 'BLACK'
        else:
            colResult = 'WHITE'
    return colResult
