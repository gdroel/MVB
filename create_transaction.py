import json
import hashlib

# Create a new transaction
def create_transaction(input_set, output_set, type, signature_set):
    test_transaction = {}

    number_plaintext = ""
    test_transaction["TYPE"] = type
    test_transaction["INPUT"] = []
    test_transaction["OUTPUT"] = []
    test_transaction["SIGNATURE"] = []

    for input_number, input_output in input_set.items():
        test_transaction["INPUT"].append({input_number: input_output})
        number_plaintext += input_number
        number_plaintext += input_output
    
    for output_value, output_key in output_set.items():
        test_transaction["OUTPUT"].append({output_value: output_key})
        number_plaintext += output_value
        number_plaintext += output_key

    for sig_id, sig in signature_set.items():
        test_transaction["SIGNATURE"].append({sig_id: sig})
        number_plaintext += sig_id
        number_plaintext += sig

    sha3 = hashlib.new("sha256")
    sha3.update(number_plaintext.encode('utf-8'))

    test_transaction["NUMBER"] = sha3.hexdigest()

    test_transaction = json.dumps(test_transaction)

    transaction_file = open("example_transaction.json", "w")
    transaction_file.write(test_transaction)


def main():
    create_transaction({"block1": "output1"}, {"100": "publickey1"}, "TRANS", {"type": "sig1", "input": "sig2", "output": "sig3"})

if __name__ == "__main__":
    main()