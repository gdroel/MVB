import json
import hashlib
import secrets
import random
import time
from ecdsa import VerifyingKey, BadSignatureError
from block import Block
import threading
import queue
from ecdsa import SigningKey

lock = threading.Lock()

class Node:
	def __init__(self, id, is_done):

		self.mining_reward = 25
		self.chain = []
		self.fork_chain = []
		self.current_transaction = None
		self.used_inputs = []
		self.fork_used_inputs = []
		self.last_common_block = None
		self.id = id
		self.is_done = is_done
		self.blockQueue = queue.Queue()
		signing_key = SigningKey.generate()
		self.verifying_key = signing_key.get_verifying_key().to_string().hex()
		self.initalize_chain()

	# Adds the Genesis Block as the first block in the chain
	def initalize_chain(self):
		with open("transaction_file.json") as file:
			data = json.load(file)
			self.current_transaction = data[0]
		self.create_block(0, 0)

	def run(self, transaction_pool, main_queue):
		while(not self.is_done):
			if len(transaction_pool) == 0:
				print("node ", self.id, " is sleeping")
				time.sleep(5)

			if not self.blockQueue.empty():
				print("node ", self.id, " is handling a block")
				self.handle_received_block(transaction_pool)
		
			elif len(transaction_pool) != 0 and self.select_transaction(transaction_pool):
				# Validate the transaction
				if self.validate_transaction(transaction_pool, self.current_transaction, self.chain, self.used_inputs):
					print("node ", self.id, " found a block")
					# Verify Transaction via POW
					verify_result = self.verify_transaction()

					if verify_result == False:
						print("node ", self.id, " interrupted mining")
						# A block was received
						self.handle_received_block(transaction_pool)
					else:
						# Broadcast the mined block
						self.broadcast_block(transaction_pool, main_queue)
		self.print_chain()

	def handle_received_block(self, transaction_pool):
		while not self.blockQueue.empty():
			block = self.blockQueue.get()
			if block.proof_of_work != self.chain[-1].proof_of_work:
				if len(self.fork_chain) != 0:
					print("FORK EXISTS ", self.id)
					print("Chain for ", self.id, " is ", self.chain[-1].proof_of_work, " fork is ", self.fork_chain[-1].proof_of_work, " block is ", block.prev)
					if block.prev == self.fork_chain[-1].proof_of_work and self.validate_block(block, transaction_pool, self.fork_chain, self.fork_used_inputs):
						print("CHOOSE FORK ", self.id)
						self.fork_chain.append(block)
						for input_block in block.transactions[1]["INPUT"]:
							self.fork_used_inputs.append(input_block)
						if len(self.fork_chain) > len(self.chain):
							for i in range(len(self.chain) - 1, 0, -1):
								if self.chain[i].proof_of_work == self.last_common_block:
									break
								else:
									self.add_transaction_to_pool(transaction_pool, self.chain[i].transactions[1])
							self.chain = self.fork_chain[:]
							self.used_inputs = self.fork_used_inputs[:]
							self.fork_chain = []
							self.fork_used_inputs = []
							
					elif block.prev == self.chain[-1].proof_of_work and self.validate_block(block, transaction_pool, self.chain, self.used_inputs):
						print("DON'T CHOOSE FORK ", self.id)
						self.chain.append(block)
						for input_block in block.transactions[1]["INPUT"]:
							self.used_inputs.append(input_block)
						if len(self.chain) > len(self.fork_chain):
							for i in range(len(self.fork_chain) - 1, -1, -1):
								if self.fork_chain[i].proof_of_work == self.last_common_block:
									break
								else:
									self.add_transaction_to_pool(transaction_pool, self.fork_chain[i].transactions[1])
							self.fork_chain = []
							self.fork_used_inputs = []

					else:
						print("NEW FORK for node ", self.id, block.transactions[1])
						for i in range(len(self.fork_chain) - 1, -1, -1):
							if self.fork_chain[i].proof_of_work == self.last_common_block:
								break
							else:
								self.add_transaction_to_pool(transaction_pool, self.fork_chain[i].transactions[1])

						for i in range(len(self.chain) - 1, -1, -1):
							if self.chain[i].proof_of_work == block.prev:
								print("FORK node ", self.id, " has prev ", self.chain[i].proof_of_work)
								self.last_common_block = self.chain[i].proof_of_work
								self.fork_chain = self.chain[:i + 1]
								self.fork_used_inputs = self.used_inputs[:i + 1]
								break
						self.fork_chain.append(block)
						for input_block in block.transactions[1]["INPUT"]:
							self.fork_used_inputs.append(input_block)

				# Check for a new fork
				elif len(self.fork_chain) == 0 and block.prev != self.chain[-1].proof_of_work:
					print("THERE IS A FORK for node ", self.id, block.transactions[1])
					for i in range(len(self.chain) - 1, -1, -1):
						if self.chain[i].proof_of_work == block.prev:
							print("FORK node ", self.id, " has prev ", self.chain[i].proof_of_work)
							self.last_common_block = self.chain[i].proof_of_work
							self.fork_chain = self.chain[:i + 1]
							self.fork_used_inputs = self.used_inputs[:i + 1]
							break
					self.fork_chain.append(block)
					for input_block in block.transactions[1]["INPUT"]:
						self.fork_used_inputs.append(input_block)

				# Check for a valid non-fork block
				elif self.validate_block(block, transaction_pool, self.chain, self.used_inputs):
					print("NO FORK ", self.id)
					self.chain.append(block)
					for input_block in block.transactions[1]["INPUT"]:
						self.used_inputs.append(input_block)
				else:
					print("block invalid")
		self.print_chain()

	def broadcast_block(self, transaction_pool, main_queue):
		print("broadcasting block from ", self.id)

		# artifically add latency
		time.sleep(5)
		main_queue.put((self.id, self.chain[-1])) 
			
		self.remove_transaction(transaction_pool, self.current_transaction, "broadcasting")
			
	# Select an unverified transaction at random from pool
	def select_transaction(self, transaction_pool):
		if len(transaction_pool) > 0:
			with lock:
				random_index = secrets.randbelow(len(transaction_pool))
				self.current_transaction = transaction_pool[random_index]
				return True
		else:
			return False

	# validate the coinbase transaction
	def validate_coinbase_transaction(self, transaction):

		print("VALIDATE COINBASE TRANSACTION")
		print(transaction["OUTPUT"][0][1])
		if transaction["OUTPUT"][0][1] != self.mining_reward:
			return False
		return True

	# Check that a transaction is valid
	def validate_transaction(self, transaction_pool, transaction, chain, used_inputs):
		# Signature must be valid, inputs must not have been used before, coins in must equal coins out
		if self.validate_signature(transaction_pool, transaction, chain) and self.validate_input(transaction_pool, transaction, used_inputs) and self.validate_coin_amount(transaction_pool, transaction, chain):
			return True
		else:
			return False

	def validate_block(self, block, transaction_pool, chain, used_inputs):
		with lock:
			unhashed = json.dumps(block.transactions[1]) + str(block.nonce)
			sha256 = hashlib.new("sha256")
			sha256.update(unhashed.encode('utf-8'))
			# convert digest to int for comparison
			digest = int(sha256.hexdigest(), 16)
			if digest == block.proof_of_work and self.validate_transaction(transaction_pool, block.transactions[1], chain, used_inputs):
				return True
			else:
				print("Failed to validate block, digest ", digest, " pow ", block.proof_of_work)
				return False

	# Validate that a transaction's sigature is valid
	def validate_signature(self, transaction_pool, transaction, chain):
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

			for k in range(len(chain) - 1, -1, -1):
				if input_block[0] == chain[k].transactions[1]["NUMBER"]:
					verifying_key = VerifyingKey.from_string(bytes.fromhex(chain[k].transactions[1]["OUTPUT"][input_block[1]][0]))

			if verifying_key is not None:
				signature = transaction["SIGNATURE"][i]
				try:
					verifying_key.verify(bytes.fromhex(signature), transaction_content.encode("utf-8"))
					transaction_content += signature
				except BadSignatureError:
					print("Invalid signature")
					self.remove_transaction(transaction_pool, transaction, "Invalid signature")
					return False
			else:
				return False

		return True

	# Validate that a transaction's inputs have not been previously used
	def validate_input(self, transaction_pool, transaction, used_inputs):
		for input_block in transaction["INPUT"]:
			if input_block in used_inputs:
				print("Input used previously ", input_block)	
				self.remove_transaction(transaction_pool, transaction, "Input used previously")
				return False
		return True
	
	# Validate that the total amount of coins in a transaction's inputs equals the total amount of coins in its outputs
	def validate_coin_amount(self, transaction_pool, transaction, chain):
		input_sum = 0
		output_sum = 0
		for input_block in transaction["INPUT"]:
			for i in range(len(chain) - 1, -1, -1):
				if input_block[0] == chain[i].transactions[1]["NUMBER"]:
					input_sum += chain[i].transactions[1]["OUTPUT"][input_block[1]][1]

		for output_block in transaction["OUTPUT"]:
			output_sum += output_block[1]

		if input_sum == output_sum:
			return True
		else:
			print("Input does not equal output")
			self.remove_transaction(transaction_pool, transaction, "Input does not equal output")
			return False

	# Verify the transaction through proof-of-work
	# Returns True if it mined block, false otherwise
	def verify_transaction(self):
		print("node ", self.id, " is mining")
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

		self.create_block(nonce, digest)

		return True

	# Create a new block from a verified transaction
	def create_block(self, nonce, digest):
		new_block = Block(nonce, digest, self.verifying_key, self.current_transaction)
		
		# set the previous to the end of the current chain
		if len(self.chain) > 0:
			new_block.prev = self.chain[-1].proof_of_work

		self.chain.append(new_block)

	# Remove a transaction from the network
	def remove_transaction(self, transaction_pool, transaction, reason):
		with lock:
			if transaction in transaction_pool:
				print("node ", self.id, "is removing because ", reason, transaction)
				transaction_pool.remove(transaction)

	# Add a transaction back to the pool
	def add_transaction_to_pool(self, transaction_pool, transaction):
		with lock:
			if transaction not in transaction_pool:
				transaction_pool.append(transaction)
		
	# Write the complete chain to a file
	def print_chain(self):
		blocks = []

		for i in range(len(self.chain) - 1, -1, -1):
			current_block = self.chain[i]
			data = {}
			data["NONCE"] = current_block.nonce
			data["POW"] = current_block.proof_of_work
			data["REWARD"] = current_block.transactions[0]
			data["TRANSACTION"] = current_block.transactions[1]
			blocks.append(data)

		with open("node_"+str(self.id)+"_results.json", "w") as file:
			file.write(json.dumps(blocks))