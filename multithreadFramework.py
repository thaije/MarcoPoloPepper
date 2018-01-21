import multiprocessing, Queue, signal, sys, random, cv2
import time
import camera
from time import sleep
import numpy as np
from naoqi import ALModule, ALProxy, ALBroker
from ReactToTouch import *
from SoundLocalization import SoundLocalization
from wordSpotting import SpeechRecognition

# general variables
ip = "192.168.1.115"
port = 9559
duration = 20
time_out = 0.2

#initiate proxies
try:
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
azimuth = False
exitProcess = False

# threads
marcoPoloProcess = False

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

def detectBallProcess(ballLocation, ballLocated, ballColour):
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
                ballDet = camera.findBall(image, ballColour)

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
    print name, " Exiting"

################################################################################
# Marco Polo
################################################################################
# TODO ik heb een wonGame variabele gemaakt, maar ik denk dat die dezelfde functie heeft als jouw exitProcess? kijk er vooral even naar :)
def runMarcoPolo(queue, azimuth, exitProcess, wonGame):
    global SoundLocalization, Speecher
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
    name = multiprocessing.current_process().name
    print name, " Starting"

    print 'running marco polo'
    say("The rules are as follows")
    say("First you hide somewhere in the room.")
    say("I am still learning so don't make it too difficult please.")
    say("I call Marco")
    say("And you respond with Polo!")

    SoundLocalization = SoundLocalization("SoundLocalization", memory)
    Speecher = SpeechRecognition("Speecher", memory)
    Speecher.getSpeech(["stop", "marco", "polo"], True)

    nextAzimuth = 0
    try:
        while not exitProcess.value:
            # test speech recognition
            # print "Recognized word:"  , Speecher.recognizedWord
            # if Speecher.recognizedWord != False:
            #     word = Speecher.recognizedWord
            #     Speecher.recognizedWord = False
            #     say("Did you say" + word)
            # sleep(0.1)

            # Get a reply from the other person
            getPolo = waitForPolo(Speecher)
            while not getPolo:
                getPolo = waitForPolo(Speecher)

            print "I heard Polo"

            # Save the location of the speaker, and rotate to them
            print "Azimuth of speaker is:" + nextAzimuth
            nextAzimuth = SoundLocalization.azimuth
            azimuthToRotate(nextAzimuth)

    # except:
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print name, " Exiting"
        Speecher.stop()
        # TODO stop the broker??

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
def runLittleSpy(ballLocation, ballLocated, wonGame):
    # give instructions to the game
    say("We are playing I spy with my little eye")
    say("These are the rules")
    say("You will place several balls in the room")
    say("You tell me the colour of the ball you picked")
    say("Then I will try to find the ball you picked")
    say("When I pick the wrong ball, you say WRONG!")
    say("When I have found the right ball, you say CORRECT!")
    say("We will play this game for three rounds.")
    say("I hope you are ready!")
    sleep(1)

    # decide on the colours of the balls
    ballColours = ["pink" "red" "blue" "yellow" "orange" "green" "white"]
    Speecher = SpeechRecognition("Speecher", memory)

    for i in range(0,1): # every round do
        say("this is round " + str(i))
        say("Pick a ball")
        ballColourDecided = False
        ballColour = ""

        Speecher.getSpeech(ballColours, True)
        # TODO implement check on correct understanding of the colour? say("is this the correct colour") recognize yes/no?
        # decide on the ballcolour to find!
        while not ballColourDecided:
            if Speecher.recognizedWord is not False: #default is False
                ballColour = Speecher.recognizedWord
                Speecher.recognizedWord = False
                ballColourDecided = True
                Speecher.stop() # stop listening for the colour to detect
            sleep(0.5)

        say("I will look for a ball that is " + ballColour)
        # TODO make eyeleds same colour as the ball we are looking for? or too much effort for too little reward? :p

        # look for the fucking ball, boyeah
        ballDetectionProcess = multiprocessing.Process(name="ball-detection-proc", target=detectBallProcess,
                                                       args=(ballLocation, ballLocated, ballColour,))

        correct = False # start with False
        while not correct:
            # TODO this is a thread started in a thread, is that okay?? needs checking
            ballDetectionProcess.start()
            while not ballLocated:
                # TODO while you haven't found the ball, look and turn around and check for balls
                sleep(0.1)

            ballDetectionProcess.terminate()
            say("Is it that ball?")
            # TODO also point at the ball?

            # listen for the answer and classify it as right or wrong
            Speecher.getSpeech(["yes", "no", "correct", "wrong"], True)
            while True:
                if Speecher.recognizedWord is not False:
                    word = Speecher.recognizedWord
                    Speecher.recognizedWord = False
                    Speecher.stop()
                    if word == "true" or word == "correct":
                        correct = True
                    elif word == "no" or word == "wrong":
                        correct = False
                    break

            if correct:
                say("yay!")
                say("This is the end of the first round.")
                break
            else:
                say("Okay, I will continue my search for a " + ballColour + " ball.")


