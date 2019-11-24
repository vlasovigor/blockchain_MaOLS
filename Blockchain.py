from time import time
import json
import hashlib
from urllib.parse import urlparse
import requests
from web3 import Web3


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': self.last_block['index'] + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        try:
            return self.last_block['index'] + 1
        except TypeError:
            return 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n------------------\n')

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflict(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if requests.status_codes == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


class GanacheHandler(object):
    url = "http://127.0.0.1:7545"

    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(self.url))
        self.account = self.web3.eth.accounts

    def init_contract(self):
        pass

    def simple_transaction(self, account_1, account_2, pk):
        nonce = self.web3.eth.getTransactionCount(account_1)

        tx = {
            'nonce': nonce,
            'to': account_2,
            'value': self.web3.toWei(4, 'ether'),
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
        }

        signed_tx = self.web3.eth.account.signTransaction(tx, pk)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return self.web3.toHex(tx_hash)


class ContractHandler(object):
    def __init__(self, ganache, abi, bytecode):
        self.contract = ganache.web3.eth.contract(abi=abi, bytecode=bytecode)
        self.tx_hash = self.contract.constructor().transact()
        self.tx_receipt = ganache.web3.eth.waitForTransactionReceipt(self.tx_hash)


if __name__ == '__main__':
    ganache = GanacheHandler()
    print(ganache.account.)
