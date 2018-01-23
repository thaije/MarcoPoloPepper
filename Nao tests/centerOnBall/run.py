# Author        :   Tjalling Haije (s1011759)
# Date          :   05-12-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   Makes the NAO walk around, track a blue ball, react to
#                   speech commands and touch. For specifics see report.txt
# How to run    :   fix ip variable, then: python run.py


from time import time, sleep
import random
import cv2
import sys

import camera
from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.143"
port = 9559

duration = 200

# walking variables
walkSpeed = 0.6
turnSpeed = 0.5
blocked = True
walking = False

# camera variables
resolution = 1
resolutionX = 320
resolutionY = 240
ballThreshold = 25
foundBall = False
videoProxy = False
cam = False

# lists with events to listen to
wordlist = ["left", "right", "stop", "start"]
importantBumpers = ('RFoot/Bumper/Left', 'RFoot/Bumper/Right','LFoot/Bumper/Left', 'LFoot/Bumper/Right')

# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
sonar = ALProxy("ALSonar", ip, port)

# disable ALAutonomousMoves bug during listening
am = ALProxy("ALAutonomousMoves", ip ,port )
am.setExpressiveListeningEnabled(False)
am.setBackgroundStrategy("none")

ReactToTouch = False
Speecher = False
pythonBroker = False

sonarLeftHistory = 1000
sonarRightHistory = 1000

################################################################################
# Class for recognizing speech
################################################################################
class SpeechRecognition(ALModule):

    def __init__(self, name):
        checkProxyDuplicates(name)
        ALModule.__init__(self, name)
        self.response = False
        self.value = []
        self.name = name
        self.wordlist = []
        self.wordspotting = False
        self.spr = ALProxy("ALSpeechRecognition")


    def getSpeech(self, wordlist, wordspotting):
        self.response = False
        self.value = []
        self.wordlist = wordlist
        self.wordspotting = wordspotting

        self.spr.setVocabulary(self.wordlist, self.wordspotting)
        memory.subscribeToEvent("WordRecognized", self.name, "onDetect")


    def onDetect(self, keyname, value, subscriber_name):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)

        self.response = True
        self.value = value
        val = value[0].replace('<...>', '')
        val = val.strip()
        # print val
        # tts.say ("I think you said. " + val)

        global blocked
        if val == "stop":
            say("Command received, stopping")
            stopWalking()
            blocked = True

        if val == "left":
            say("Command received, looking left")
            look("left")

        if val == "right":
            say("Command received, looking right")
            look("right")

        if val == "start" and not walking:
            say("Command received, starting")
            initRandomWalk()

        self.getSpeech(self.wordlist, self.wordspotting)

    def stop(self):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)



################################################################################
# Class for catching touch events
################################################################################
class ReactToTouch(ALModule):

    def __init__(self, name):
        checkProxyDuplicates(name)
        ALModule.__init__(self,name)

        memory.subscribeToEvent("TouchChanged", name, "onTouched")
        self.footTouched = False


    def onTouched(self, strVarName, value):
        memory.unsubscribeToEvent("TouchChanged", "ReactToTouch")

        # check which bodies were touched
        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])

        # if touch is leftFoot or touch is rightFoot, do avoid behaviour
        if any(event in importantBumpers for event in touched_bodies):
            say("Oh no my foot hit something, avoiding")
            avoid(True, "random")
            initRandomWalk()

        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")


################################################################################
# Locomotion functions
################################################################################
def initRandomWalk():
    say("Continuing")
    motionProxy.moveToward(walkSpeed, 0, 0)
    global walking, blocked
    walking = True
    blocked = False


def stopWalking():
    global walking
    walking = False
    motionProxy.stopMove()
    postureProxy.goToPosture("StandInit", 0.6667)


def turn(theta, direction):
    global walking
    walking = True

    # turn in which direction
    if direction is "left":
        motionProxy.moveToward(0, 0, turnSpeed * 1)
    elif direction is "random":
        leftRight = random.choice([-1, 1])
        motionProxy.moveToward(0, 0, turnSpeed * leftRight)
    elif direction is "right":
        motionProxy.moveToward(0, 0, turnSpeed * -1)

    # turn x degrees = wait n seconds
    if theta is 45:
        sleep(4)
    motionProxy.stopMove()


