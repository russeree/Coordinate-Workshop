import requests
from requests.auth import HTTPBasicAuth
import json

# Bitcoin Core RPC connection details
rpc_user = "tabconf"
rpc_password = "bitcoin"
rpc_url = "http://tabconf.testnet4.io:38332"

# List of wallet names
wallet_names = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
    "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
    "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol"
]

def wallet_rpc_call(wallet_name, method, params=[]):
    """Make RPC call directly to a specific wallet"""
    try:
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1
        }
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        return response.json().get('result')
    except requests.exceptions.RequestException as e:
        print(f"Error in RPC call to wallet {wallet_name}: {e}")
        return None

def create_wallet(wallet_name):
    """Create a new wallet"""
    try:
        payload = {
            "method": "createwallet",
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
        print(f"Error creating wallet: {e}")
        return None

# File to log wallet names and addresses
log_file = 'wallet_addresses.txt'

with open(log_file, 'w') as f:
    for name in wallet_names:
        try:
            # Try to create wallet
            create_wallet(name)
            print(f"Created wallet: {name}")
        except:
            print(f"Wallet {name} already exists")
        
        # Generate new address directly from the wallet
        address = wallet_rpc_call(name, 'getnewaddress')
        
        if address:
            # Log wallet name and address
            f.write(f"{name}: {address}\n")
            print(f"Generated address for {name}: {address}")
        else:
            print(f"Failed to generate address for {name}")

print(f"Wallet names and addresses have been logged to {log_file}")