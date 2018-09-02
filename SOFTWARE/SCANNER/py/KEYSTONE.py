import numpy as np
import cv2

webcam = cv2.VideoCapture(0)
cv2.namedWindow('image')
webcam.set(3, 800)
webcam.set(4, 600)

# top left, top right, bottom left, bottom right
pts = [(0, 0), (0, 0), (0, 0), (0, 0)]
pointIndex = 0
mousePos = (0, 0)

# Aspect ratio
ASPECT_RATIO = (600, 600)
pts2 = np.float32([[0, 0], [ASPECT_RATIO[1], 0], [0, ASPECT_RATIO[0]], [
                  ASPECT_RATIO[1], ASPECT_RATIO[0]]])


def selectFourPoints():
    global frame
    global pointIndex

    print("select 4 points, by double clicking on each of them in the order: \n\
	top left, top right, bottom left, bottom right.")
    while(pointIndex != 4):
        # wait for clicks
        cv2.setMouseCallback('image', saveThisPoint)
        _, frame = webcam.read()
        # draw mouse pos
        cv2.circle(frame, mousePos, 10, (0, 0, 255), 1)
        # draw clicked points
        for pt in pts:
            cv2.circle(frame, pt, 10, (255, 0, 0), 1)
        cv2.imshow('image', frame)
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            return False
    return True


def saveThisPoint(event, x, y, flags, param):
    # mouse callback function
    global frame
    global pointIndex
    global pts
    global mousePos

    if event == cv2.EVENT_MOUSEMOVE:
        mousePos = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        # draw a ref. circle
        print('point  # ', pointIndex, (x, y))
        # save this point to the array pts
        pts[pointIndex] = (x, y)
        pointIndex = pointIndex + 1


# checks if finished selecting the 4 corners
if(selectFourPoints()):
    # The four points in the image
    pts1 = np.float32([
        [pts[0][0], pts[0][1]],
        [pts[1][0], pts[1][1]],
        [pts[2][0], pts[2][1]],
        [pts[3][0], pts[3][1]]])

# perform the transformation
    M = cv2.getPerspectiveTransform(pts1, pts2)
    print("np array keystone pts", M)
    np.savetxt("keystone.txt", M)

webcam.release()
cv2.destroyAllWindows()
