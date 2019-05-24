import json
import hashlib
from ecdsa import SigningKey

# Create a new transaction
def create_transaction(signing_keys, transactions, input_set, output_set, type):
    test_transaction = {}

    number_plaintext = ""
    number_plaintext += type
    test_transaction["TYPE"] = type
    test_transaction["INPUT"] = []
    test_transaction["OUTPUT"] = []
    test_transaction["SIGNATURE"] = []

    for input_pair in input_set:
        if input_pair is not None:
            test_transaction["INPUT"].append(input_pair)
            number_plaintext += input_pair[0]
            number_plaintext += str(input_pair[1])
        else:
            test_transaction["INPUT"].append(None)
    
    for output_pair in output_set:
        print(output_pair)
        test_transaction["OUTPUT"].append((output_pair))
        number_plaintext += output_pair[0]
        number_plaintext += str(output_pair[1])

    if signing_keys is not None:
        for key in signing_keys:
                signature = key.sign(number_plaintext.encode('utf-8')).hex()
                test_transaction["SIGNATURE"].append(signature)
                number_plaintext += str(signature)
    else:
        test_transaction["SIGNATURE"].append(None)

    sha3 = hashlib.new("sha256")
    sha3.update(number_plaintext.encode('utf-8'))
    
    test_transaction["NUMBER"] = sha3.hexdigest()
    transactions.append(test_transaction)

def main():
    signing_key_1 = SigningKey.generate()
    verifying_key_1 = signing_key_1.get_verifying_key().to_string().hex()

    signing_key_2 = SigningKey.generate()
    verifying_key_2 = signing_key_1.get_verifying_key().to_string().hex()


    transactions = []
    create_transaction(None, transactions, [None], [(verifying_key_1, 25)], "TRANS")
    prev_block = transactions[0]["NUMBER"]
    create_transaction([signing_key_1], transactions, [(prev_block, 25)], [(verifying_key_2, 25)], "TRANS")

    transactions = json.dumps(transactions)

    transaction_file = open("transaction_file.json", "w")
    transaction_file.write(transactions)


if __name__ == "__main__":
    main()