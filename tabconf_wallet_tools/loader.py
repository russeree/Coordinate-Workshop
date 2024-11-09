import requests
from requests.auth import HTTPBasicAuth
import json

# Bitcoin Core RPC connection details
rpc_user = "tabconf"
rpc_password = "bitcoin"
rpc_url = "http://tabconf.testnet4.io:38332"

def load_wallet(wallet_name):
    """Load an existing wallet"""
    try:
        payload = {
            "method": "loadwallet",
            "params": [wallet_name],
            "jsonrpc": "2.0",
            "id": 1
        }
        response = requests.post(
            rpc_url,
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        return response.json().get('result')
    except requests.exceptions.RequestException as e:
        print(f"Error loading wallet {wallet_name}: {e}")
        return None

def list_available_wallets():
    """Get list of available wallets"""
    try:
        payload = {
            "method": "listwalletdir",
            "params": [],
            "jsonrpc": "2.0",
            "id": 1
        }
        response = requests.post(
            rpc_url,
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        wallets = response.json().get('result', {}).get('wallets', [])
        return [wallet['name'] for wallet in wallets]
    except requests.exceptions.RequestException as e:
        print(f"Error listing wallets: {e}")
        return []

# Get list of available wallets and load them
available_wallets = list_available_wallets()
print(f"Found {len(available_wallets)} wallets")

for wallet_name in available_wallets:
    try:
        result = load_wallet(wallet_name)
        if result:
            print(f"Successfully loaded wallet: {wallet_name}")
        else:
            print(f"Failed to load wallet: {wallet_name}")
    except Exception as e:
        print(f"Error while loading wallet {wallet_name}: {e}")

print("Finished loading wallets")