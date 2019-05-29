# This is just me playing around with threads
import threading
import queue
import time

def thread_one(theQueue, event):
    for i in range(0,50):
        time.sleep(0.05)

    print(theQueue.get())
    theQueue.put("hello2")

def thread_two(theQueue, event):
    for i in range(0,75):
        # if event.is_set():
        #     print("block received in thread two")
        #     print(event.param)
        #     print("\n")
        #     return
        # else:
        time.sleep(0.05)

    print("done with thread two")
    print(theQueue.get())
    theQueue.put("hello3")



def thread_three(theQueue, event):
    for i in range(0,100):
        # if event.is_set():
        #     print("block received in thread three")
        #     print(event.param)
        #     return
        # else:
        time.sleep(0.05)
    
    
    print("done with thread three")

    print(theQueue.get())


event = threading.Event()
theQueue = queue.Queue()
theQueue.put("hello1")

# create all the threads 
threading.Thread(target = thread_one, args=[theQueue, event]).start()
threading.Thread(target = thread_two, args=[theQueue, event]).start()
threading.Thread(target = thread_three, args=[theQueue, event]).start()

# wait for all threads to exit
for t in threading.enumerate():
    if t != threading.current_thread():
        t.join()