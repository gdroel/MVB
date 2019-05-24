import json
import hashlib
import uuid
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

      print("select tranasction")

    # Check that a transaction is valid
    def validate_transaction(self):
        print("validate")
        

    # Verify the transaction through proof-of-work
    def verify_transaction(self):
        # for testing purposes only
        file = open("example_transaction.json")
        transactionJSON = file.read()

        # our hashed value neesd to be less than this   
        lessThan = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        # set the digest as the highest possible value so the loop runs at least once
        digest = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        print(lessThan)
        # keep generating values while it's less than this value
        while(digest > lessThan):
            # generate the nonce
            nonce = random.getrandbits(32)
            unhashed = transactionJSON + str(nonce)
            sha256 = hashlib.new("sha256")
            sha256.update(unhashed.encode('utf-8'))

            # convert digest to int for comparison
            digest = int(sha256.hexdigest(), 16)


def main():
    node = Node()
    node.select_transaction()
    node.select_transaction()

if __name__ == "__main__":
    main()