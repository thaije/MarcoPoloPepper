from naoqi import ALModule, ALProxy, ALBroker


ip = "192.168.1.115"
port = 9559

postureProxy = ALProxy("ALRobotPosture", ip ,port )
navigationProxy = ALProxy("ALNavigation", ip, port)


# postureProxy.goToPosture("Stand", 0.6667)


# if( navigationProxy.navigateTo(2.0, 0) ):
#     print "succes"
# else:
#     print "couldn't find path"


# postureProxy.goToPosture("Crouch", 0.6667)
