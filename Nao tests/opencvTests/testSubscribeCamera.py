import naoqi

ip = "192.168.1.103"
port = 9559

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

videoProxy.unsubscribe(cam)
