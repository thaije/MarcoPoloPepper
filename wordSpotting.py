from naoqi import ALModule, ALProxy, ALBroker


class SpeechRecognition(ALModule):

    def __init__(self, name, memory):
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
        self.memory = memory
        self.recognizedWord = False
        self.spr = ALProxy("ALSpeechRecognition")
        print "Setting up word spotting"


    def getSpeech(self, wordlist, wordspotting):
        self.response = False
        self.value = []
        self.wordlist = wordlist
        self.wordspotting = wordspotting

        # print "Set get speech"

        self.spr.setVocabulary(self.wordlist, self.wordspotting)
        self.memory.subscribeToEvent("WordRecognized", self.name, "onDetect")

    def onDetect(self, keyname, value, subscriber_name):
        try:
            self.memory.unsubscribeToEvent("WordRecognized", self.name)
            self.spr.pause(True)

            self.response = True
            self.value = value
            val = value[0].replace('<...>', '')
            val = val.strip()
            self.recognizedWord = val
            # print "Detected in word spotting", value[0]

            self.getSpeech(self.wordlist, self.wordspotting)
        except:
            # print "Word spotting error"
            pass

    def stop(self):
        try:
            self.memory.unsubscribeToEvent("WordRecognized", self.name)
        except:
            pass
        self.spr.pause(True)
        try:
            p = ALProxy("ALSpeechRecognition")
            p.quit()
        except:
            pass
