import naoqi
from time import sleep

ip = "192.168.1.143"
port = 9559

# postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
# motionProxy = naoqi.ALProxy("ALMotion", ip ,port )

memory = naoqi.ALProxy("ALMemory", ip, port)
sonar = naoqi.ALProxy("ALSonar", ip, port)

sonar.subscribe("myS")

i = 0
while i < 100:
    print "Left:", memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    print "Right:", memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
    i += 1
    sleep(0.5)

sonar.unsubscribe("myS")
