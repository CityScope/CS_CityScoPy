# import the necessary packages
import numpy as np
import argparse
import cv2

ORANGE_MIN = np.array([5, 50, 50], np.uint8)
ORANGE_MAX = np.array([15, 255, 255], np.uint8)


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
    # # try to find if this color is in range [0 or 255]
    inRange = cv2.inRange(bgrToHsv, ORANGE_MIN, ORANGE_MAX)
    inRange = int(inRange)
    return inRange
