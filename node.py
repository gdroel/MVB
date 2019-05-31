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
import queue

lock = threading.Lock()

class Node:
	def __init__(self, id, is_done):
		self.chain = Blockchain()
		self.current_transaction = None
		self.used_inputs = []
		self.id = id
		self.is_done = is_done
		self.blockQueue = queue.Queue()
		self.initalize_chain()

	# Adds the Genesis Block as the first block in the chain
	def initalize_chain(self):
		with open("transaction_file.json") as file:
			data = json.load(file)
			self.current_transaction = data[0]
		self.create_block(0, 0)

	def run(self, transaction_pool, mainQueue):
		while(not self.is_done):
			if len(transaction_pool) == 0:
				time.sleep(5)
			if self.select_transaction(transaction_pool):
				print(self.current_transaction)
				# Validate the transaction
				if self.validate_transaction(transaction_pool, self.current_transaction):
					# Verify Transaction via POW
					verify_result = self.verify_transaction()

					if verify_result == False:
						# A block was received
						self.handle_received_block()
					else:
						# Broadcast the mined block
						self.broadcast_block(transaction_pool, mainQueue)
		self.print_chain()

	def handle_received_block(self, transaction_pool):
		while not self.blockQueue.empty():
			print("block received")
			block = self.blockQueue.get()
			if self.validate_block(block, transaction_pool):
				print("block valid")
				self.chain.add_block(block)
			print("block invalid")

	def broadcast_block(self, transaction_pool, mainQueue):
		print("broadcasting block")
		for i in range(0, 1):
			mainQueue.put(self.chain.head)   
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
	def validate_transaction(self, transaction_pool, transaction):
		# Signature must be valid, inputs must not have been used before, coins in must equal coins out
		if self.validate_signature(transaction_pool, transaction) and self.validate_input(transaction_pool, transaction) and self.validate_coin_amount(transaction_pool, transaction):
			return True
		else:
			return False

	def validate_block(self, block, transaction_pool):
		unhashed = json.dumps(block.transaction) + str(block.nonce)
		sha256 = hashlib.new("sha256")
		sha256.update(unhashed.encode('utf-8'))
		# convert digest to int for comparison
		digest = int(sha256.hexdigest(), 16)
		if digest == block.digest and self.validate_transaction(transaction_pool, block.transaction):
			return True
		else:
			return False

	# Validate that a transaction's sigature is valid
	def validate_signature(self, transaction_pool, transaction):
		transaction_content = transaction["TYPE"]

		for input_block in transaction["INPUT"]:
			transaction_content += input_block[0]
			transaction_content += str(input_block[1])

		for output_set in transaction["OUTPUT"]:
			transaction_content += output_set[0]
			transaction_content += str(output_set[1])

		for i in range(len(transaction["SIGNATURE"])):
			input_block = transaction["INPUT"][i]
			verifying_key = None
			current_block = self.chain.head
			while current_block is not None:
				if input_block[0] == current_block.transaction["NUMBER"]:
					verifying_key = VerifyingKey.from_string(bytes.fromhex(current_block.transaction["OUTPUT"][input_block[1]][0]))
				current_block = current_block.prev

			if verifying_key is not None:
				signature = transaction["SIGNATURE"][i]
				try:
					verifying_key.verify(bytes.fromhex(signature), transaction_content.encode("utf-8"))
					transaction_content += signature
				except BadSignatureError:
					print("Invalid signature")
					self.remove_transaction(transaction_pool, transaction)
					return False
			else:
				print(input_block[0])
				print("Input does not exist")
				return False
		return True

	# Validate that a transaction's inputs have not been previously used
	def validate_input(self, transaction_pool, transaction):
		for input_block in transaction["INPUT"]:
			if input_block in self.used_inputs:
				print("Input used previously")
				self.remove_transaction(transaction_pool, self.current_transaction)
				return False
		return True
	
	# Validate that the total amount of coins in a transaction's inputs equals the total amount of coins in its outputs
	def validate_coin_amount(self, transaction_pool, transaction):
		input_sum = 0
		output_sum = 0
		for input_block in transaction["INPUT"]:
			current_block = self.chain.head
			while current_block is not None:
				if input_block[0] == current_block.transaction["NUMBER"]:
					input_sum += current_block.transaction["OUTPUT"][input_block[1]][1]
				current_block = current_block.prev

		for output_block in transaction["OUTPUT"]:
			output_sum += output_block[1]

		if input_sum == output_sum:
			return True
		else:
			print("Input does not equal output")
			self.remove_transaction(transaction_pool, self.current_transaction)
			return False

	# Verify the transaction through proof-of-work
	# Returns True if it mined block, false otherwise
	def verify_transaction(self):

		# our hashed value neesd to be less than this   
		lessThan = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

		# set the digest as the highest possible value so the loop runs at least once
		digest = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

		# we keep track of the nonce
		nonce = 0

		# keep generating values while it's less than this value
		while(digest > lessThan):
			# if there's nothing in our block queue, then we keep looking 
			if self.blockQueue.empty():
				# generate the nonce
				nonce = random.getrandbits(32)
				unhashed = json.dumps(self.current_transaction) + str(nonce)
				sha256 = hashlib.new("sha256")
				sha256.update(unhashed.encode('utf-8'))

				# convert digest to int for comparison
				digest = int(sha256.hexdigest(), 16)
			else:
				return False
		
		# Add the transaction's inputs to the used input list
		for input_block in self.current_transaction["INPUT"]:
			self.used_inputs.append(input_block)
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