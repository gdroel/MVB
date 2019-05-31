from queue import Queue

class MainQueue(Queue):

    nodes = []

    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def put(self, item):
        for node in self.nodes:
            node.blockQueue.put(item, True, None)

        super().put(item, False)