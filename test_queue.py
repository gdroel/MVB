from node import Node
from MainQueue import MainQueue

nodes = []

# create all the nodes
for i in range(0, 10):
    newNode = Node(i, False)
    nodes.append(newNode)

main_queue = MainQueue(nodes)
main_queue.put("hi")

for node in nodes:
    print(node.blockQueue.get())

