import time
import sys
import naoqi

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

#ReactToTouch = None

ip = "192.168.1.103"
port = 9559

memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)

class ReactToTouch(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self.tts = ALProxy("ALTextToSpeech")

        memory.subscribeToEvent("TouchChanged", name, "onTouched")
        self.footTouched = False

    def onTouched(self, strVarName, value):
        memory.unsubscribeToEvent("TouchChanged", "ReactToTouch")

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        self.say(touched_bodies)

        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")

    def say(self, bodies):
        if bodies==[]:
            return
        sentence = "My " + bodies [0]
        for b in bodies[1:]:
            sentence = sentence + " and my " + b
        if len(bodies)>1:
            sentence = sentence + " are"
        else:
            sentence = sentence + " is"
        sentence = sentence + " touched I think."

        print sentence
        # self.tts.say(sentence)

if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)
    ReactToTouch = ReactToTouch("ReactToTouch")
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        pythonBroker.shutdown()
        sys.exit(0)
