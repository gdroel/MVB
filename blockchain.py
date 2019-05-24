class Blockchain:
    def __init__(self):
        self.head = None

    def add_block(self, block):
        block.prev = self.head
        self.head = block

