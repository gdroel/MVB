from node import Node
import json
import threading
import queue

def main():

    with open("transaction_file.json") as transaction_file:
        data = json.load(transaction_file)
        with open("unverified_pool.json", "w") as unverified_pool:
            transactions = json.dumps(data[1:])
            unverified_pool.write(transactions)

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



if __name__ == "__main__":
    main()