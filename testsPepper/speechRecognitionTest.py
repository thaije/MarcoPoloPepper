# Author        :   Tjalling Haije (s1011759)
# Date          :   21-11-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   File which makes the robot to the words left, right
#                   and stop.


import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.115"
port = 9559

memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)

class SpeechRecognition(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass

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
        print value[0]
        tts.say ("Did you say " + value[0] + "?")

        self.getSpeech(self.wordlist, self.wordspotting)

    def stop(self):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)

if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)


    # fucks up the asr module, better to restart
    asr = ALProxy("ALSpeechRecognition", ip, port)
    asr.pause(True)
    #
    # pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
    Speecher = SpeechRecognition("Speecher")
    Speecher.getSpeech(["stop", "marco", "polo"], True)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        Speecher.stop()
        pythonBroker.shutdown()
        sys.exit(0)
