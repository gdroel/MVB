# Minimum Viable Blockchain
A simulation of a minimum viable blockhain, written in Python. 

The most disruptive new currency.

# Transactions
ID: Hash of entire transaction

Input: List of other transaction IDs used in the transaction

Output: Hash of public key of recipient and how much is being sent

Signature: Function of private key, "I am the one who owns the coins I am trying to spend"

Previous: Hash of the most recent transaction in the blockchain

Nonce: Number that can only be used once

Proof of work: Hash representing that the claimed work has actually been done.

# Questions
How are public keys published? 
How do the nodes obtain the public keys used to verify a transaction's signature?