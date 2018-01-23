from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559

postureProxy = ALProxy("ALRobotPosture", ip ,port )


def coverEyesPosture():
    # Choregraphe simplified export in Python.
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.0628932, -0.0628932, -0.0628932, -0.0628932])

    names.append("HeadYaw")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([0, 0, 0, 0])

    names.append("HipPitch")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.0460193, -0.0460193, -0.0460193, -0.0460193])

    names.append("HipRoll")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.00766993, -0.00766993, -0.00766993, -0.00766993])

    names.append("KneePitch")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.0107379, -0.0107379, -0.0107379, -0.0107379])

    names.append("LElbowRoll")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-1.43734, -1.43734, -1.43734, -1.43734])

    names.append("LElbowYaw")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-1.04617, -1.04617, -1.04617, -1.04617])

    names.append("LHand")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([0.490334, 0.490334, 0.490334, 0.490334])

    names.append("LShoulderPitch")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.082835, -0.082835, -0.082835, -0.082835])

    names.append("LShoulderRoll")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([0.00872665, 0.00872665, 0.00872665, 0.00872665])

    names.append("LWristYaw")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-1.37451, -1.37451, -1.37451, -1.37451])

    names.append("RElbowRoll")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([1.39132, 1.39132, 1.39132, 1.39132])

    names.append("RElbowYaw")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([0.961806, 0.961806, 0.961806, 0.961806])

    names.append("RHand")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([0.495606, 0.495606, 0.495606, 0.495606])

    names.append("RShoulderPitch")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.174874, -0.174874, -0.174874, -0.174874])

    names.append("RShoulderRoll")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([-0.0184078, -0.0184078, -0.0184078, -0.0184078])

    names.append("RWristYaw")
    times.append([1, 1.48, 1.96, 2.44])
    keys.append([1.37135, 1.37135, 1.37135, 1.37135])

    try:
      # uncomment the following line and modify the IP if you use this script outside Choregraphe.
      # motion = ALProxy("ALMotion", IP, 9559)
      motion = ALProxy("ALMotion", ip ,port )
      motion.angleInterpolation(names, keys, times, True)
    except BaseException, err:
      print err
