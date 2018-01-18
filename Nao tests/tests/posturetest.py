import naoqi
ip = "192.168.1.143"
port = 9559

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )



postureProxy.goToPosture("Stand" ,0.6667)

postureProxy.goToPosture("SitRelax" ,0.6667)

motionProxy.rest()
