# import the necessary packages
import numpy as np
import argparse
import cv2
import socket


colRangeDict = {0: [np.array([0, 70, 50], np.uint8),  # red down
                    np.array([10, 255, 255], np.uint8)],  # red up
                1: [np.array([0, 0, 0], np.uint8),  # black d
                    np.array([0, 0, 50], np.uint8)],  # black u
                2: [np.array([0, 0, 50], np.uint8),  # white d
                    np.array([0, 0, 100], np.uint8)]}  # wihte u

colDict = {0: (0, 0, 255),  # red
           1: (0, 0, 0),  # black
           2: (255, 255, 255)}  # white


def colorSelect(meanColor):
    # convert color to hsv for oclidian distance
    bgrToHsv = cv2.cvtColor(meanColor, cv2.COLOR_BGR2HSV)
    bgrToGray = cv2.cvtColor(meanColor, cv2.COLOR_BGR2GRAY)
    # # try to find if this color is in range [0 or 255]

    colRange = int(cv2.inRange(
        bgrToHsv, colRangeDict[0][0], colRangeDict[0][1]))
    if colRange == 255:
        colResult = 0
    elif colRange != 255:
        if int(bgrToGray) < 125:
            colResult = 1
        else:
            colResult = 2
    return colResult


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


def sendOverUDP(udpPacket):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    # convert to string and encode the packet
    udpPacket = str(udpPacket).encode()
    # debug
    print('\n', "UDP message:", '\n', udpPacket)
    # open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(udpPacket, (UDP_IP, UDP_PORT))
