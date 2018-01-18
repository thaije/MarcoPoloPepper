import multiprocessing
import time, sys
import Queue
from FaceRecognition import *

from naoqi import ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559

try:
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9600, ip, port)
    #videoProxy = ALProxy("ALVideoDevice", ip, port)
    tts = ALProxy("ALTextToSpeech", ip, port)
    #leds = ALProxy("ALLeds", ip, port)
    #audioProxy = ALProxy("ALAudioDevice", ip, port)
    motionProxy = ALProxy("ALMotion", ip, port)
    postureProxy = ALProxy("ALRobotPosture", ip, port)
    #soloProxy = ALProxy("ALSoundLocalization", ip, port)
    memory = ALProxy("ALMemory", ip, port)
    print "finished proxy setup"
except Exception, e:
    print "could not create all proxies"
    print "error was ", e
    sys.exit(1)

def __moveHead(x, y):
    joints = ["HeadYaw", "HeadPitch"]
    # there will be one moment in time for movement
    times = [[1.0], [1.0]]

    angles = [[x * .6], [y * .6]] # make the angle small, so nao does not make large and sudden movements

    # make actual movement,
    motionProxy.setStiffnesses(joints, 0.8)
    motionProxy.angleInterpolation(joints, angles, times, False)
    motionProxy.setStiffnesses(joints, 0.0)

def writer1(queue):
    FaceRecognizer = FaceRecognition(ip, port, memory, "FaceRecognizer")
    print "writer 1 has started"
    while True:
        if FaceRecognizer.hasrecognized:
            queue.put(FaceRecognizer.faceCoords())
        time.sleep(0.2)

def writer2(queue):
    print "writer 2 has started"
    i = 100
    while True:
        print "writer 2 putting in que: ", i
        queue.put(i)
        i += 10
        time.sleep(5)

def reader(queue1, queue2):
    print "reader has started"
    postureProxy.goToPosture("Stand", 0.3)
    time_out = 0.1
    msg1 = None
    msg2 = None
    while True:
        try:
            msg1 = queue1.get(True, time_out)
        except Queue.Empty:
            print "no message in queue 1"
        else:
            print "from queue 1 received ", msg1

        try:
            msg2 = queue2.get(True, time_out)
        except Queue.Empty:
            print "no message in queue 2"
        else:
            print "from queue 2 received ", msg2
            tts.say("let me have a look at you")
            x,y = msg2
            __moveHead(x,y)

        print "-------   READY FOR NEXT ITERATION -------"

# define variables
q1 = multiprocessing.Queue()
q2 = multiprocessing.Queue()

w1 = multiprocessing.Process(name='writer1-proc', target=writer1, args=(q1,))
w2 = multiprocessing.Process(name='writer2-proc', target=writer2, args=(q2,))
rdr = multiprocessing.Process(name='reader-proc', target=reader, args=(q1, q2,))

if __name__ == '__main__':
    try:
        # make sure autonomous movements are off
        am = ALProxy("ALAutonomousMoves", ip, port)
        am.setExpressiveListeningEnabled(False)
        am.setBackgroundStrategy("none")
    except:
        print "could not turn off autonomous movements"
        sys.exit(1)

    print 'starting'
    try:
        w1.start()
        w2.start()
        rdr.start()

        t=1
        while t<10: # during 10 seconds
            time.sleep(0.5)
            t+=1

        print 'reached timelimit, terminating process'
        w1.terminate()
        w2.terminate()
        rdr.terminate()
        postureProxy.goToPosture("Crouch", 0.2)
        motionProxy.rest()
        pythonBroker.shutdown()


    except KeyboardInterrupt:
        print "Caught keyboard interrupt, terminating processes"
        w1.terminate()
        w2.terminate()
        rdr.terminate()
        postureProxy.goToPosture("Crouch", 0.2)
        motionProxy.rest()
        pythonBroker.shutdown()

    except Exception, e:
        print "Caught exception, terminating processes"
        print "exception was ", e
        w1.terminate()
        w2.terminate()
        rdr.terminate()
        postureProxy.goToPosture("Crouch", 0.2)
        motionProxy.rest()
        pythonBroker.shutdown()

