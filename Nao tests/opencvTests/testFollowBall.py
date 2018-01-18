import cv2
import numpy as np
import naoqi

ip = "192.168.1.103"
port = 9559

videoProxy = False
cam = False

resolution = 1
resolutionX = 320
resolutionY = 240

def setupCamera():
    global videoProxy
    videoProxy = naoqi.ALProxy('ALVideoDevice', ip, port)

    cam_name = "camera"
    cam_type = 0
    res = resolution
    colspace = 13
    fps = 30

    cams = videoProxy.getSubscribers()
    for cam in cams:
        videoProxy.unsubscribe(cam)

    global cam
    cam = videoProxy.subscribeCamera(cam_name, cam_type, res, colspace, fps)

    print "Succesfully connected"



def findBall(image):

    ###################################
    # Apply a threshold
    ##################################

    # image = cv2.imread("ballimage.png")

    lower_blue = np.array([70,50,50], dtype=np.uint8)
    upper_blue = np.array([170, 255, 255], dtype=np.uint8)

    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(hsvImage, lower_blue, upper_blue)

    blue_image = cv2.bitwise_and(image, image, mask=color_mask)


    ##############################################
    # Remove noise from mask and smooth result
    #############################################
    kernel = np.ones((9,9), np.uint8)

    opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

    smoothed_mask = cv2.GaussianBlur(closing, (9,9), 0)


    #################################################
    # Find circular shapes
    #################################################
    blue_image = cv2.bitwise_and(image, image, mask=smoothed_mask)

    gray_image = blue_image[:, :, 2]

    circles = cv2.HoughCircles(
        gray_image,
        cv2.HOUGH_GRADIENT,
        1,
        5,
        param1 = 200,
        param2 = 20,
        minRadius = 5,
        maxRadius = 100
    )

    if not circles is None:
        circle = circles[0, :][0]
        # print circle
        print "Ball at " , circle[0], ", ", circle[1], " with size", 2*circle[2]
        cv2.circle(image, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)

    cv2.imshow("Result", image)



def getFrame():
    image_container = videoProxy.getImageRemote(cam)

    width = image_container[0]
    height = image_container[1]

    values = map(ord, list(image_container[6]))

    image = np.array(values, np.uint8).reshape((height, width, 3))
    return image


def moveHead():
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    # joints = "HeadPitch"
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    # angles = [-0.6, 0.5, 0]
    times = [[2.0, 4.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True

setupCamera()
i = 0
while i < 1:

    try:
        # capture frame
        image = getFrame()
    except:
        print "missed frame"
        pass

    #process frame
    findBall(image)

    if cv2.waitKey(33) == 27:
        videoProxy.unsubscribe(cam)
        break;
