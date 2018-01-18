import multiprocessing
import Queue
import time, signal, sys, cv2
import numpy as np
import almath
import random
import naoqi
from naoqi import ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559

try:
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9600, ip, port)
    videoProxy = ALProxy("ALVideoDevice", ip, port)
    tts = ALProxy("ALTextToSpeech", ip, port)
    leds = ALProxy("ALLeds", ip, port)
    audioProxy = ALProxy("ALAudioDevice", ip, port)
    motionProxy = ALProxy("ALMotion", ip, port)
    postureProxy = ALProxy("ALPosture", ip, port)
    soloProxy = ALProxy("ALSoundLocalization", ip, port)
    memory = ALProxy("ALMemory", ip, port)
    print "finished proxy setup"
except Exception, e:
    print "could not create all proxies"
    print "error was ", e
    sys.exit(1)

# make sure you are able to listen to audio and decide on it's intensity
audioProxy.enableEnergyComputation()

# setting for video processing
cam_name = "camera" # identifier for cam subscription
cam_type = 0        # 0 for top camera, 1 for bottom camera
res = 1             # 320x240 (resolution)
colspace = 13       # BGR colorspace
fps = 10            # the requested frames per second

# unsubscribe all previous video proxies
cams = videoProxy.getSubscribers()
for cam in cams:
    videoProxy.unsubscribe(cam)

# subscribe wanted cam and set related variables
cam = videoProxy.subscribeCamera(cam_name, cam_type, res, colspace, fps)
# contains info on the image
width = 320
middle_width = width / 2
height = 240
middle_height = height / 2

# define the range of blues
lower_blue = np.array([70, 50, 50], dtype=np.uint8)
upper_blue = np.array([170, 255, 255], dtype=np.uint8)

kernel = np.ones((9, 9), np.uint8)

def recBlueBalls():
    try:
        # now take an image from the camera
        image_container = videoProxy.getImageRemote(cam)
        # and try recognize blue balls in the image
        values = map(ord, list(image_container[6]))
        image = np.array(values, np.uint8).reshape((height,width, 3))
        # determine threshold values
        # use HSV colorspace: hue saturation value
        # convert to hsv color space
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # create threshold mask
        color_mask = cv2.inRange(hsvImage, lower_blue, upper_blue)
        # remove small objects
        opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
        # close small openings
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        # apply blur to smooth edges
        smoothed_mask = cv2.GaussianBlur(closing, (9,9), 0)
        # # apply mask on image
        blue_image = cv2.bitwise_and(image, image, mask = smoothed_mask)
        # get grayscale
        gray_image = blue_image[:,:,2]

        # use hough transform to find circular objects in the image
        blue_circles = cv2.HoughCircles(
        gray_image,
        cv2.HOUGH_GRADIENT,
        1,
        5,
        param1=200,
        param2=20,
        minRadius=5,
        maxRadius=100
        )
        if blue_circles is not None:
            return True, blue_circles[0,:][0] # first blue circle that is being recognized
        return False,0
    except Exception,e:
        print "could not process image"
        print "error was ", e
        return None

def writer1(queue):
    # process that keeps tracking for blue balls
    # report ball location to queue
    name = multiprocessing.current_process().name
    print name, 'Starting'
    while True:
        blueballs = recBlueBalls()
        print "blueballs ", blueballs
        if blueballs is not None: # only send a message if the image was properly processed
            if blueballs[0]:
                i = blueballs[1][0],blueballs[1][1]
            else:
                i = 'no blue balls'

            print name, 'sending', i
            queue.put(i)
        time.sleep(1)
    #print name, 'Exciting'

def writer2(queue):
    # process that keeps listening to the sound volume in the room
    # report the volume to queue
    name = multiprocessing.current_process().name
    print name, 'Starting'
    while True:
        energy = audioProxy.getFrontMicEnergy()
        print "energy is ", energy
        if energy > 800:
            i = "high volume"
        elif energy <= 800  :
            i = "low volume"
        print name, 'sending', i
        queue.put(i)
        time.sleep(1)
    #print name, 'Exciting'

def writer3(queue):
    name = multiprocessing.current_process().name
    soloProxy.subscribe("")
    memory.subscribeToEvent("SoundLocated", "soLorecognizer", "locateSound")
    print name,  'Starting'
    while True:
        # do something to record audio, decide on location
        print 'waiting for audio'
        time.sleep(1)

def reader(queue1, queue2, queue3):
    # process that reads from two queues and decides on intensity and color of LED
    # blue ball in sight: blue light
    # blue ball out of sight: red light
    # low volume: low intensity
    # high volume: high intensity
    name = multiprocessing.current_process().name
    time_out = 0.1

    ledname =  'FaceLeds'
    intensity = 0.5 # low intensity
    red = intensity
    green = 0.0
    blue = 0.0
    duration = 0.5
    leds.fadeRGB(ledname, red, green, blue, duration)

    print name, 'Starting'
    msg1 = None
    msg2 = None
    msg3 = None
    while True:
        try:
            msg1 = queue1.get(True,time_out)
        except Queue.Empty:
            # if no message had been added to the queue within time_out:
            print name, 'no message in queue1'
        else: # if there is a message in queue 1
            print 'from queue1 received ', msg1
            if msg1 == "no blue balls":
                red = intensity
                blue = 0.0
            else:
                red = 0.0
                blue = intensity
                location = msg1
                print "blue ball is at ", location
        try:
            msg2 = queue2.get(True, time_out)
        except Queue.Empty:
            print name, 'no message in queue2'
        else:
            print 'from queue2 received ', msg2
            if msg2 == "low volume":
                intensity = 0.35
            elif msg2 == "high volume":
                intensity = 1.0
                print "intensity is now high"
        try:
            msg3 = queue3.get(True, time_out)
        except Queue.Empty:
            print name, 'no message in queue3'
        else:
            print 'from queue3 received ', msg3
            if msg3 == "low volume":
                intensity = 0.35
            elif msg3 == "high volume":
                intensity = 1.0
                print "intensity is now high"

        print "intensity ", intensity, " red ", red, " blue ", blue
        leds.fadeRGB(ledname, red, green, blue, duration)


# define variables
q1 = multiprocessing.Queue()
q2 = multiprocessing.Queue()
q3 = multiprocessing.Queue()

w1 = multiprocessing.Process(name='writer1-proc', target=writer1, args=(q1,))
w2 = multiprocessing.Process(name='writer2-proc', target=writer2, args=(q2,))
w3 = multiprocessing.Process(name='writer3-proc', target=writer3, args=(q3,))
rdr = multiprocessing.Process(name='reader-proc', target=reader, args=(q1, q2, q3,))

if __name__ == '__main__':
    print 'starting'
    try:
        # w1.start()
        # w2.start()
        # w3.start()
        # rdr.start()
        #
        # t=1
        # while t<30: # during 30 seconds
        #     time.sleep(1)
        #     t+=1
        #
        # print 'reached timelimit, terminating process'
        # w1.terminate()
        # w2.terminate()
        # w3.terminate()
        # rdr.terminate()
        tts.say("hi tjalling")

    except KeyboardInterrupt:
        print "Caught keyboard interrupt, terminating processes"
        # w1.terminate()
        # w2.terminate()
        # w3.terminate()
        # rdr.terminate()

    videoProxy.unsubscribe(cam)
    pythonBroker.shutdown()