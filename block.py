class Block:
    def __init__(self, nonce, proof_of_work, transaction):
        self.nonce = nonce
        self.proof_of_work = nonce
        self.transaction = transaction
        self.prev = None