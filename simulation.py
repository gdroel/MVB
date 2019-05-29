from node import Node
import json
import secrets
import time
import threading
import queue

# def add_transaction(i):
#     with open("transaction_file.json", "r") as transaction_file:
#         data = json.load(transaction_file)
#                 transaction = data[i]
#                 pool.append(transaction)
#                 unverified_pool.write(json.dumps(pool))
#     time.sleep(secrets.randbelow(200) / 100)

def main():
    # with open("transaction_file.json", "r") as transaction_file:
    #     data = json.load(transaction_file)
    #     with open("unverified_pool.json", "w") as unverified_pool:
    #         unverified_pool.write(json.dumps([]))
        
    nodes = []

    # create all the nodes
    for i in range(0, 1):
        newNode = Node(i)
        nodes.append(newNode)

    # create the event
    event = threading.Event()

    blockQueue = queue.Queue()
    transaction_pool = []
    for node in nodes:
        # create all the threads 
        threading.Thread(target = node.run, args=[blockQueue, transaction_pool]).start()

    i = 1
    with open("transaction_file.json", "r") as transaction_file:
        data = json.load(transaction_file)
    while True:
        if i < 11:
            transaction = data[i]
            for j in range(1):
                transaction_pool.append(transaction)
                time.sleep(secrets.randbelow(200) / 100)
        if len(transaction_pool) == 0:
            blockQueue.put("Done")
            print("Sim exit")
            break
        i += 1

if __name__ == "__main__":
    main()