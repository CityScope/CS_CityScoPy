# imports packages
import numpy as np
import argparse
import cv2
import socket

##################################################

colRangeDict = {
    0: [np.array([0, 0, 0], np.uint8),  # black d
        np.array([0, 0, 50], np.uint8)],  # black u
    1: [np.array([0, 0, 50], np.uint8),  # white d
        np.array([0, 0, 100], np.uint8)]}  # wihte u

colDict = {
    0: (0, 0, 0),  # black
    1: (255, 255, 255)}  # white

##################################################


def colorSelect(meanColor):
    # convert color to hsv for oclidian distance
    bgrToGray = cv2.cvtColor(meanColor, cv2.COLOR_BGR2GRAY)
    if int(bgrToGray) < 125:
        colResult = 0
    else:
        colResult = 1
    return colResult

##################################################


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


##################################################

def checkForNewGrid():
    '''
pseudo code here:
if no change to results array, do nothing
else, compse the sliced submatrix of X*Y for each grid cell

import numpy as np
    a = np.reshape(np.arange(162), (18, 9))
    print(a)
    b = a[0: 3, 0: 3]
    print(b)

'''

##################################################


def findType(resultColorArray, tagsArray):
    typesArray = []
    for i in resultColorArray:

        if i in tagsArray:
            typesArray.append(tagsArray.index(i))
        else:
            typesArray.append(-1)
    return typesArray


##################################################


# hardcode the locations of the scanners
scannersHardcodeList = [
    15, 43, 85, 113, 155, 183,
    18, 46, 88, 116, 158, 186,
    21, 49, 91, 119, 161, 189
]


def makeGridOrigins(videoResX, videoResY, cropSize):

    # actual locations of scanners
    scannersLocationsArr = []

    # zreo the counter
    c = 0

    # gap
    gap = 10

    for x in range(0, videoResX - int(videoResX/14), int(videoResX/14)):
        for y in range(0, videoResX-int(videoResX/8), int(videoResY/8)):
            # check if this poistion is in hardcoded locations
            # array and if so get its position
            #
            if c in scannersHardcodeList:
                for i in range(0, 3):
                    for j in range(0, 3):

                        # append 3x3 loctions to array for scanners
                        scannersLocationsArr.append([x-25 + i*(cropSize + gap),
                                                     y-25 + j*(cropSize + gap)])
            # count
            c += 1
    # print("Init scanner array: ", scannersLocationsArr,
    #       '\n', len(scannersLocationsArr))
    return scannersLocationsArr
