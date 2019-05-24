class Block:
    def __init__(self, transaction):
        self.transaction = transaction
        self.prev = None