################################################################################
# Main functions
################################################################################
def setup():
    global pythonBroker
    # add threads here
    global marcoPolo, littleSpy
    # add thread variables here
    global mainQueue, azimuth, exitProcess, wonGame
    # TODO can you explain why these variables are both global and passed to the processes. shouldn't one of these be enough?

    # Set robot to default posture
    postureProxy.goToPosture("Stand", 0.6667)
    # TODO we have the pythonbroker now at three locations. make it generally defined in top?
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    say("Initializing threads")

    # multithread variables
    manager = multiprocessing.Manager()
    ballLocation = manager.Value('i', -1)
    ballLocated = manager.Value('i', False)
    mainQueue = multiprocessing.Queue()
    azimuth = manager.Value('i', 0)
    exitProcess = manager.Value('i', False)
    wonGame = manager.Value('i', False)

    # extra threads
    marcoPolo = multiprocessing.Process(name="MarcoPolo-proc", target=runMarcoPolo, args=(mainQueue,azimuth, exitProcess, wonGame,))
    littleSpy = multiprocessing.Process(name="littleSpy-proc", target=runLittleSpy, args=(ballLocation, ballLocated, wonGame,))


def main():
    global pythonBroker, ReactToTouch
    # add threads here
    global marcoPolo, littleSpy
    # add thread variables here
    global mainQueue, azimuth, exitProcess, wonGame

    try:
        # start threads
        setup()

        # start the process that responds to touch
        ReactToTouch = ReactToTouch("ReactToTouch", memory)
        ReactToTouch.subscribeTouch()
        # start timer
        start = time.time()
        end = time.time()

        while end - start < duration:
            # make sure wonGame is always False when starting a new round!
            wonGame = False
            if ReactToTouch.parts != []:
                print 'touched bodyparts are: \n', ReactToTouch.parts
                parts = ReactToTouch.parts
                ReactToTouch.parts = [] # make the list empty again
                for part in parts:
                    print 'current part is ', part
                    # touch when this is not an aspect of importance
                    if "Head" in part:
                        ReactToTouch.unsubscribeTouch()
                        print 'time for marco polo'
                        # make a process for Marco Polo
                        say("lets play a game of Marco polo!")
                        marcoPolo.start()

                        while True:
                            try:
                                wonMP = mainQueue.get(True, time_out)
                            except Queue.Empty:
                                pass # do nothing
                            else:
                                if wonMP: # if you've won marcopolo, finish this part
                                    break
                        marcoPolo.join()
                        say('that was fun!')
                        ReactToTouch.subscribeTouch()
                        break # don't check other the other parts in the list if you have already found a part
                    elif "Hand" in part:
                        ReactToTouch.unsubscribeTouch()
                        # make a process for I Spy with my little Eye
                        say("you choose to play I spy with my little eye")
                        say("lets have some fun!")

                        littleSpy.start()

                        ReactToTouch.subscribeTouch()
                        break # don't check other parts if you have already found a part

            # update time
            sleep(0.1)
            end = time.time()

        ReactToTouch.unsubscribe()
        say("Thank you for playing, I had a lot of fun!")
        say("I hope we can play again sometime.")
        say("Bye!")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        say("I am now shutting down.")
        exitProcess.value = True
        sleep(1.0)
        # rest
        postureProxy.goToPosture("Crouch", 0.6667)
        motionProxy.rest()
        # stop threads
        #exampleProcess.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
