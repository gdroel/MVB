from create_transaction import *

class Block:

    def __init__(self, nonce, proof_of_work, node_verifying_key, transaction):
        self.nonce = nonce
        self.proof_of_work = proof_of_work
        self.transactions = []
        self.node_verifying_key = node_verifying_key
        self.add_coinbase_transaction()
        self.transactions.append(transaction)
        self.prev = None

        print("NODE TRANSACTIONS")
        print(self.transactions)

    def add_coinbase_transaction(self):
        create_transaction(None, self.transactions, [None], [(self.node_verifying_key, 30)], "COINBASE")
