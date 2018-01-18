import time
import sys
import naoqi

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

#ReactToTouch = None

ip = "192.168.1.115"
port = 9559


memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALSoundLocalization", ip, port)
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )

azimuth = 0

class SoundLocalization(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self.tts = ALProxy("ALTextToSpeech")
        self.name = name

        memory.subscribeToEvent("ALSoundLocalization/SoundLocated", name, "onLocalize")



    def onLocalize(self, parameter, value):
        try:
            memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocalization")

            # front el -0.3 (-17degrees)
            # top el -1.45 (should be 1.57 degrees)
            #
            # left az 1.25 (should be 1.57)
            # right az -1.25 (right should be -1.57)
            # behind az 3 (should be 3.14)
            # right az 4.5 (should be 4.7)

            global azimuth
            azimuth = value[1][0]
            print "Azimuth ", value[1][0] , " elevation ", value[1][1] , " with energy:", value[1][3] , " with condifence", value[1][2]

            memory.subscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocalization", "onLocalize")
        except:
            print "Oops error"



def azimuthToRotate(azimu):
    print "rotate with azimuth ", azimu
    motionProxy.moveTo(0, 0, azimu)






if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)
    SoundLocalization = SoundLocalization("SoundLocalization")

    postureProxy.goToPosture("Stand", 0.6667)

    try:
        while True:
            time.sleep(2)
            # print azimuth
            azimuthToRotate(azimuth)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"

        postureProxy.goToPosture("Crouch", 0.6667)
        motionProxy.rest()

        pythonBroker.shutdown()
        sys.exit(0)
