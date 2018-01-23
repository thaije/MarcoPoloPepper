from naoqi import ALModule, ALProxy, ALBroker
import random
from time import sleep
import numpy as np

# general variables
ip = "192.168.1.115"
port = 9559

motionProxy = ALProxy("ALMotion", ip ,port )
postureProxy = ALProxy("ALRobotPosture", ip ,port )

# look a relative amount to the current head posture in a certain direction
def look(direction):
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.3], [0.3]] #time in seconds
    motionProxy.setStiffnesses(["HeadYaw" "HeadPitch"], [0.8, 0.8])

    # yaw = 0 # left (2) right (-2)
    # pitch = 0 # up(-0.6) down (0.5)
    if direction is "right":
        angles = [[-0.3], [0]]
    elif direction is "left":
        angles = [[0.3], [0]]
    elif direction is "up":
        angles = [[0], [-0.2]]
    elif direction is "down":
        angles = [[0], [0.2]]
    else:
        angles = [[0], [0]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    motionProxy.setStiffnesses(["HeadYaw" "HeadPitch"], [0.0, 0.0])


def turn(theta, direction):
    turnRad = np.radians(theta)
    # turn in which direction
    if direction is "left":
        motionProxy.moveTo(0, 0, 0.5)
    elif direction is "random":
        leftRight = random.choice([-1, 1])
        motionProxy.moveTo(0, 0, 0.5 * leftRight)
    elif direction is "right":
        print "right direction"
        motionProxy.moveTo(0, 0, -turnRad)

    motionProxy.stopMove()

postureProxy.goToPosture("Stand", 0.6667)
look("left")
sleep(1)
look("right")
sleep(1)
postureProxy.goToPosture("Crouch", 0.6667)
motionProxy.rest()