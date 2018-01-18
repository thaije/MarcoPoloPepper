from naoqi import ALModule, ALProxy
import time

class ReactToTouch(ALModule):

    def __init__(self, name, memory):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self.name = name

        self.memory = memory
        self.parts = []

        print("ReactToTouch now initiated")
        memory.subscribeToEvent("TouchChanged", self.name, "onTouched")

    def onTouched(self, strVarName, value):
        self.memory.unsubscribeToEvent("TouchChanged", self.name)
        print 'touched: ', value
        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        self.parts = touched_bodies
        print touched_bodies
        # don't do something here with the touched bodyparts, you want to do this in the main and/or a behaviour thread!
        # note that the touched parts will be replaced every time
        self.memory.subscribeToEvent("TouchChanged", self.name, "onTouched")

    def unsubscribe(self):
        self.memory.unsubscribeToEvent("TouchChanged", self.name)

    # def say(self, bodies):
    #     if bodies==[]:
    #         return
    #     sentence = "My " + bodies [0]
    #     for b in bodies[1:]:
    #         sentence = sentence + " and my " + b
    #     if len(bodies)>1:
    #         sentence = sentence + " are"
    #     else:
    #         sentence = sentence + " is"
    #     sentence = sentence + " touched."
    #
    #     self.tts.say(sentence)