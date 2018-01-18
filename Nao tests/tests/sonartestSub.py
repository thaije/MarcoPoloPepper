from naoqi import ALProxy, ALModule, ALBroker
from time import sleep

ip = "192.168.1.143"
port = 9559

# postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
# motionProxy = naoqi.ALProxy("ALMotion", ip ,port )

memory = ALProxy("ALMemory", ip, port)
sonar = ALProxy("ALSonar", ip, port)
pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)


class Sonar(ALModule):
    def __init__(self, strName):
        try:
            p = ALProxy(strName)
            p.exit()
        except:
            pass
        self.front = False
        ALModule.__init__(self, strName)
        self.memory = ALProxy("ALMemory")
        sonard = ALProxy("ALSonar")
        self.name = strName
        sonard.subscribe(strName)
        self.memory.subscribeToEvent("SonarLeftDetected", strName, "sonarLeft")
        self.memory.subscribeToEvent("SonarRightDetected", strName, "sonarRight")

    def sonarLeft(self, key, value, message):
        # motionProxy.stopMove()
        self.memory.subscribeToEvent("SonarLeftDetected", self.name)
        print "Something on the right, stop moving"
        self.memory.subscribeToEvent("SonarLeftDetected", self.name, "sonarLeft")

    def sonarRight(self, key, value, message):
        # motionProxy.stopMove()
        self.memory.subscribeToEvent("SonarRightDetected", self.name)
        print "Something on the right, stop moving"
        self.memory.subscribeToEvent("SonarRightDetected", self.name, "sonarRight")

sonars = Sonar("sonars")

i = 0
while i < 100:
    sleep(0.2)
