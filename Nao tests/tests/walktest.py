import time
import naoqi
ip = "192.168.1.143"
port = 9559

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )


# First make the Nao stand still before it can walk
postureProxy.goToPosture("Stand", 0.8)
# StandInit?

# X = forward speed
# forward = 1.0, backward = -1.0
X = 0.5

# Y = Sidewards speed
# 1.0 = counter-clockwise, -1.0 = clockwise
Y = 0

# Theta = Rotation speed
# 1.0 = counter-clockwise, -1.0 counter-clockwise
Theta = 0.0

MotionProxy.moveToward(X, Y, Theta)
time.sleep(10.0)

# stop walking
motionProxy.stopMove()

# sit and relax joints
postureProxy.goToPosture("Sit", 0.5)
motionProxy.rest()
