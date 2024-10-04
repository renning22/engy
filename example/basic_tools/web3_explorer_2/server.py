
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from web3 import Web3
import logging

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Web3
INFURA_URL = os.getenv('INFURA_URL', 'https://mainnet.infura.io/v3/0826cbe5c945461a8cde38f960d2f735')
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Mock data for demonstration
MOCK_ACCOUNT = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
MOCK_BALANCE = 1.5

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/connect', methods=['POST'])
def connect():
    try:
        # In a real scenario, you would interact with MetaMask here
        # For this mock, we'll just return the mock account
        logger.info(f"Connection attempt from {request.remote_addr}")
        return jsonify({"address": MOCK_ACCOUNT}), 200
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return jsonify({"error": "Failed to connect to MetaMask"}), 400

@app.route('/balance', methods=['GET'])
def balance():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address parameter is required"}), 400

    try:
        # In a real scenario, you would fetch the actual balance
        # For this mock, we'll just return the mock balance
        logger.info(f"Balance query for address: {address}")
        balance = get_eth_balance(address)
        return jsonify({"balance": balance}), 200
    except Exception as e:
        logger.error(f"Balance fetch error: {str(e)}")
        return jsonify({"error": "Failed to fetch balance"}), 400

def connect_metamask():
    # This function would typically handle MetaMask connection
    # For this mock, we'll just return True
    return True

def get_eth_balance(address):
    # In a real scenario, you would use web3.py to fetch the actual balance
    # For this mock, we'll just return the mock balance
    return MOCK_BALANCE

if __name__ == '__main__':
    app.run(host='localhost', port=5011, debug=True)
