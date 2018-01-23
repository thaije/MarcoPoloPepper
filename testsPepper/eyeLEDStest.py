import multiprocessing, Queue, signal, sys, random, cv2, math
import time
from time import sleep
import numpy as np
from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.115"
port = 9559

LED = ALProxy("ALLeds", ip, port)

def setEyeLeds(colour, intensity):
    if colour == "red":
        LED.fadeRGB('FaceLeds', intensity, 0, 0, 0.5)
    elif colour == "blue":
        LED.fadeRGB('FaceLeds', 0, 0, intensity, 0.5)
    elif colour == "green":
        LED.fadeRGB('FaceLeds', 0, intensity, 0, 0.5)
    elif colour == "pink":
        LED.fadeRGB('FaceLeds', intensity, 0.01 * intensity, 0.58 * intensity, 0.5)
    elif colour == "yellow":
        LED.fadeRGB('FaceLeds', intensity, intensity, 0.0, 0.5)
    elif colour == "none":
        LED.fadeRGB('FaceLeds', intensity, intensity, intensity, 0.5)
    else:
        print "Sorry, I don't know that colour"

setEyeLeds("yellow", 1.0)
sleep(3)