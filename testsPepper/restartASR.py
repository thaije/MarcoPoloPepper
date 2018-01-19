
import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.115"
port = 9559

memory = ALProxy("ALMemory", ip, port)

pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)

asr = ALProxy("ALSpeechRecognition", ip, port)
asr.pause(True)

print "ASR restarted"
