from node import Node
import json
import secrets
import time
import threading
import queue

def add_transaction(i):
    with open("transaction_file.json", "r") as transaction_file:
        data = json.load(transaction_file)
        with open("unverified_pool.json", "r") as current_pool:
            pool = json.load(current_pool)
            with open("unverified_pool.json", "w") as unverified_pool:
                transaction = data[i]
                pool.append(transaction)
                unverified_pool.write(json.dumps(pool))
    time.sleep(secrets.randbelow(200) / 100)

def main():
    with open("transaction_file.json", "r") as transaction_file:
        data = json.load(transaction_file)
        with open("unverified_pool.json", "w") as unverified_pool:
            unverified_pool.write(json.dumps([]))
        
    nodes = []

    # create all the nodes
    for i in range(0, 10):
        newNode = Node()
        nodes.append(newNode)

    # create the event
    event = threading.Event()

    blockQueue = queue.Queue()

    for node in nodes:
        # create all the threads 
        threading.Thread(target = node.run, args=[blockQueue]).start()

    i = 1
    while True:
        if i < 11:
            add_transaction(i)
        unverified_pool = open("unverified_pool.json", "r")
        transactions = json.load(unverified_pool)
        if len(transactions) == 0:
            break
        else:
            node.run()
        i += 1
    node.print_chain()

if __name__ == "__main__":
    main()