import json
import hashlib
import uuid
import secrets
import random
import time
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from blockchain import Blockchain
from block import Block
import threading

lock = threading.Lock()

class Node:
	def __init__(self, id, is_done):
		self.chain = Blockchain()
		self.current_transaction = None
		self.used_inputs = []
		self.initalize_chain()
		self.id = id
		self.is_done = is_done

	# Adds the Genesis Block as the first block in the chain
	def initalize_chain(self):
		with open("transaction_file.json") as file:
			data = json.load(file)
			self.current_transaction = data[0]
		self.create_block(0, 0)

	def run(self, transaction_pool, blockQueue):
		while(not self.is_done):
			print("testing")
			if self.select_transaction(transaction_pool):
				print(self.current_transaction)
				# Validate the transaction
				if self.validate_transaction():
					# Verify Transaction via POW
					verify_result = self.verify_transaction(blockQueue)

					if verify_result == False:
						# A block was received
						block = blockQueue.get()
						self.handle_received_block(transaction_pool, block)
					else:
						# Broadcast the mined block
						self.broadcast_block(transaction_pool, blockQueue)
				else: # Remove an invalid transaction from the pool
					self.remove_transaction(transaction_pool, self.current_transaction)
		self.print_chain()

	def handle_received_block(self, transaction_pool, block):
		print("block received")
		self.chain.add_block(block)

	def broadcast_block(self, transaction_pool, blockQueue):
		print("broadcasting block")
		for i in range(0, 1):
			blockQueue.put(self.chain.head)   
		self.print_chain()  
			
		self.remove_transaction(transaction_pool, self.current_transaction)
			
	# Select an unverified transaction at random from pool
	def select_transaction(self, transaction_pool):
		if len(transaction_pool) > 0:
			with lock:
				random_index = secrets.randbelow(len(transaction_pool))
				self.current_transaction = transaction_pool[random_index]
				return True
		else:
			return False

	# Check that a transaction is valid
	def validate_transaction(self):
		input_blocks = []
		# Signature must be valid, inputs must not have been used before, coins in must equal coins out
		if self.validate_signature() and self.validate_input() and self.validate_coin_amount():
			# Add the transaction's inputs to the used input list
			for input_block in self.current_transaction["INPUT"]:
				self.used_inputs.append(input_block)
				return True
		else:
			return False
		

	# Validate that a transaction's sigature is valid
	def validate_signature(self):
		transaction_content = self.current_transaction["TYPE"]

		for input_block in self.current_transaction["INPUT"]:
			transaction_content += input_block[0]
			transaction_content += str(input_block[1])

		for output_set in self.current_transaction["OUTPUT"]:
			transaction_content += output_set[0]
			transaction_content += str(output_set[1])

		for i in range(len(self.current_transaction["SIGNATURE"])):
			input_block = self.current_transaction["INPUT"][i]
			verifying_key = None
			current_block = self.chain.head
			while current_block is not None:
				if input_block[0] == current_block.transaction["NUMBER"]:
					verifying_key = VerifyingKey.from_string(bytes.fromhex(current_block.transaction["OUTPUT"][input_block[1]][0]))
				current_block = current_block.prev

			if verifying_key is not None:
				signature = self.current_transaction["SIGNATURE"][i]
				try:
					verifying_key.verify(bytes.fromhex(signature), transaction_content.encode("utf-8"))
					transaction_content += signature
				except BadSignatureError:
					print("Invalid signature")
					return False
			else:
				print("Input does not exist")
				return False
		return True

	# Validate that a transaction's inputs have not been previously used
	def validate_input(self):
		for input_block in self.current_transaction["INPUT"]:
			if input_block in self.used_inputs:
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
	# Returns True if it mined block, false otherwise
	def verify_transaction(self, blockQueue):

		# our hashed value neesd to be less than this   
		lessThan = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

		# set the digest as the highest possible value so the loop runs at least once
		digest = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

		# we keep track of the nonce
		nonce = 0

		# keep generating values while it's less than this value
		while(digest > lessThan):
			# if there's nothing in the block queue, then we keep looking 
			if blockQueue.empty():
				# generate the nonce
				nonce = random.getrandbits(32)
				unhashed = json.dumps(self.current_transaction) + str(nonce)
				sha256 = hashlib.new("sha256")
				sha256.update(unhashed.encode('utf-8'))

				# convert digest to int for comparison
				digest = int(sha256.hexdigest(), 16)
			else:
				return False

		print("block found on a thread")
		self.create_block(nonce, digest)

		return True

	# Create a new block from a verified transaction
	def create_block(self, nonce, digest):
		new_block = Block(nonce, digest, self.current_transaction)
		self.chain.add_block(new_block)

	# Remove a transaction from the network
	def remove_transaction(self, transaction_pool, transaction):
		with lock:
			if transaction in transaction_pool:
				transaction_pool.remove(transaction)
		
	def print_chain(self):
		blocks = []
		current_block = self.chain.head
		while current_block is not None:
			data = {}
			data["NONCE"] = current_block.nonce
			data["POW"] = current_block.proof_of_work
			data["TRANSACTION"] = current_block.transaction
			blocks.append(data)
			current_block = current_block.prev
		with open("node_"+str(self.id)+"_results.json", "w") as file:
			file.write(json.dumps(blocks))