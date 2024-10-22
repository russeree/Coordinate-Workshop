import requests
import json
from requests.auth import HTTPBasicAuth
import base64
from pathlib import Path
import hashlib


# Bitcoin node RPC configuration
rpc_user = "tabconf"
rpc_password = "bitcoin"
rpc_url = "http://localhost:18332"  # Default Bitcoin RPC port

# Global variable to store wallet names
# Global variables
WALLET_LIST = []
ASSET_CONTROLLER_ADDRESS =  "tc1qkrtry6vzjt9kmjtj6rsfng0vcmxze453yes5lf"
ASSET_RECEIVE_ADDRESS = "tc1q9p9lgxtg88krma7sdf278ya8nsjsnwejhyf7ca"
IMAGE_DATA_URL = None
IMAGE_SHA256 = None

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


def get_unspent_from_wallet(wallet_name):
    """Get the first unspent output from a wallet"""
    try:
        # Load the wallet first
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

        # Get unspent outputs
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
            return unspent[0]  # Return first unspent output
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting unspent outputs for wallet {wallet_name}: {e}")
        return None

def get_change_address(wallet_name):
    """Get a new change address from the wallet"""
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

def create_asset_transaction(wallet_name, utxo):
    """Create a raw transaction for asset creation"""
    if not IMAGE_DATA_URL or not IMAGE_SHA256:
        raise Exception("Image data not available")

    # Get change address
    change_address = get_change_address(wallet_name)
    if not change_address:
        raise Exception("Failed to get change address")

    # Get UTXO amount and calculate change
    utxo_amount = float(utxo['amount'])
    fee = 0.00001  # Transaction fee
    #change_amount = utxo_amount - asset_amount - fee

    #if change_amount < 0:
    #    raise Exception(f"Insufficient funds in UTXO. Required: {asset_amount + fee}, Available: {utxo_amount}")

    # Convert the IMAGE_DATA_URL directly to hex
    payload_data = json.dumps([{
        "image_data": IMAGE_DATA_URL,
        "mime": "png"
    }])
    
    payload_data_hex = payload_data.encode('utf-8').hex()
    
    # Convert hex to bytes and hash those bytes
    payload_hash = ''.join(reversed([hashlib.sha256(bytes.fromhex(payload_data_hex)).hexdigest().lower()[i:i+2] for i in range(0, len(hashlib.sha256(bytes.fromhex(payload_data_hex)).hexdigest().lower()), 2)]))

    print(f"PayloadData: {payload_data_hex}")
    print(f"Payload Hash: {payload_hash}")

    # Prepare the inputs
    inputs = [{
        "txid": utxo['txid'],
        "vout": utxo['vout']
    }]

    # Prepare the outputs with asset destination and change address
    outputs = {
        ASSET_CONTROLLER_ADDRESS: 1,
        ASSET_RECEIVE_ADDRESS: 1,
        change_address: .960,
    }

    asset_details = {
        "assettype": 2,
        "ticker": "TAB",
        "headline": "Conference PNG",
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
        return response.json().get('result')  # This will be the hex of the transaction
    except requests.exceptions.RequestException as e:
        print(f"Error creating asset transaction: {e}")
        return None
    
def sign_raw_transaction(wallet_name, tx_hex):
    """Sign the raw transaction"""
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

def main():
   print("Loading image...")
   if not load_image_and_hash():
       print("Failed to load image. Exiting.")
       return
   
   print(f"Image Data/URI SHA256: {IMAGE_SHA256}")

   input("Press Enter to continue to transaction creation...")

   print("Getting available wallets...")
   if not get_available_wallets():
       print("Failed to retrieve wallet list. Exiting.")
       return

   print(f"\nFound {len(WALLET_LIST)} wallets")
   
   for wallet_name in WALLET_LIST:
       print(f"\nProcessing wallet: {wallet_name}")
       
       # Get unspent output from wallet
       utxo = get_unspent_from_wallet(wallet_name)
       if not utxo:
           print(f"No unspent outputs found in wallet {wallet_name}, skipping...")
           continue

       # Create the asset transaction
       print("Creating asset transaction...")
       unsigned_hex = create_asset_transaction(wallet_name, utxo)
       
       if unsigned_hex:
           print("\nUnsigned transaction created successfully!")
           input("\nPress Enter to sign the transaction...")
           
           signed_hex = sign_raw_transaction(wallet_name, unsigned_hex)
           if signed_hex:
               print("\nTransaction signed successfully!")
               print("\n" + "="*50)
               print("Final Signed Transaction Hex:")
               print("="*50)
               print(signed_hex)
               print("="*50)
               print("\nCopy the hex above to use with sendrawtransaction")
               
               choice = input("\nPress 1 to broadcast transaction, anything else to skip: ")
               if choice == "1":
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
                           print(f"\nTransaction broadcast successfully!")
                           print(f"Transaction ID: {result['result']}")
                       else:
                           print(f"\nFailed to broadcast transaction: {result.get('error', 'Unknown error')}")
                   except Exception as e:
                       print(f"\nError broadcasting transaction: {e}")
               else:
                   print("\nSkipping transaction broadcast")
               
               input("\nPress Enter to continue with the next wallet...")
           else:
               print("Failed to sign transaction")
       else:
           print(f"Failed to create transaction for wallet {wallet_name}")

if __name__ == "__main__":
   main()
