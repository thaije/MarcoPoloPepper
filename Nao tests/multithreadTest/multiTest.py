import multiprocessing, Queue, time


def function_x(t1, t2):
    # while True:
    print t1, t2
    time.sleep(0.5)

arg1 = "t1"
arg2 = "t2"

proc1 = multiprocessing.Process(name='process-name', target=function_x, args=(arg1, arg2))

proc1.start()

i = 0
while i < 3:
    time.sleep(0.5)
    print "sleeping"
    i += 0.5

time.sleep(3)

print "Done"

proc1.terminate()

# i = 0
# while True:
#     time.sleep(0.5)
#     print "Is alive?", proc1.is_alive()
#     i += 0.5
