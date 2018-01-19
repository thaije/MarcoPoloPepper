import multiprocessing, Queue, signal, sys, random, cv2
import time
import camera
from time import sleep
import numpy as np
from naoqi import ALModule, ALProxy, ALBroker
from ReactToTouch import *

ip = "192.168.1.115"
port = 9559


# general variables
duration = 20
time_out = 0.2

try:
    # proxies
    postureProxy = ALProxy("ALRobotPosture", ip ,port )
    motionProxy = ALProxy("ALMotion", ip ,port )
    touchProxy = ALProxy("ALTouch", ip, port)
    tts = ALProxy("ALTextToSpeech", ip , port )
    memory = ALProxy("ALMemory", ip, port)
    LED = ALProxy("ALLeds", ip, port)
    pythonBroker = False
except Exception, e:
    print "could not create all proxies"
    print "error was ", e
    sys.exit(1)

# disable ALAutonomousMoves bug
am = ALProxy("ALAutonomousMoves", ip ,port )
am.setExpressiveListeningEnabled(False)
am.setBackgroundStrategy("none")


# multithread variables
exampleVariable = False

# threads
exampleProcess = False



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
    print('saying: ',str)


################################################################################
# Example process
################################################################################
def exampleProc(exampleVariable):
    name = multiprocessing.current_process().name
    print name, " Starting"

    try:
        while True:
            exampleVariable.value += 1
            sleep(0.2)
    except:
        print "Error in process ", name
        pass

    print name, " Exiting"

################################################################################
# Detecting Balls Processes
################################################################################
# set balldetection variables
ballDetected = False
ballDetectionProcess = False
# camera variables
resolution = 1
resolutionX = 320
resolutionY = 240
ballThreshold = 35
foundBall = False
videoProxy = False
cam = False
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

def detectBallProcess(ballLocation, ballLocated, colour):
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
                    break
            sleep(0.2)
    except:
        videoProxy.unsubscribe(cam)
    videoProxy.unsubscribe(cam)
    print name, " Exiting"

################################################################################
# Marco Polo
################################################################################
def runMarcoPolo(queue):
    print 'running marco polo'
    tts.say("The rules are as follows")
    tts.say("First you hide somewhere in the room. I am still learning so not too difficult please..")
    tts.say("I call Marco")
    tts.say("And you respond with Polo!")

    # this is supposed to be the behavior process. This process will listen for certain events and perform certain
    # behaviors, like calling Marco and waiting for you to respond with Polo. This needs implementation still.
    wonMarcoPolo = False
    i = 0
    while True:
        if wonMarcoPolo:
            break
        i += 1
        if i >= 5:
            wonMarcoPolo = True
        queue.put(wonMarcoPolo)
        sleep(1)

    print 'exiting marco polo'

################################################################################
# I Spy With My Little Eye
################################################################################
# Choose the players. ...
# Select the first spy. ...
# Pick an object. ...
# Pick your first hint. ...
# Provide the first hint. ...
# Let each player guess. ...
# Provide another hint if necessary. ...
# Let the player who guesses correctly become the next spy.
def runLittleSpy(ballLocation, ballLocated):
    tts.say("We are playing I spy with my little eye")
    tts.say("These are the rules")
    tts.say("You will place several balls in the room")
    tts.say("You tell me the colour of the ball you picked")
    tts.say("Then I will try to find the ball you picked")
    tts.say("When I pick the wrong ball, you say WRONG!")
    tts.say("When I have found the right ball, you say CORRECT!")
    tts.say("We will play this game for three rounds.")
    tts.say("I hope you are ready!")
    sleep(1)

    # decide on the colours of the balls
    ballColours = ["pink" "red" "blue" "yellow" "orange" "green" "white" "purple"]

    for i in range(0,1): # every round do
        tts.say("pick a ball")
        ballColourDecided = False
        ballColour = ""
        # decide on the ballcolour to find!
        while not ballColourDecided:
            sleep(0.5)
            # TODO listen for the ball-colour
            ballColour = "blue" # TODO make this: = wordspotting ballcolours or something
            ballColourDecided = True

        tts.say("I will look for a ball that is " + ballColour)

        # look for the fucking ball, boyeah
        ballDetectionProcess = multiprocessing.Process(name="ball-detection-proc", target=detectBallProcess,
                                                       args=(ballLocation, ballLocated, ballColour,))
        ballDetectionProcess.start()
        while not ballLocated:
            # TODO while you haven't found the ball, look and turn around and check for balls
            sleep(0.1)

        ballDetectionProcess.terminate()
        tts.say("Is it that ball?")
        # TODO also look at the ball

        # listen for the answer and classify it as right or wrong
        correct = True # start with False
        # TODO listen for "correct" or "wrong"

        if correct:
            tts.say("yay!")
            break


################################################################################
# Main functions
################################################################################
def setup():
    global pythonBroker

    # add threads and thread variables here
    global exampleProcess, exampleVariable, mainQueue, marcoPolo


    # Set robot to default posture
    postureProxy.goToPosture("Stand", 0.6667)
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    say("Initializing threads")

    # multithread variables
    manager = multiprocessing.Manager()
    exampleVariable = manager.Value('i', 0)
    ballLocation = manager.Value('i', -1)
    ballLocated = manager.Value('i', False)
    mainQueue = multiprocessing.Queue()

    # extra threads
    exampleProcess = multiprocessing.Process(name = "example-proc", target=exampleProc, args=(exampleVariable,))
    marcoPolo = multiprocessing.Process(name="MarcoPolo-proc", target=runMarcoPolo, args=(mainQueue,))
    littleSpy = multiprocessing.Process(name="littleSpy-proc", target=runLittleSpy, args=(ballLocation, ballLocated,))


def main():

    global pythonBroker, ReactToTouch
    # add threads and thread variables here
    global exampleProcess, exampleVariable, marcoPolo, mainQueue

    try:
        # start threads
        setup()
        #exampleProcess.start()

        # start timer
        start = time.time()
        end = time.time()

        pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)
        ReactToTouch = ReactToTouch("ReactToTouch", memory)

        while end - start < duration:

            #print "Example variable is:" , exampleVariable.value
            if ReactToTouch.parts != []:
                print 'touched bodyparts are: \n', ReactToTouch.parts
                parts = ReactToTouch.parts
                ReactToTouch.parts = [] # make the list empty again
                for part in parts:
                    print 'current part is ', part
                    if "Head" in part:
                        print 'time for marco polo'
                        # make a process for Marco Polo
                        tts.say("lets play a game of Marco polo!")
                        marcoPolo.start()

                        while True:
                            try:
                                wonMP = mainQueue.get(True, time_out)
                            except Queue.Empty:
                                pass # do nothing
                            else:
                                if wonMP is True: # if you've won marcopolo, finish this part
                                    break
                        marcoPolo.join()
                        tts.say('that was fun!')
                        break # don't check other parts if you have already found a part
                    elif "Hand" in part:
                        # make a process for I Spy with my little Eye
                        tts.say("you choose to play I spy with my little eye")
                        tts.say("lets have some fun!")
                        break # don't check other parts if you have already found a part

            # update time
            sleep(0.2)
            end = time.time()

        ReactToTouch.unsubscribe()
        say("This was my presentation")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        say("Shutting down")
        # rest
        postureProxy.goToPosture("Crouch", 0.6667)
        motionProxy.rest()
        # stop threads
        #exampleProcess.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
