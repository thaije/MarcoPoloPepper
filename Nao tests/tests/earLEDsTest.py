import sys
from time import sleep
from naoqi import ALProxy
ip = "192.168.1.137"
port = 9559

try:
    LED = ALProxy("ALLeds", ip, port)
except Exception, e:
    print "Could not create proxy to ALLeds"
    print "Error was: ", # -*- coding: utf-8 -*-
    sys.exit(1)

# ear leds blink
LED.off("EarLeds")
sleep(0.05)
LED.on("EarLeds")


#  eye leds / blink
LED.off("FaceLeds")
sleep(0.15)
LED.on("FaceLeds")

# fade to black
name = 'FaceLeds'
red = 1.0
green = 0.0
blue = 0.0
duration = 0.5
LED.fadeRGB(name, red, green, blue, duration)

# fade to blue
# only blue works on some robots
name = 'EarLeds'
red = 1.0
green = 1.0
blue = 1.0
duration = 0.5
LED.fadeRGB(name, red, green, blue, duration)
