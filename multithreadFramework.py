import multiprocessing, Queue, signal, sys, random, cv2
import time
from time import sleep
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
    mainQueue = multiprocessing.Queue()

    # extra threads
    exampleProcess = multiprocessing.Process(name = "example-proc", target=exampleProc, args=(exampleVariable,))
    marcoPolo = multiprocessing.Process(name="MarcoPolo-proc", target=runMarcoPolo, args=(mainQueue,))


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
