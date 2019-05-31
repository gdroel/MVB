from node import Node
import json
import secrets
import time
import threading
import queue
from MainQueue import MainQueue


def main():
    nodes = []

    # create all the nodes
    for i in range(0, 10):
        newNode = Node(i, False)
        nodes.append(newNode)

    main_queue = MainQueue(nodes)
    transaction_pool = []
    for node in nodes:
        # create all the threads 
        threading.Thread(target = node.run, args=([transaction_pool, main_queue])).start()

    i = 1
    with open("transaction_file.json", "r") as transaction_file:
        data = json.load(transaction_file)
    is_done = False
    while not is_done:
        if i < 11:
            transaction = data[i]
            transaction_pool.append(transaction)
            time.sleep(secrets.randbelow(200) / 100)
        if len(transaction_pool) == 0:
            is_done = True
            for node in nodes:
                node.is_done = True
            print("Sim exit")
        i += 1

if __name__ == "__main__":
    main()