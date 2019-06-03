from queue import Queue

class MainQueue(Queue):

    nodes = []

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def put(self, item):
        print("pushed block from ", item[0], item[1].prev, item[1].transactions[1])
        for node in self.nodes:
            node.blockQueue.put(item[1], True, None)

        super().put(item[1], False)