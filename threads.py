# This is just me playing around with threads
import threading
import time

def thread_one(event):
    for i in range(0,1000):
        if event.is_set():
            print("block received in thread one")
            print(event.param)
            print("\n")
            return
        else:
            time.sleep(0.05)

    event.set()

def thread_two(event):
    for i in range(0,8000):
        if event.is_set():
            print("block received in thread two")
            print(event.param)
            print("\n")
            return
        else:
            time.sleep(0.05)

    event.set()

def thread_three(event):
    for i in range(0,100):
        if event.is_set():
            print("block received in thread three")
            print(event.param)
            return
        else:
            time.sleep(0.05)

    print("Block sent from thread three")
    event.param = "Block: \nNonce = 0x00003289383298323\nPrevious Hash = 832489723acd8932"
    event.set()

event = threading.Event()
# create all the threads 
threading.Thread(target = thread_one, args=[event]).start()
threading.Thread(target = thread_two, args=[event]).start()
threading.Thread(target = thread_three, args=[event]).start()

# wait for all threads to exit
for t in threading.enumerate():
    if t != threading.current_thread():
        t.join()