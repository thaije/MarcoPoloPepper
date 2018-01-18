import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.143"
port = 9559

memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)


class FaceRecognition(ALModule):

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

        self.facep = ALProxy("ALFaceDetection", ip, port)
        self.facep.subscribe("Test_Face", 500, 0.0)
        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")

        print "initiliazed face recogntion"
        tts.say ("Checking for faces")



    def faceCall(self, eventName, value, subscriberIdentifier):
        memory.unsubscribeToEvent("FaceDetected", self.name)

        self.value = value
        print "Detected face"
        tts.say ("Hello handsome")

        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")


if __name__ == "__main__":

    # fucks up the asr module, better to restart
    # asr = ALProxy("ALSpeechRecognition", ip, port)
    # asr.pause(True)


    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    FaceDetector = FaceRecognition("FaceDetector")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        pythonBroker.shutdown()
        sys.exit(0)
