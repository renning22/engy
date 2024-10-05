
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Connect to Ethereum network (using Infura as an example)
INFURA_URL = os.getenv('INFURA_URL', 'https://mainnet.infura.io/v3/0826cbe5c945461a8cde38f960d2f735')
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def validate_address(address):
    return Web3.is_address(address)

@app.route('/api/balance/<address>')
def get_balance(address):
    if not validate_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
    
    try:
        balance = w3.eth.get_balance(address)
        return jsonify({"balance": w3.from_wei(balance, 'ether')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions/<address>')
def get_transactions(address):
    if not validate_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400
    
    try:
        # This is a simplified version. In a real-world scenario, you'd need to use an Ethereum explorer API
        # or index transactions yourself, as getting all transactions for an address is not trivial.
        latest_block = w3.eth.get_block('latest')
        transactions = []
        for i in range(10):  # Get last 10 blocks as an example
            block = w3.eth.get_block(latest_block.number - i, full_transactions=True)
            for tx in block.transactions:
                if tx['from'] == address or tx['to'] == address:
                    transactions.append({
                        "hash": tx['hash'].hex(),
                        "from": tx['from'],
                        "to": tx['to'],
                        "value": w3.from_wei(tx['value'], 'ether')
                    })
        return jsonify({"transactions": transactions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=7112, debug=True)
