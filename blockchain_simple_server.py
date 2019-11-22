from flask import Flask, render_template, jsonify, request
import requests
from uuid import uuid4
from Blockchain import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/layout')
def layout():
    return render_template("layout.html")


@app.route('/aboutus')
def about():
    return render_template("about.html")

@app.route('/upload')    # ('/') - WORK
def upload():
    return render_template("upload.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        return render_template("success.html", name=f.filename)


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


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    try:
        values = request.args
    except BaseException:
        return jsonify({'message': 'some shit happens'}), 401

    required = ['sender', 'recipient', 'amount']

    if not all(r in values.keys() for r in required):
        return 'Missing required argument', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def get_full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return render_template('all_chain.html', response=response)


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
    app.run(host='0.0.0.0', port=5000)
