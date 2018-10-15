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


def GUI(keyStonePts, videoResX, videoResY):

    cv2.createTrackbar('Upper Left X', 'CityScopeScanner',
                       keyStonePts[0][0], videoResX, nothing)
    cv2.createTrackbar('Upper Left Y', 'CityScopeScanner',
                       keyStonePts[0][1], videoResY, nothing)
    cv2.createTrackbar('Upper Right X', 'CityScopeScanner',
                       keyStonePts[1][0], videoResX, nothing)
    cv2.createTrackbar('Upper Right Y', 'CityScopeScanner',
                       keyStonePts[1][1], videoResY, nothing)
    cv2.createTrackbar('Buttom Left X', 'CityScopeScanner',
                       keyStonePts[2][0], videoResX, nothing)
    cv2.createTrackbar('Buttom Left Y', 'CityScopeScanner',
                       keyStonePts[2][1], videoResY, nothing)
    cv2.createTrackbar('Buttom Right X', 'CityScopeScanner',
                       keyStonePts[3][0], videoResX, nothing)
    cv2.createTrackbar('Buttom Right Y', 'CityScopeScanner',
                       keyStonePts[3][1], videoResY, nothing)


def nothing(event):
    pass


def getSliders():

    ulx = cv2.getTrackbarPos('Upper Left X', 'CityScopeScanner')
    uly = cv2.getTrackbarPos('Upper Left Y', 'CityScopeScanner')
    urx = cv2.getTrackbarPos('Upper Right X', 'CityScopeScanner')
    ury = cv2.getTrackbarPos('Upper Right Y', 'CityScopeScanner')
    blx = cv2.getTrackbarPos('Buttom Left X', 'CityScopeScanner')
    bly = cv2.getTrackbarPos('Buttom Left Y', 'CityScopeScanner')
    brx = cv2.getTrackbarPos('Buttom Right X', 'CityScopeScanner')
    bry = cv2.getTrackbarPos('Buttom Right Y', 'CityScopeScanner')
    return np.asarray([(ulx, uly), (urx, ury), (blx, bly), (brx, bry)], dtype=np.float32)

##################################################


def saveToFile(keystoneArr):
    filePath = "DATA/keystone.txt"
    f = open(filePath, 'w')
    np.savetxt(f, keystoneArr)
    f.close()
    print("keystone points were saved in", filePath)

##################################################


'''
NOTE: Aspect ratio is fliped than in scanner
so that aspectRat[0,1] will be aspectRat[1,0]
in SCANNER tool
'''


def keystone(videoResX, videoResY, keyStonePts):
    # inverted screen ratio for np source array
    aspectRat = (videoResY, videoResX)
    # np source points array
    srcPnts = np.float32(
        [
            [0, 0],
            [aspectRat[1], 0],
            [0, aspectRat[0]],
            [aspectRat[1], aspectRat[0]]
        ])
    # make the 4 pnts matrix perspective transformation
    trans = cv2.getPerspectiveTransform(keyStonePts, srcPnts)
    return trans

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


def findType(cellColorsArray, tagsArray, mapArray, rotationArray):
    typesArray = []
    # create np colors array with table struct
    npColsArr = np.reshape(cellColorsArray, (18, 9))
    # go through the results
    for thisResult in npColsArr:
        # look for this result in tags array from JSON
        # and return only where TRUE apears in results
        whichTag = np.where([(thisResult == tag).all()
                             for tag in tagsArray])[0]
        # if this tag is not found return -1
        if whichTag.size == 0:
            typesArray.append(-1)
        # else return the tag location in the list
        else:
            typesArray.append([mapArray[int(whichTag[0])],
                               rotationArray[int(whichTag[0])]])
    # finally, return this list to main program for UDP
    return typesArray


##################################################


def get_scanner_pixel_coordinates(video_res_x, crop_size):
    """Creates list of pixel coordinates for scanner.

    Steps:
        - Determine vritual points on the grid that will be the centers of blocks.
        - Transform those virtual points pixel coordinates and expand them into 3x3 clusters of pixel points

    Args:


    Returns list of [x, y] pixel coordinates for scanner to read.
    """

    # Point looks like [x, y]
    virtual_points = [
        # # First row
        [1, 1],
        [3, 1],
        [6, 1],
        [8, 1],
        [11, 1],
        [13, 1],
        # # Second row
        [1, 4],
        [3, 4],
        [6, 4],
        [8, 4],
        [11, 4],
        [13, 4],
        # # Third row
        [1, 7],
        [3, 7],
        [6, 7],
        [8, 7],
        [11, 7],
        [13, 7]
    ]

    number_of_cells = 14
    scale = int(video_res_x/number_of_cells)
    scanner_locations_array = transform_virtual_points_to_pixels(
        virtual_points, scale, crop_size)
    return scanner_locations_array


def transform_virtual_points_to_pixels(points, scale, crop_size):
    """
    Transforms virtual [x, y] coordinate pairs to pixel representations
    for scanner.

    Returns list of [x, y] pixel coordinates for scanner.
    """
    pixel_coordinates_list = []
    for [x, y] in points:
        scaled_x = x*scale
        scaled_y = y*scale
        for i in range(0, 3):
            for j in range(0, 3):
                pixel_coordinates_list.append(
                    [scaled_x + (i*crop_size), scaled_y + (j*crop_size)])

    return pixel_coordinates_list


##################################################


'''
def checkForNewGrid():
if no change to results array, do nothing
else, compse the sliced submatrix of X*Y for each grid cell
'''
