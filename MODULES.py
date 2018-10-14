# imports packages
import numpy as np
import cv2
import socket
import json

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


def JSONparse(field):
    # init array for json fields
    filedArray = []
    # open json file
    with open('DATA/tags.json') as json_data:
        jd = json.load(json_data)
    # return each item for this field
    for i in jd[field]:
        # if item length is more than 1 [tags]
        if len(i) > 1:
            # parse this item as np array
            filedArray.append(np.array([int(ch) for ch in i]))
        else:
            # otherwise send it as is
            filedArray.append(i)
    return filedArray

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


def findType(cellColorsArray, tagsArray):
    typesArray = []
    # create np colors array with table struct
    npColsArr = np.reshape(cellColorsArray, (18, 9))
    # go through the results
    for thisResult in npColsArr:
        # look for this result in tags array from JSON
        whichTag = np.where([(thisResult == tag).all()
                             for tag in tagsArray])[0]
        # if this tag is not found return -1
        if whichTag.size == 0:
            typesArray.append(-1)
        # else return the tag location in the list
        else:
            typesArray.append(int(whichTag[0]))
    # finally, return this list to main program for UDP
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

    # sum of 'half' virtual modules in the table
    moduleX = 14
    moduleY = 8
# zreo the counter
    c = 0
    # gap
    gap = 10
    for x in range(0, videoResX - int(videoResX/moduleX), int(videoResX/moduleX)):
        for y in range(0, videoResX-int(videoResX/moduleY), int(videoResY/moduleY)):
            # check if this poistion is in hardcoded locations
            # array and if so get its position
            if c in scannersHardcodeList:
                for i in range(0, 3):
                    for j in range(0, 3):
                        # append 3x3 loctions to array for scanners
                        scannersLocationsArr.append([x + i*(cropSize + gap),
                                                     y + j*(cropSize + gap)])
            # count
            c += 1
    return scannersLocationsArr


##################################################


# Upkey: 2490368
# DownKey: 2621440
# LeftKey: 2424832
# RightKey: 2555904
# Space: 32
# Delete: 3014656

'''
NOTE: Aspect ratio is fliped than in scanner
so that aspectRat[0,1] will be aspectRat[1,0]
in SCANNER tool
'''


def fineGrainKeystone(videoResX, videoResY, keyStonePts, value):
    # inverted screen ratio for np source array
    aspectRat = (videoResY, videoResX)
    # np source points array
    srcPnts = np.float32([[0, 0], [aspectRat[1], 0], [0, aspectRat[0]], [
        aspectRat[1], aspectRat[0]]])

    M = cv2.getPerspectiveTransform(keyStonePts, srcPnts)
    return M


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
