from node import Node
import json

def main():
    with open("transaction_file.json") as transaction_file:
        data = json.load(transaction_file)
        with open("unverified_pool.json", "w") as unverified_pool:
            transactions = json.dumps(data[1:])
            unverified_pool.write(transactions)

    node = Node()
    while True:
        unverified_pool = open("unverified_pool.json", "r")
        transactions = json.load(unverified_pool)
        if len(transactions) == 0:
            break
        else:
            node.run()
    node.print_chain()

if __name__ == "__main__":
    main()