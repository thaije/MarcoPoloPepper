import cv2
import numpy as np

###################################
# Apply a threshold
##################################

image = cv2.imread("../ballimage.png")

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

# cv2.imshow("Result", blue_image)


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
    print circle
    cv2.circle(image, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)

cv2.imshow("Result", image)
cv2.waitKey()
