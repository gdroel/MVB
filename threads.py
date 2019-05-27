# This is just me playing around with threads

import threading
import time

def thread(event):
    for i in range(0,1000):
        if event.is_set():
            print(event.param)
            return
        else:
            time.sleep(0.05)

    event.set()


def other_thread(event):
    for i in range(0,8000):
        if event.is_set():
            print(event.param)
            print("fuck")
            return
        else:
            time.sleep(0.05)

    event.set()


def waiter_thread(event):
    for i in range(0,100):
        if event.is_set():
            print("event received in waiter")
            return
        else:
            time.sleep(0.05)

    event.param = "hello"
    event.set()

event = threading.Event()
threading.Thread(target = flagger_thread, args=[event]).start()
threading.Thread(target = waiter_thread, args=[event]).start()
threading.Thread(target = other_thread, args=[event]).start()

# wait for all threads to exit
for t in threading.enumerate():
    if t != threading.current_thread():
        t.join()