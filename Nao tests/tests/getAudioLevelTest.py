from time import time, sleep
import random, sys
from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.143"
port = 9559


pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
memory = ALProxy("ALMemory", ip, port)
aud = ALProxy("ALAudioDevice", ip ,port )
aud.enableEnergyComputation()

i = 0.0
while i < 5.0:
    print "Audio level: %d %d %d %d" % ( aud.getFrontMicEnergy(), aud.getRightMicEnergy(), aud.getRearMicEnergy(), aud.getLeftMicEnergy())
    audioLevels = [aud.getFrontMicEnergy(), aud.getRightMicEnergy(), aud.getRearMicEnergy(), aud.getLeftMicEnergy()]
    maxAudioLevel = max(audioLevels)
    print "maxAudioLevel: ", int(maxAudioLevel)
    sleep(0.1)
    i += 0.1



pythonBroker.shutdown()
