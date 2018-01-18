# Author        :   Tjalling Haije (s1011759)
# Date          :   11-01-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   Makes the Nao track a ball, and measure the ambient volume.
#                   Both are communicated to the user with the eye leds and speech.
#                   Red eye leds = no ball found
#                   Green eye leds = ball found and centered
#                   Blue eye leds = ball found but not centered
#                   A higher audio volume = higher LED intensity

# Notes         :   The location of the ball is spoken by the Nao, which also
#                   increases LED intensity.

# How to run    :   fix ip variable, then: python run.py

import multiprocessing, Queue, signal, sys
from time import time, sleep
import random
import cv2
import sys

import camera
from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559

# general variables
duration = 200
ballDetected = False

# camera variables
resolution = 1
resolutionX = 320
resolutionY = 240
ballThreshold = 35
foundBall = False
videoProxy = False
cam = False

# multithread variables
audioVolume = False
ballLocation = False
ballLocated = False

# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
LED = ALProxy("ALLeds", ip, port)
pythonBroker = False

# disable ALAutonomousMoves bug
am = ALProxy("ALAutonomousMoves", ip ,port )
am.setExpressiveListeningEnabled(False)
am.setBackgroundStrategy("none")

# threads
ballDetected = False
ballDetectionProcess = False
volLevelProcess = False



# righttop seen from front = 50, 50
# x = 0 = left
# x = 320 = right
# y = 0 = top
# y = 240 = bottom

################################################################################
# Ball searching and looking / sensing functions
################################################################################
def detectBallProcess(ballLocation, ballLocated):
    name = multiprocessing.current_process().name
    print name, " Starting"

    # setup camera stream
    videoProxy, cam = camera.setupCamera(ip, port)

    try:
        while True:
            # get and process a camera frame
            image = camera.getFrame(videoProxy, cam)
            if image is not False:
                # Check if we can find a ball, and point the head towards it if so
                ballDet = camera.findBall(image)

                if ballDet != False:
                    ballLocated.value = True
                    centerOnBall(ballDet, ballLocation)
                    print "Ball detected"
                else:
                    ballLocated.value = False
                    print "No ball detected"

                if cv2.waitKey(33) == 27:
                    videoProxy.unsubscribe(cam)
                    break;
            sleep(0.2)
    except:
        pass
    print name, " Exiting"



# Try to center the ball (with a certain threshold)
def centerOnBall(ballCoords, ballLocation):
    x = ballCoords[0]
    y = ballCoords[1]

    # -1=not found, 0=centered, 1=top, 2=right, 3=bottom, 4=left
    if x > (resolutionX/2 + ballThreshold):
        ballLocation.value = "right"
        # look("right")
    elif x < (resolutionX/2 - ballThreshold):
        ballLocation.value = "left"
        # look("left")
    elif y > (resolutionY/2 + ballThreshold):
        ballLocation.value = "down"
        # look("down")
    elif y < (resolutionY/2 - ballThreshold):
        ballLocation.value = "up"
    else:
        ballLocation.value = "centered"
        # look("up")


# look left look right
def lookAround():
    print("looking around")
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


# look a relative amount to the current head posture in a certain direction
def look(direction):
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.1], [0.1]] #time in seconds

    # yaw = 0 # left (2) right (-2)
    # pitch = 0 # up(-0.6) down (0.5)
    if direction is "right":
        angles = [[-0.3], [0]]
    if direction is "left":
        angles = [[0.3], [0]]
    elif direction is "up":
        angles = [[0], [-0.2]]
    elif direction is "down":
        angles = [[0], [0.2]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)



################################################################################
# General functions
################################################################################
def checkProxyDuplicates(name):
    try:
        p = ALProxy(name)
        p.exit()
    except:
        pass

def say(str):
    tts.say(str)
    print(str)



################################################################################
# Volume measurement thread
################################################################################
def volumeLevel(audioVolume):
    name = multiprocessing.current_process().name
    print name, " Starting"

    # global aud
    aud = ALProxy("ALAudioDevice", ip ,port )
    aud.enableEnergyComputation()

    try:
        while True:
            audioLevels = [aud.getFrontMicEnergy(), aud.getRightMicEnergy(), aud.getRearMicEnergy(), aud.getLeftMicEnergy()]
            audioVolume.value = max(audioLevels)
            sleep(0.2)
    except:
        pass

    print name, " Exiting"


################################################################################
# Communication functions
################################################################################
def changeLeds(intensity, color):
    if intensity > 5000:
        intensity = 1.0
    elif intensity < 500:
        intensity = 0
    else:
        intensity = intensity / 5000.0

    # print "Changing face leds to intensity ", intensity, " and color", color
    name = 'FaceLeds'
    red = intensity if color == "RED" else 0.0
    blue = intensity if color == "BLUE" else 0.0
    green = intensity if color == "GREEN" else 0.0
    duration = 0.2
    LED.fadeRGB(name, red, green, blue, duration)


################################################################################
# Main functions
################################################################################
def setup():
    global videoProxy, cam, pythonBroker, ballDetectionProcess, volLevelProcess, audioVolume, ballLocation, ballLocated

    manager = multiprocessing.Manager()
    audioVolume = manager.Value('i', 0)
    ballLocation = manager.Value('i', -1)
    ballLocated = manager.Value('i', False)

    # Set robot to default posture
    motionProxy.setStiffnesses("Head", 0.8)
    postureProxy.goToPosture("Stand", 0.6667)
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # video processing
    videoProxy, cam = camera.setupCamera(ip, port)
    sleep(1)

    ballDetectionProcess = multiprocessing.Process(name = "ball-detection-proc", target=detectBallProcess, args=(ballLocation, ballLocated,))
    volLevelProcess = multiprocessing.Process(name = "volume-measurement-proc", target=volumeLevel, args=(audioVolume,))



def main():
    global videoProxy, cam, ballDetectionProcess, volLevelProcess, pythonBroker, audioVolume, ballLocation, ballLocated
    setup()

    # start timer
    start = time()
    end = time()
    try:
        ballDetectionProcess.start()
        volLevelProcess.start()

        lastBallLocation = False
        eyesColor = "BLUE"
        while end - start < duration:

            # announce the location of the ball
            if not ballLocated.value and lastBallLocation:
                lastBallLocation = False
                tts.say("I lost the ball")
            elif ballLocated.value and lastBallLocation != ballLocation.value:
                lastBallLocation = ballLocation.value;
                tts.say("I see the ball " + ballLocation.value)

            # determine eye led colour
            if not ballLocated.value:
                eyesColor = "RED"
            elif ballLocation.value == "centered":
                eyesColor = "GREEN"
            else:
                eyesColor = "BLUE"

            changeLeds(audioVolume.value, eyesColor)
            print eyesColor + " eyes with vol ", audioVolume.value, " because ballLocated ", ballLocated.value , " and ballLocation ", ballLocation.value

            # update time
            sleep(0.2)
            end = time()

        say("This was my presentation")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print "Shutting down"
        postureProxy.goToPosture("Crouch", 0.6667)
        motionProxy.rest()
        videoProxy.unsubscribe(cam)
        ballDetectionProcess.terminate()
        volLevelProcess.terminate()
        pythonBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
