from naoqi import ALModule, ALProxy, ALBroker


################################################################################
# Sound localization
################################################################################
class SoundLocalization(ALModule):

    def __init__(self, name, memory):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        self.name = name
        self.azimuth = 0
        self.energy = 0
        self.memory = memory
        memory.subscribeToEvent("ALSoundLocalization/SoundLocated", name, "onLocalize")

    def onLocalize(self, parameter, value):
        try:
            self.memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocalization")

            # front el -0.3 (-17degrees)
            # top el -1.45 (should be 1.57 degrees)
            #
            # left az 1.25 (should be 1.57)
            # right az -1.25 (right should be -1.57)
            # behind az 3 (should be 3.14)
            # right az 4.5 (should be 4.7)

            self.azimuth = value[1][0]
            self.energy = value[1][3]
            # print "Azimuth ", value[1][0] , " elevation ", value[1][1] , " with energy:", value[1][3] , " with condifence", value[1][2]

            self.memory.subscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocalization", "onLocalize")
        except:
            # print "Oops error"
            pass