def backwards():
    global walking
    walking = True
    motionProxy.moveToward(-1 * walkSpeed, 0, 0)
    sleep(4)
    stopWalking()


def avoid(backward, direction):
    # block the main loop
    global blocked, foundBall
    blocked = True
    foundBall = False

    stopWalking()
    postureProxy.goToPosture("StandInit", 0.6667)

    if backward:
        backwards()
    turn(45, direction)
    initRandomWalk()

################################################################################
# Ball searching and looking / sensing functions
################################################################################
def onBallDetect(ballDetection):
    global foundBall

    if ballDetection is False:
        # announce we lost the ball
        if foundBall:
            foundBall = False
            say("Lost ball")
    else:
        # Announce that we found the ball
        if not foundBall:
            foundBall = True
            say("Found a ball, centering on ball")
            stopWalking()
        # center on the ball
        print("Centering on ball at ", ballDetection[0],  ballDetection[1])
        centerOnBall(ballDetection[0], ballDetection[1])


# Try to center the ball (with a certain threshold)
def centerOnBall(x, y):
    if x > (resolutionX/2 + ballThreshold):
        look("right")
    elif x < (resolutionX/2 - ballThreshold):
        look("left")
    elif y > (resolutionY/2 + ballThreshold):
        look("down")
    elif y < (resolutionY/2 - ballThreshold):
        look("up")


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
    else:
        angles = [[0], [0]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


def updateSonar():
    global sonarLeftHistory, sonarRightHistory, blocked

    if blocked:
        return False

    left = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    right = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")

    print "Left sonar:", left , " previous:", sonarLeftHistory
    print "Right sonar:", right, " previous:", sonarRightHistory

    if left < 0.7 and sonarLeftHistory < 0.7:
        blocked = True
        stopWalking()
        say("object detected on left with sonar, avoiding")
        avoid(False, "right")
    elif right < 0.7 and sonarRightHistory < 0.7:
        blocked = True
        stopWalking()
        say("object detected on right with sonar, avoiding")
        avoid(False, "left")

    sonarLeftHistory = left
    sonarRightHistory = right

    # sonarHistory.pop(0)
    # sonarHistory.append

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

# def onSonarDetect():
#     avoid(False)
#     say("I sensed an object with sonar, avoiding")


################################################################################
# Main functions
################################################################################
def setup():
    global videoProxy, cam, ReactToTouch, Speecher, pythonBroker

    say("You can give me commands during walking, such as left, right, stop and start.")

    # Set robot to default posture
    motionProxy.setStiffnesses("Head", 0.8)
    postureProxy.goToPosture("StandInit", 0.6667)
    sleep(2)

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # video processing
    videoProxy, cam = camera.setupCamera(ip, port)

    # speecher
    Speecher = SpeechRecognition("Speecher")
    Speecher.getSpeech(wordlist, True)

    # Touch sensors
    ReactToTouch = ReactToTouch("ReactToTouch")

    # sonars
    sonar.subscribe("myS")

def main():
    global videoProxy, cam, blocked
    setup()

    say("Please give me the command start, to start")

    # start timer
    start = time()
    end = time()

    try:
        while end - start < duration:

            updateSonar()

            # get and process a camera frame
            image = camera.getFrame(videoProxy, cam)
            if image is not False:
                # Check if we can find a ball, and point the head towards it if so
                ballDet = camera.findBall(image)
                if not blocked:
                    onBallDetect(ballDet)

            # close the video proxy and end the script if escape is pressed
            if cv2.waitKey(33) == 27:
                videoProxy.unsubscribe(cam)
                break;

            # start a random walk
            if not walking and not blocked and not foundBall:
                initRandomWalk()

            # look around if we are not doing much special
            if not blocked and not foundBall:
                # look around
                lookAround()

            # update time
            end = time()

        say("This was my presentation")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        say("Shutting down after sitting")
        videoProxy.unsubscribe(cam)
        postureProxy.goToPosture("SitRelax", 0.6667)
        motionProxy.rest()
        Speecher.stop()
        sonar.unsubscribe("myS")
        pythonBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
