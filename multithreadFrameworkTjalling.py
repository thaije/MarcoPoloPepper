import multiprocessing, Queue, signal, sys, random, math, cv2
from time import time, sleep
from naoqi import ALModule, ALProxy, ALBroker

from SoundLocalization import SoundLocalization

ip = "192.168.1.115"
port = 9559


# general variables
duration = 60

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
azimuth = False

# threads
exampleProcess = False
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
    print(str)

def rotateToVoice(azimu):
    print "rotate with azimuth ", azimu
    motionProxy.moveTo(0, 0, azimu)




################################################################################
# Sound localization process
################################################################################
def marcoPoloProc(azimuth):
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
    global SoundLocalization

    name = multiprocessing.current_process().name
    print name, " Starting"

    SoundLocalization = SoundLocalization("SoundLocalization", memory)

    try:
        while True:
            sleep(0.2)
            print "Azimuth:", SoundLocalization.azimuth
            azimuth.value = SoundLocalization.azimuth
            # azimuthToRotate(azimuth)
    except:
        print "Error in process ", name
        pass

    print name, " Exiting"






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
    global exampleProcess, exampleVariable, marcoPoloProcess, azimuth


    # Set robot to default posture
    motionProxy.setStiffnesses("Head", 0.8)
    postureProxy.goToPosture("Stand", 0.6667)
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    say("Initializing threads")

    # multithread variables
    manager = multiprocessing.Manager()
    exampleVariable = manager.Value('i', 0)
    azimuth = manager.Value('i', 0)

    # extra threads
    exampleProcess = multiprocessing.Process(name = "example-proc", target=exampleProc, args=(exampleVariable,))
    marcoPoloProcess = multiprocessing.Process(name = "marco-polo-proc", target=marcoPoloProc, args=(azimuth,))


def main():
    global pythonBroker
    # add threads and thread variables here
    global exampleProcess, exampleVariable, marcoPoloProcess, azimuth

    setup()

    # start timer
    start = time()
    end = time()
    try:
        # start threads
        exampleProcess.start()
        marcoPoloProcess.start()

        print "Pepper doing startup move.."
        # sleep(4)

        print "moving"
        # X = forward speed = forward = 1.0, backward = -1.0
        # X = 0.5
        # Y = Sidewards speed = # 1.0 = counter-clockwise, -1.0 = clockwise
        # Y = 0
        # Theta = Rotation speed = # 1.0 = counter-clockwise, -1.0 clockwise
        # Theta = 0
        # motionProxy.moveToward(0.5, 0, 0)
        # sleep(2.0)
        # motionProxy.stopMove()


        # x - Distance along the X axis in meters.
        # y - Distance along the Y axis in meters.
        # theta - Rotation around the Z axis in radians [-3.1415 to 3.1415].
        # motionProxy.moveTo(0, 0, math.pi * 1.5)

        while end - start < duration:

            print "Azimuth variable is:" , azimuth.value

            rotateToVoice(azimuth.value)

            # update time
            sleep(1.0)
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
        marcoPoloProcess.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
