# NOTE THAT YOU DO NOT NEED A ROBOT FOR THIS TEST

import numpy as np
import naoqi
import time
import cv2

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

image = cv2.imread("PinkBall.jpg")
img = cv2.imread("wafeltosti.jpg")
middle_width = 160
middle_height = 120

ballColour = "pink"

# ballColours = ["pink" "red" "blue" "yellow" "orange" "green" "white"]
if ballColour == "pink": # TODO check colour ranges!!
    lower_colour = np.array([200,10,60], dtype=np.uint8)
    upper_colour = np.array([255, 115, 170], dtype=np.uint8)
elif ballColour == "green":
    lower_colour = np.array([0, 252, 127], dtype=np.uint8)
    upper_colour = np.array([47, 255, 173], dtype=np.uint8)
elif ballColour == "yellow":
    lower_colour = np.array([20, 100, 100], dtype=np.uint8)
    upper_colour = np.array([60, 255, 255], dtype=np.uint8)
elif ballColour == "red":
    lower_colour = np.array([0, 100, 100], dtype=np.uint8)
    upper_colour = np.array([20, 255, 255], dtype=np.uint8)
elif ballColour == "blue":
    lower_colour = np.array([70, 50, 50], dtype=np.uint8)
    upper_colour = np.array([170, 255, 255], dtype=np.uint8)
else: # default is blue balls
    lower_colour = np.array([70, 50, 50], dtype=np.uint8)
    upper_colour = np.array([170, 255, 255], dtype=np.uint8)


    # determine threshold values
    # # use HSV colorspace: hue saturation value
lower_blue = np.array([70,50,50], dtype=np.uint8)
upper_blue = np.array([170, 255, 255], dtype=np.uint8)
# convert to hsv color space
hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# create threshold mask
color_mask = cv2.inRange(hsvImage, lower_colour, upper_colour)
cv2.imshow('image', color_mask)
#
# kernel = np.ones((9,9), np.uint8)
# # remove small objects
# opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
# # close small openings
# closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
# # apply blur to smooth edges
# smoothed_mask = cv2.GaussianBlur(closing, (9,9), 0)
# # # apply mask on image
# blue_image = cv2.bitwise_and(image, image, mask = smoothed_mask)
# # get grayscale
# gray_image = blue_image[:,:,2]
#
# cv2.imshow("gray", gray_image)
#
# # use hough transform to find circular objects in the image
# circles = cv2.HoughCircles(
# gray_image,
# cv2.HOUGH_GRADIENT,
# 1,
# 5,
# param1=200,
# param2=20,
# minRadius=5,
# maxRadius=100
# )
# # get first circle
# circle = circles[0,:][0]
#
# # draw detected circle on original image
# cv2.circle(image, (circle[0], circle[1]), circle[2], (0,255,0), 2)
# cv2.circle(image, (middle_width, middle_height), 15, (0,0,255), 2)
#
# # hoeveel horizontaal anders kijken:
# hor = (circle[0] - middle_width) / middle_width
# ver = (circle[1] - middle_height) / middle_height
#
# print(hor)
# print(ver)
#
# cv2.imshow("Result", image)
#
# #######################################################################################################################
#
# hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# smooth_mask = cv2.GaussianBlur(hsvImg, (9,9), 0)
# #img2 = cv2.bitwise_and(img, img, mask = smooth_mask)
# circles2 = cv2.HoughCircles(
# smooth_mask,
# cv2.HOUGH_GRADIENT,
# 1,
# 5,
# param1=200,
# param2=20,
# minRadius=5,
# maxRadius=100
# )
# if not circles2 is None:
#     circle2 = circles2[0,:][0]
#     cv2.circle(img, (circle2[0], circle2[1]), circle2[2], (0, 0, 255), 2)
#     cv2.imshow("circle2", img)

cv2.waitKey()