import cv2
import numpy as np
import naoqi


ip = "192.168.1.103"
port = 9559


#######################
# connect

videoProxy = naoqi.ALProxy('ALVideoDevice', ip, port)

cam_name = "camera"
cam_type = 0
res = 1
colspace = 13
fps = 10

cams = videoProxy.getSubscribers()
for cam in cams:
    videoProxy.unsubscribe(cam)

cam = videoProxy.subscribeCamera(cam_name, cam_type, res, colspace, fps)

print "Succesfully connected"

###################################3
# get/save frame
image_container = videoProxy.getImageRemote(cam)

width = image_container[0]
height = image_container[1]

values = map(ord, list(image_container[6]))

image = np.array(values, np.uint8).reshape((height, width, 3))

cv2.imwrite("ballimage3.png", image)


image = cv2.imread("ballimage3.png")
cv2.imshow("First image", image)

cv2.waitKey()


#############################
# unsubscribe
videoProxy.unsubscribe(cam)
