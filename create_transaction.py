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
        test_transaction["OUTPUT"].append((output_pair))
        number_plaintext += output_pair[0]
        number_plaintext += str(output_pair[1])

    if signing_keys is not None:
        for i in range(len(input_set)):
            signature = signing_keys[i].sign(number_plaintext.encode('utf-8')).hex()
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
    verifying_key_2 = signing_key_2.get_verifying_key().to_string().hex()

    signing_key_3 = SigningKey.generate()
    verifying_key_3 = signing_key_3.get_verifying_key().to_string().hex()

    signing_key_4 = SigningKey.generate()
    verifying_key_4 = signing_key_4.get_verifying_key().to_string().hex()

    signing_key_5 = SigningKey.generate()
    verifying_key_5 = signing_key_5.get_verifying_key().to_string().hex()

    transactions = []

    # Genesis block transaction, 15 coins -> 1 and 10 coins -> 2
    create_transaction(None, transactions, [None], [(verifying_key_1, 15), (verifying_key_2, 10)], "TRANS")
    genesis_transaction = transactions[0]["NUMBER"]

    # Valid TRANS transaction, 10 coins from 1 -> 3 and 5 coins from 1 -> 1
    create_transaction([signing_key_1], transactions, [(genesis_transaction, 0)], [(verifying_key_3, 10), (verifying_key_1, 5)], "TRANS")
    first_transaction = transactions[1]["NUMBER"]

    # Malicious TRANS transaction, double spend, 10 coins from 1 -> 3 and 5 coins from 1 -> 1
    create_transaction([signing_key_1], transactions, [(genesis_transaction, 0)], [(verifying_key_2, 10), (verifying_key_1, 5)], "TRANS")
    second_transaction = transactions[2]["NUMBER"]

    # Valid TRANS transaction, 3 coins from 2 -> 4, 3 coins from 2 -> 5, 4 coins from 2 -> 2
    create_transaction([signing_key_2], transactions, [(genesis_transaction, 1)], [(verifying_key_4, 3), (verifying_key_5, 3), (verifying_key_2, 4)], "TRANS")
    third_transaction = transactions[3]["NUMBER"]

    # Invalid TRANS transaction, wrong signature, 3 coins from 5 -> 1
    create_transaction([signing_key_1], transactions, [(third_transaction, 1)], [(verifying_key_1, 3)], "TRANS")
    fourth_transaction = transactions[4]["NUMBER"]

    # Valid JOIN transaction, 5 coins from 1 + 4 coins from 2 -> 3
    create_transaction([signing_key_1, signing_key_2], transactions, [(first_transaction, 1), (third_transaction, 2)], [(verifying_key_3, 9)], "JOIN")
    fifth_transaction = transactions[5]["NUMBER"]

    # Valid MERGE transaction, 10 coins + 9 coins -> 3
    create_transaction([signing_key_3, signing_key_3], transactions, [(first_transaction, 0), (fifth_transaction, 0)], [(verifying_key_3, 19)], "MERGE")
    sixth_transaction = transactions[6]["NUMBER"]

    # Invalid MERGE transaction, does not own all coins, 3 coins + 3 coins -> 4
    create_transaction([signing_key_4, signing_key_4], transactions, [(third_transaction, 0), (third_transaction, 1)], [(verifying_key_4, 6)], "MERGE")
    seventh_transaction = transactions[7]["NUMBER"]

    # Valid TRANS transaction, 10 coins from 3 -> 4, 9 coins from 3 -> 5
    create_transaction([signing_key_3], transactions, [(sixth_transaction, 0)], [(verifying_key_4, 10), (verifying_key_5, 9)], "TRANS")
    eighth_transaction = transactions[8]["NUMBER"]

    # Valid TRANS transaction, 3 coins from 4 -> 1, 10 coins from 4 -> 4
    create_transaction([signing_key_4, signing_key_4], transactions, [(eighth_transaction, 0), (third_transaction, 0)], [(verifying_key_1, 3), (verifying_key_4, 10)], "TRANS")
    ninth_transaction = transactions[9]["NUMBER"]

    # Valid JOIN transaction, 1 coin from 1 -> 2, 3 coins from 4 -> 2
    create_transaction([signing_key_1, signing_key_4], transactions, [(ninth_transaction, 0), (ninth_transaction, 1)], [(verifying_key_2, 4), (verifying_key_1, 2), (verifying_key_4, 7)], "JOIN")
    tenth_transaction = transactions[10]["NUMBER"]

    transactions = json.dumps(transactions)

    transaction_file = open("transaction_file.json", "w")
    transaction_file.write(transactions)


if __name__ == "__main__":
    main()