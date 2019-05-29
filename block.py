class Block:
    def __init__(self, nonce, proof_of_work, transaction):
        self.nonce = nonce
        self.proof_of_work = proof_of_work
        self.transaction = transaction
        self.prev = None