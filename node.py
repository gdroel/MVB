import json
import hashlib
import uuid
import random
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from blockchain import Blockchain
from block import Block

class Node:
    def __init__(self):
        self.chain = Blockchain()
        self.current_transaction = None
        self.used_inputs = []
        self.initalize_chain()

    # Adds the Genesis Block as the first block in the chain
    def initalize_chain(self):
        with open("transaction_file.json") as file:
            data = json.load(file)
            self.current_transaction = data[0]
        self.create_block(0, 0)

    # This is the main code for the node
    def run():
        # Select a random transaction 
        self.select_transaction()
        # Validate the ransation
        self.validate_transaction()

        # Verify Transaction via POW
        self.verify_transaction()

        # Broadcast the mined block
        self.broadcast_transaction(self.chain.head)

        #4. Write to a file
        # Add the nonce and the final proof of work

    def broadcast_transaction(self, block):
        print("broadcast!")

    # Select an unverified transaction at random from pool
    def select_transaction(self):
        with open("unverified_pool.json") as file:
            data = json.load(file)
            random_index = random.randint(0, len(data) - 1)
            self.current_transaction = data[random_index]

    # Check that a transaction is valid
    def validate_transaction(self):
        input_blocks = []
        # Signature must be valid, inputs must not have been used before, coins in must equal coins out
        if self.validate_signature() and self.validate_input() and self.validate_coin_amount():
            # Add the transaction's inputs to the used input list
            for input_block in self.current_transaction["INPUT"]:
                self.used_inputs.append(input_block[0])
            print("Valid transaction")
            return True

        else:
            print("Invalid transaction")
            return False
        

    # Validate that a transaction's sigature is valid
    def validate_signature(self):
        verifying_key = None
        for input_block in self.current_transaction["INPUT"]:
            current_block = self.chain.head
            while current_block is not None:
                if input_block[0] == current_block.transaction["NUMBER"]:
                    verifying_key = VerifyingKey.from_string(bytes.fromhex(current_block.transaction["OUTPUT"][input_block[1]][0]))
                current_block = current_block.prev

        if verifying_key is not None:
            transaction_content = self.current_transaction["TYPE"]

            for input_block in self.current_transaction["INPUT"]:
                transaction_content += input_block[0]
                transaction_content += str(input_block[1])

            for output_set in self.current_transaction["OUTPUT"]:
                transaction_content += output_set[0]
                transaction_content += str(output_set[1])

            for signature in self.current_transaction["SIGNATURE"]:
                try:
                    verifying_key.verify(bytes.fromhex(signature), transaction_content.encode("utf-8"))
                    return True
                except BadSignatureError:
                    print("Invalid signature")
                    return False
        else:
            print("Input does not exist")
            return False

    # Validate that a transaction's inputs have not been previously used
    def validate_input(self):
        for input_block in self.current_transaction["INPUT"]:
            if input_block[0] in self.used_inputs:
                print("Input used previously")
                return False
        return True
    
    # Validate that the total amount of coins in a transaction's inputs equals the total amount of coins in its outputs
    def validate_coin_amount(self):
        input_sum = 0
        output_sum = 0
        for input_block in self.current_transaction["INPUT"]:
            current_block = self.chain.head
            while current_block is not None:
                if input_block[0] == current_block.transaction["NUMBER"]:
                    input_sum += current_block.transaction["OUTPUT"][input_block[1]][1]
                current_block = current_block.prev

        for output_block in self.current_transaction["OUTPUT"]:
            output_sum += output_block[1]

        if input_sum == output_sum:
            return True
        else:
            print("Input does not equal output")
            return False

    # Verify the transaction through proof-of-work
    def verify_transaction(self):

        # our hashed value neesd to be less than this   
        lessThan = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        # set the digest as the highest possible value so the loop runs at least once
        digest = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        # we keep track of the nonce
        nonce = 0

        # keep generating values while it's less than this value
        while(digest > lessThan):
            # generate the nonce
            nonce = random.getrandbits(32)
            unhashed = json.dumps(self.current_transaction) + str(nonce)
            sha256 = hashlib.new("sha256")
            sha256.update(unhashed.encode('utf-8'))

            # convert digest to int for comparison
            digest = int(sha256.hexdigest(), 16)
        self.create_block(nonce, digest)

    # Create a new block from a verified transaction
    def create_block(self, nonce, digest):
        new_block = Block(nonce, digest, self.current_transaction)
        self.chain.add_block(new_block)

    # Remove an invalid transaction from the network
    def remove_invalid_transaction(self):
        with open("unverified_pool.json", "r") as file:
            data = json.load(file)

        with open("unverified_pool.json", "w") as file:
            data = data.remove(self.current_transaction)
            new_pool = json.dumps(data)
            file.write(new_pool)

    # Start the node
    def run(self):
        self.select_transaction()
        if self.validate_transaction():
            self.verify_transaction()
        else:
            self.remove_invalid_transaction()