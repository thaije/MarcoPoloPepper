import multiprocessing, Queue, signal, sys, random, cv2
from time import time, sleep
from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559


# general variables
duration = 20


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
    print(str)



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
    motionProxy.setStiffnesses("Head", 0.8)
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

    setup()

    # start timer
    start = time()
    end = time()
    try:
        # start threads
        exampleProcess.start()


        while end - start < duration:

            print "Example variable is:" , exampleVariable.value


            # update time
            sleep(0.2)
            end = time()

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
        exampleProcess.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
