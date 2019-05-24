import json
import random

class Node:
    def __init__(self):
        self.prev = "hashstring"
        self.current_transaction = None

    # Select an unverified transaction at random from pool
    def select_transaction(self):
        with open("unverified_pool.json") as file:
            data = json.load(file)
            random_index = random.randint(0, len(data) - 1)
            transaction = data[random_index]
            self.current_transaction = transaction
            print(self.current_transaction)


    # Check that a transaction is valid
    def validate_transaction(self):
        """
        The transaction that is being transferred is addressed to Bob.
        Bob has not previously transfered the same transaction to anyone else.
        """
        

    # # Verify the transaction through proof-of-work
    # def verify_transaction(self):


def main():
    node = Node()
    node.select_transaction()
    node.select_transaction()

if __name__ == "__main__":
    main()
