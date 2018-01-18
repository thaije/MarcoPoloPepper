import naoqi
ip = "192.168.1.102"
port = 9559

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )

# put in a stable position
# postureProxy.goToPosture("Sit", 0.8)
# motionProxy.rest()

# http://doc.aldebaran.com/2-1/family/robots/bodyparts.html#nao-effector

# yaw = 0 # left (2) right (-2)
# pitch = 0 # up(-0.6) down (0.5)
# speed = 0.6
# joints = ["HeadYaw", "HeadPitch"]
# angles = [yaw, pitch]

# non blocking
# motionProxy.setAngles(joints, angles, speed)


speed = 0.5
joints = ["HeadYaw", "HeadPitch"]
# joints = "HeadPitch"
angles = [[-1.0, 1.0, 0], [-0.2, 0]]
# angles = [-0.6, 0.5, 0]
times = [[2.0, 4.0, 5.0], [1.0, 5.0]] #time in seconds
isAbsolute = True

# motionProxy.setStiffnesses(joints, 0.8)


motionProxy.setStiffnesses("Head", 0.8)
motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

motionProxy.rest()
