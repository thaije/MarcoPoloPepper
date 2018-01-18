import multiprocessing, Queue, signal, sys, random, cv2
import time
from time import sleep
from naoqi import ALModule, ALProxy, ALBroker
#from ReactToTouch import *

ip = "192.168.1.115"
port = 9559


# general variables
duration = 20

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
# React to touch class
################################################################################

class ReactToTouch(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self.name = name
        self.parts = []

        print("ReactToTouch now initiated")
        memory.subscribeToEvent("TouchChanged", self.name, "onTouched")

    def onTouched(self, strVarName, value):
        print 'touched unsubscr: ', value
        memory.unsubscribeToEvent("TouchChanged", self.name)
        print 'touched bodyparts: ', value
        tts.say("you touched me!")
        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        self.parts = touched_bodies
        print touched_bodies
        # don't do something here with the touched bodyparts, you want to do this in the main and/or a behaviour thread!
        # note that the touched parts will be replaced every time
        memory.subscribeToEvent("TouchChanged", self.name, "onTouched")

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
# Main functions
################################################################################
def setup():
    global pythonBroker

    # add threads and thread variables here
    global exampleProcess, exampleVariable


    # Set robot to default posture
    postureProxy.goToPosture("Stand", 0.6667)
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    say("Initializing threads")

    # multithread variables
    manager = multiprocessing.Manager()
    exampleVariable = manager.Value('i', 0)

    # extra threads
    exampleProcess = multiprocessing.Process(name = "example-proc", target=exampleProc, args=(exampleVariable,))



def main():
    global pythonBroker
    # add threads and thread variables here
    global exampleProcess, exampleVariable

    try:
        # start threads
        #exampleProcess.start()
        #setup()

        # start timer
        start = time.time()
        end = time.time()


        pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)
        ReactToTouch = ReactToTouch("ReactToTouch")

        while end - start < duration:

            #print "Example variable is:" , exampleVariable.value
            if ReactToTouch.parts != []:
                print 'touched bodyparts are: \n', ReactToTouch.parts
                sleep(0.5)
                ReactToTouch.parts = [] # make the list empty
            else:
                print 'no touch occurred'

            # update time
            sleep(0.2)
            end = time.time()

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
