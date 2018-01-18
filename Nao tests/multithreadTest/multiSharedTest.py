import multiprocessing, Queue, time, signal, sys


def writer1(queue):
    name = multiprocessing.current_process().name
    print name, " Starting"
    i = 100
    while True:
        print name, " sending ", i
        queue.put(i)
        i += 1
        time.sleep(1)
    print name, " Exiting"


def writer2(queue):
    name = multiprocessing.current_process().name
    print name, " Starting"
    i = 0
    while True:
        print name, " sending ", i
        queue.put(i)
        i += 1
        time.sleep(3)
    print name, " Exiting"


def reader(queue1, queue2):
    name = multiprocessing.current_process().name
    time_out = 0.1
    print name, " Starting"
    msg1 = None
    msg2 = None
    while True:
        try:
            # get msg from queue.
            # If no msg -> block for time_out
            # if msg added -> handle
            # elif time_out over, throw queue.epty exception
            msg1 = queue1.get(True, time_out)
        except Queue.Empty:
            # if no msg has been added to the queue within time_out
            # seconds do this
            # print name, " no message in queue1"
            try:
                msg2 = queue2.get(True, time_out)
                print "from queue2 received ", msg2
            except Queue.Empty:
                blabla = "bla"
                # print name, " no message in queue2"
        else:
            # if msg has been added, handle it and sleep (non-blocking)
            print "from queue1 received ", msg1
    print name, " Exiting"

if __name__ == "__main__":
    print "Starting"
    try:

        q1 = multiprocessing.Queue()
        q2 = multiprocessing.Queue()
        writer1 = multiprocessing.Process(name = "writer1-proc", target=writer1, args=(q1,))
        writer2 = multiprocessing.Process(name = "writer2-proc", target=writer2, args=(q2,))
        reader = multiprocessing.Process(name = "reader-proc", target=reader, args=(q1, q2,))

        writer1.start()
        writer2.start()
        reader.start()

        t=1
        while t < 4:
            time.sleep(1)
            print "sleeping"
            t += 1

        # wait untill done and then exit
        # writer1.join()
        # writer2.join()
        # reader.join()

        # Just exit
        writer1.terminate()
        writer2.terminate()
        reader.terminate()

        print "----------"
        print "Exiting"

        while True:
            print "----------"
            print  "Is wr1 alive?", writer1.is_alive()
            print "Is wr2 alive?", writer2.is_alive()
            print "Is r alive?", reader.is_alive()
            time.sleep(0.5)

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating processes"
        writer1.terminate()
        writer2.terminate()
        reader.terminate()
