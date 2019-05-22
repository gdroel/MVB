import hashlib
import uuid
import random

class Node:
    def __init__(self):
        self.prev = "hashstring"

    # Select an unverified transaction at random from pool
    def select_transaction(self):
      print("select tranasction")

    # Check that a transaction is valid
    def validate_transaction(self):
        print("validate")
        """
        The transaction that is being transferred is addressed to Bob.
        Bob has not previously transfered the same transaction to anyone else.
        """

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

            






        

        

        
