import requests
import json
from requests.auth import HTTPBasicAuth
import base64
from pathlib import Path
import hashlib
from decimal import Decimal, ROUND_UP

# Bitcoin node RPC configuration
rpc_user = "username"
rpc_password = "password"
rpc_url = "http://tabconf.testnet4.io:38332"

# Global variables
WALLET_LIST = []
ASSET_CONTROLLER_ADDRESS = "tc1qkrtry6vzjt9kmjtj6rsfng0vcmxze453yes5lf"
IMAGE_DATA_URL = None
IMAGE_SHA256 = None

def get_available_wallets():
    global WALLET_LIST
    payload = {
        "method": "listwalletdir",
        "params": [],
        "jsonrpc": "2.0",
        "id": 1
    }
    
    try:
        response = requests.post(
            rpc_url,
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        
        wallet_dirs = response.json().get('result', {}).get('wallets', [])
        WALLET_LIST = [wallet['name'] for wallet in wallet_dirs]
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Bitcoin node: {e}")
        return False

def load_image_and_hash():
    global IMAGE_DATA_URL, IMAGE_SHA256
    try:
        with open("asset.png", "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            IMAGE_DATA_URL = f"data:image/png;base64,{image_base64}"
            IMAGE_SHA256 = hashlib.sha256(IMAGE_DATA_URL.encode('utf-8')).hexdigest()
            return True
    except Exception as e:
        print(f"Error loading image: {e}")
        return False

def get_unspent_from_wallet(wallet_name):
    try:
        load_payload = {
            "method": "loadwallet",
            "params": [wallet_name],
            "jsonrpc": "2.0",
            "id": 1
        }
        
        try:
            requests.post(
                rpc_url,
                auth=HTTPBasicAuth(rpc_user, rpc_password),
                json=load_payload
            )
        except:
            pass

        listunspent_payload = {
            "method": "listunspent",
            "params": [],
            "jsonrpc": "2.0",
            "id": 1
        }
        
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=listunspent_payload
        )
        
        unspent = response.json().get('result', [])
        if unspent:
            return unspent[0]
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting unspent outputs for wallet {wallet_name}: {e}")
        return None

def get_change_address(wallet_name):
    try:
        payload = {
            "method": "getrawchangeaddress",
            "params": [],
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
        print(f"Error getting change address: {e}")
        return None

def create_asset_transaction(wallet_name, utxo, asset_receive_address):
    if not IMAGE_DATA_URL or not IMAGE_SHA256:
        raise Exception("Image data not available")

    change_address = get_change_address(wallet_name)
    if not change_address:
        raise Exception("Failed to get change address")

    utxo_amount = float(utxo['amount'])
    fee = 0.01
    
    change_amount = Decimal(str(utxo_amount - fee)).quantize(Decimal('0.00001'), rounding=ROUND_UP)

    if change_amount < 0:
        raise Exception(f"Insufficient funds in UTXO. Required: {fee}, Available: {utxo_amount}")
    else:
        print(f"Using a change output value of {change_amount}")

    payload_data = json.dumps([{
        "image_data": IMAGE_DATA_URL,
        "mime": "png"
    }])
    
    payload_data_hex = payload_data.encode('utf-8').hex()
    payload_hash = ''.join(reversed([hashlib.sha256(bytes.fromhex(payload_data_hex)).hexdigest().lower()[i:i+2] 
                                   for i in range(0, len(hashlib.sha256(bytes.fromhex(payload_data_hex)).hexdigest().lower()), 2)]))

    print(f"Payload Hash: {payload_hash}")

    inputs = [{
        "txid": utxo['txid'],
        "vout": utxo['vout']
    }]

    outputs = {
        ASSET_CONTROLLER_ADDRESS: 1,
        asset_receive_address: .00000001,
        change_address: str(change_amount)
    }

    asset_details = {
        "assettype": 2,
        "ticker": "TABConf",
        "headline": "Testnet Giveaway Event",
        "precision": 0,
        "payload": payload_hash,
        "payloaddata": payload_data
    }

    payload = {
        "method": "createrawtransaction",
        "params": [inputs, outputs, None, None, asset_details],
        "jsonrpc": "1.0",
        "id": 1
    }

    try:
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        return response.json().get('result')
    except requests.exceptions.RequestException as e:
        print(f"Error creating asset transaction: {e}")
        return None

def sign_raw_transaction(wallet_name, tx_hex):
    try:
        payload = {
            "method": "signrawtransactionwithwallet",
            "params": [tx_hex],
            "jsonrpc": "1.0",
            "id": 1
        }
        
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        result = response.json().get('result', {})
        if result and result.get('complete'):
            return result.get('hex')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error signing transaction: {e}")
        return None

def get_wallet_balance(wallet_name):
    try:
        payload = {
            "method": "getbalance",
            "params": [],
            "jsonrpc": "2.0",
            "id": 1
        }
        
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=payload
        )
        return response.json().get('result', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error getting wallet balance: {e}")
        return None

def main():
    print("Loading image...")
    if not load_image_and_hash():
        print("Failed to load image. Exiting.")
        return
    
    print(f"Image Data/URI SHA256: {IMAGE_SHA256}")

    print("\nGetting available wallets...")
    if not get_available_wallets():
        print("Failed to retrieve wallet list. Exiting.")
        return

    # Display available wallets and their balances
    print("\nAvailable wallets:")
    for i, wallet_name in enumerate(WALLET_LIST, 1):
        balance = get_wallet_balance(wallet_name)
        print(f"{i}. {wallet_name} (Balance: {balance} BTC)")

    # Get single destination address for all transactions
    asset_receive_address = input("\nEnter the address you would like to send all assets to: ").strip()

    # Process each wallet
    for wallet_name in WALLET_LIST:
        balance = get_wallet_balance(wallet_name)
        if balance < .1:  
            print(f"\nSkipping wallet {wallet_name} - insufficient balance ({balance} BTC)")
            continue

        print(f"\nProcessing wallet: {wallet_name}")
        
        utxo = get_unspent_from_wallet(wallet_name)
        if not utxo:
            print(f"No unspent outputs found in wallet {wallet_name}, skipping...")
            continue

        print(f"Creating asset transaction for wallet {wallet_name}...")
        try:
            unsigned_hex = create_asset_transaction(wallet_name, utxo, asset_receive_address)
            
            if unsigned_hex:
                print(f"Transaction created successfully for wallet {wallet_name}")
                print("Signing transaction...")
                
                signed_hex = sign_raw_transaction(wallet_name, unsigned_hex)
                if signed_hex:
                    try:
                        payload = {
                            "method": "sendrawtransaction",
                            "params": [signed_hex],
                            "jsonrpc": "1.0",
                            "id": 1
                        }
                        response = requests.post(
                            rpc_url,
                            auth=HTTPBasicAuth(rpc_user, rpc_password),
                            json=payload
                        )
                        result = response.json()
                        if 'result' in result:
                            print(f"Transaction broadcast successfully for wallet {wallet_name}!")
                            print(f"Transaction ID: {result['result']}")
                        else:
                            print(f"Failed to broadcast transaction for wallet {wallet_name}: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        print(f"Error broadcasting transaction for wallet {wallet_name}: {e}")
                else:
                    print(f"Failed to sign transaction for wallet {wallet_name}")
            else:
                print(f"Failed to create transaction for wallet {wallet_name}")
        except Exception as e:
            print(f"Error processing wallet {wallet_name}: {e}")
            continue

    print("\nFinished processing all wallets.")

if __name__ == "__main__":
    main()
