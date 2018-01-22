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

    def subscribeTouch(self):
        self.memory.subscribeToEvent("TouchChanged", self.name, "onTouched")

    def onTouched(self, strVarName, value):
        try:
            self.memory.unsubscribeToEvent("TouchChanged", self.name)
            print 'touched: ', value
            touched_bodies = []
            for p in value:
                if p[1]:
                    touched_bodies.append(p[0])
            self.parts = touched_bodies
            print touched_bodies
            # don't do anything here with the touched bodyparts, you want to do this in the main and/or a behaviour thread!
            # note that the touched parts will be replaced every time

            # automatically re-subscribe to touch event
            self.memory.subscribeToEvent("TouchChanged", self.name, "onTouched")
        except:
            # print "Multiple touch events fired, but already unsubscribed after first event"
            pass

    def unsubscribeTouch(self):
        self.memory.unsubscribeToEvent("TouchChanged", self.name)
