from naoqi import ALProxy
from naoqi import ALModule

import math
import time

class FaceRecognition(ALModule):
    def __init__(self,ip,port,memory, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self._hasrecognized = False
        self.value = []
        self.middleX = 0
        self.middleY = 0
        self.name = name
        self.memory = memory
        self.facep = ALProxy("ALFaceDetection", ip, port)
        self.facep.subscribe("Test_Face", 500, 0.0) # subscribe memory to faceproxy
        memory.subscribeToEvent("FaceDetected", "FaceRecognizer", "faceCall")

    # def __init__(self,x):
    #     self.__x = x
    #
    # def get_x(self):
    #     return self.__x
    #
    # def set_x(self, x):
    #     self.__x = x

    def hasrecognized(self):
        return self._hasrecognized

    def __set_hasrecognized(self, val):
        self._hasrecognized = val

    def faceCoords(self):
        return self.middleX, self.middleY

    def __faceCall(self, eventName, value, subscriberIdentifier):
        self.memory.unsubscribeToEvent("FaceDetected", "FaceRecognizer")

        if not self.hasrecognized:
            self.set_hasrecognized(True)
            self.value = value
            print("face recognized")

        try:
            leftEye = self.value[1][0][1][3]
            #rightEye = self.value[1][0][1][4]
            self.middleX = leftEye[0] # just use left eye as reference
            self.middleY = leftEye[1] # just use left eye as reference
            #self.moveHead(self.middleX, self.middleY)
        except:
            print("could not find eye coordinates")

        self.hasrecognized = False
        self.memory.subscribeToEvent("FaceDetected", "FaceRecognizer", "faceCall")