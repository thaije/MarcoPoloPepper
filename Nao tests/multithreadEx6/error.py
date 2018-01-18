import multiprocessing, Queue, time, signal, sys

from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.137"
port = 9559

global aud
LED = ALProxy("ALLeds", ip, port)
aud = ALProxy("ALAudioDevice", ip ,port )
aud.enableEnergyComputation()

def writer1(queue):
    name = multiprocessing.current_process().name
    print name, " Starting"

    # this without LED proxy works
    # aud = ALProxy("ALAudioDevice", ip ,port )
    # aud.enableEnergyComputation()


    while True:
        audioLevel = "not set"
        audioLevel =  aud.getFrontMicEnergy()
        print name , " sending audiolevel: ", audioLevel
        queue.put(audioLevel)
        time.sleep(1)
    print name, " Exiting"



def reader(queue1):
    name = multiprocessing.current_process().name
    time_out = 0.1
    print name, " Starting"
    msg1 = None
    while True:
        try:
            msg1 = queue1.get(True, time_out)
        except Queue.Empty:
            pass
        else:
            print "from queue1 received ", msg1
    print name, " Exiting"

if __name__ == "__main__":
    print "Starting"
    try:

        q1 = multiprocessing.Queue()
        wr1 = multiprocessing.Process(name = "writer1-proc", target=writer1, args=(q1,))
        rd = multiprocessing.Process(name = "reader-proc", target=reader, args=(q1,))

        wr1.start()
        rd.start()

        t=1
        while t < 4:
            time.sleep(1)
            print ""
            t += 1



        # Just exit
        wr1.terminate()
        rd.terminate()

        print "Done"

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating processes"
        wr1.terminate()
        rd.terminate()
