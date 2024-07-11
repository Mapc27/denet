import os

from web3 import Web3
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

web3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com/'))
erc20_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

token_contract_address = os.getenv('TOKEN_CONTRACT_ADDRESS')
api_key = os.getenv('API_KEY')
polygonscan_api_url = os.getenv('API_URL')

token_address = Web3.to_checksum_address(token_contract_address)
token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)


app = Flask(__name__)


def fetch_token_holders(api_key, contract_address):
    url = f"{polygonscan_api_url}?module=account&action=tokenholderlist&contractaddress={contract_address}" \
          f"&apikey={api_key}"
    holders = []

    page = 1
    while True:
        response = requests.get(f"{url}&page={page}&offset=1000")
        data = response.json()
        if data['status'] == '1' and data['result']:
            holders.extend(data['result'])
            page += 1
        else:
            break
    return holders


def get_last_transaction(api_key, address):
    url = f"{polygonscan_api_url}?module=account&action=txlist&address={address}&sort=desc&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1' and data['result']:
        return data['result'][0]['timeStamp']  # Assuming the first transaction is the most recent
    return "No transactions found"


@app.route('/get_balance', methods=['GET'])
def get_balance():
    address = request.args.get('address')
    address = Web3.to_checksum_address(address)
    balance = token_contract.functions.balanceOf(address).call()
    return jsonify({'balance': balance})


@app.route('/get_balance_batch', methods=['POST'])
def get_balance_batch():
    addresses = request.json.get('addresses', [])
    balances = []
    for address in addresses:
        checksum_address = Web3.to_checksum_address(address)
        balance = token_contract.functions.balanceOf(checksum_address).call()
        balances.append(balance)
    balances = []
    return jsonify({'balances': balances})


@app.route('/get_top', methods=['GET'])
def get_top():
    n = request.json.get('n', 10)
    holders = fetch_token_holders(api_key, token_contract_address)
    sorted_holders = sorted(holders, key=lambda x: int(x['balance']), reverse=True)
    return jsonify(sorted_holders[:n])


@app.route('/get_top_with_transactions', methods=['GET'])
def get_top_with_transactions():
    n = request.json.get('n', 10)
    holders = fetch_token_holders(api_key, token_contract_address)
    sorted_holders = sorted(holders, key=lambda x: int(x['balance']), reverse=True)
    for holder in sorted_holders[:n]:
        last_transaction = get_last_transaction(api_key, holder['account'])
        holder['last_transaction'] = last_transaction
    return jsonify(sorted_holders[:n])


@app.route('/get_token_info', methods=['GET'])
def get_token_info():
    url = f"{polygonscan_api_url}?module=token&action=tokeninfo&contractaddress={token_contract_address}" \
          f"&apikey={api_key}"
    response = requests.get(url)
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
