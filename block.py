from create_transaction import create_transaction

class Block:

    def __init__(self, nonce, proof_of_work, node_verifying_key, transaction):
        self.nonce = nonce
        self.proof_of_work = proof_of_work
        self.transactions = []
        self.node_verifying_key = node_verifying_key

        # not the genesis block
        if nonce != 0:
            self.add_coinbase_transaction()
        else:
            self.transactions.append("")
        self.transactions.append(transaction)
        self.prev = None

    def add_coinbase_transaction(self):
        create_transaction(None, self.transactions, [None], [(self.node_verifying_key, 25)], "COINBASE")
