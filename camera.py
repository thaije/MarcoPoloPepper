# Author        :   Tjalling Haije (s1011759)
# Date          :   05-12-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   Does image processing for tracking blue round objects
# How to run    :   Don't run this file, run run.py

import cv2
import numpy as np
import naoqi
import sys

resolution = 1
resolutionX = 320
resolutionY = 240

def setupCamera(ip, port):
    videoProxy = naoqi.ALProxy('ALVideoDevice', ip, port)

    cam_name = "camera"
    cam_type = 0
    res = resolution
    colspace = 13
    fps = 30

    cams = videoProxy.getSubscribers()
    for cam in cams:
        videoProxy.unsubscribe(cam)

    cam = videoProxy.subscribeCamera(cam_name, cam_type, res, colspace, fps)

    print "Succesfully connected camera"
    return videoProxy, cam


def findBall(image, ballColour): # default ballcolour to recognize is blue

    ###################################
    # Apply a threshold
    ##################################

    # lower_blue = np.array([70,50,50], dtype=np.uint8)
    # upper_blue = np.array([170, 255, 255], dtype=np.uint8)

    # ballColours = ["pink" "red" "blue" "yellow" "orange" "green" "white"]
    if ballColour == "pink":
        lower_colour = np.array([130, 100, 100], dtype=np.uint8)
        upper_colour = np.array([180, 255, 255], dtype=np.uint8)
    elif ballColour == "green":
        lower_colour = np.array([29, 86, 6], dtype=np.uint8)
        upper_colour = np.array([64, 255, 255], dtype=np.uint8)
    elif ballColour == "yellow":
        lower_colour = np.array([20, 100, 100], dtype=np.uint8)
        upper_colour = np.array([60, 255, 255], dtype=np.uint8)
    elif ballColour == "red":
        lower_colour = np.array([0, 100, 100], dtype=np.uint8)
        upper_colour = np.array([10, 255, 255], dtype=np.uint8)
        # red has an extra colur mask
        lower_colour2 = np.array([160, 100, 100], dtype=np.uint8)
        upper_colour2 = np.array([179, 255, 255], dtype=np.uint8)
    elif ballColour == "blue":
        lower_colour = np.array([70, 50, 50], dtype=np.uint8)
        upper_colour = np.array([170, 255, 255], dtype=np.uint8)
    else: # default is blue balls
        lower_colour = np.array([70, 50, 50], dtype=np.uint8)
        upper_colour = np.array([170, 255, 255], dtype=np.uint8)


    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsvImage, lower_colour, upper_colour)

    # if the colour is red, we have two colour ranges so create
    # an extra colour mask, and blend them together
    if ballColour == "red":
        color_mask2 = cv2.inRange(hsvImage, lower_colour2, upper_colour2)
        color_mask = cv2.addWeighted(color_mask, 1.0, color_mask2, 1.0, 0)
        color_mask = cv2.GaussianBlur(color_mask, (5,5), 0)

    #colour_image = cv2.bitwise_and(image, image, mask=color_mask)


    ##############################################
    # Remove noise from mask and smooth result
    #############################################
    kernel = np.ones((9,9), np.uint8)

    opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

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

    # check if we found a ball, if so show it and return it
    if circles is not None:
        print "Found a ball in findBall in camera"
        circle = circles[0, :][0]
        # print circle
        # print "Ball at " , circle[0], ", ", circle[1], " with size", 2*circle[2]
        cv2.circle(image, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        cv2.imshow("Result", image)
        return (circle[0], circle[1])

    cv2.imshow("Result", image)
    return False


def getFrame(videoProxy, cam):
    image = False

    try:
        image_container = videoProxy.getImageRemote(cam)
        width = image_container[0]
        height = image_container[1]
        values = map(ord, list(image_container[6]))
        image = np.array(values, np.uint8).reshape((height, width, 3))
    except:
        print "missed frame (or error)"
        # print "Unexpected error:", sys.exc_info()[0]
        pass

    return image

# test code
#
# setupCamera()
# i = 0
# while i < 1:
#
#     try:
#         # capture frame
#         image = getFrame()
#     except:
#         print "missed frame"
#         pass
#
#     #process frame
#     findBall(image)
#
#     if cv2.waitKey(33) == 27:
#         videoProxy.unsubscribe(cam)
#         break;
