from flask import Flask, render_template, jsonify, request
import requests
from uuid import uuid4
from Blockchain import Blockchain, GanacheHandler, ContractHandler
import random
import asyncio

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/layout')
def layout():
    return render_template('layout.html')


@app.route('/create_contract')  # flask function
def create_contract():
    response = dict()
    ganache = GanacheHandler()

    senders = [ganache.account[0], ganache.account[1]]
    distributor = [ganache.account[2], ganache.account[3]]
    receiver = ganache.account[4], 'e7a328e9fa5d14b7e8574a70b947865b0a08f28c7410372462a2b365ad0886de'
    response['sender'] = random.choice(senders)
    response['distributor'] = random.choice(distributor)
    response['receiver'] = receiver[0]
    response['price_delivery'] = random.choice([2, 3, 5])
    response['price_goods'] = random.choice([5, 6, 8])
    response['weight'] = random.choice([12, 45, 56])
    response['volume'] = random.choice([23, 34, 11])
    response['final_date'] = random.choice(['12.12.2019', '23.01.2020'])

    contract = ContractHandler()
    if contract.get_contract(ganache=ganache, response=response, receiver=receiver):
        return render_template('create_contract.html', response=response)
    else:
        return render_template('no_money.html')


@app.route('/aboutus')
def about():
    return render_template('about.html')


@app.route('/maps')
def maps():
    return render_template('maps.html')


@app.route('/')
@app.route('/mine', methods=['GET'])
def mine():
    try:
        last_block = blockchain.last_block
    except IndexError:
        return jsonify({'message': 'no transactions'}), 401

    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return render_template('mine.html', response=response)


@app.route('/chain', methods=['GET'])
def get_full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return render_template('all_chain.html', response=response, )


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New node have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflict()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 201


if __name__ == '__main__':
    app.run(debug=True)
