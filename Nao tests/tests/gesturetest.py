import naoqi
ip = "192.168.1.143"
port = 9559

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )

postureProxy.goToPosture("Stand", 0.8)

leftJoints = [ "LShoulderRoll" , "LShoulderPitch" , "LElbowYaw" ,
"LElbowRoll" , "LWristYaw" ]
angles = [ -0.15 , -0.45 , -0.3 , -0.5 , -0.1]
times = [ 1.0 , 1.0 , 1.0 , 1.0 , 1.0 ]
isAbsolute = True
motionProxy.setStiffnesses(leftJoints, 0.8 )
motionProxy.angleInterpolation(leftJoints, angles, times, isAbsolute)

postureProxy.goToPosture("Stand", 0.8)
motionProxy.rest()
