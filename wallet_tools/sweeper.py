import requests
import json
from requests.auth import HTTPBasicAuth
from decimal import Decimal, ROUND_UP

# Bitcoin node RPC configuration
rpc_user = "tabconf"
rpc_password = "bitcoin"
rpc_url = "http://tabconf.testnet4.io:38332"

# Global variables
WALLET_LIST = []

def get_available_wallets():
    '''Get list of available wallets'''
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
    """Get all unspent outputs from a wallet"""
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
        
        return response.json().get('result', [])
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting unspent outputs: {e}")
        return None

def get_wallet_balance(wallet_name):
    """Get the balance of a specific wallet"""
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

def create_sweep_transaction(wallet_name, utxos, destination_address):
    """Create a raw transaction that sweeps all funds to a destination address"""
    
    # Calculate total amount from UTXOs
    total_amount = sum(float(utxo['amount']) for utxo in utxos)
    fee = 0.00001  # Fixed fee - adjust as needed
    final_amount = Decimal(str(total_amount - fee)).quantize(Decimal('0.00000001'), rounding=ROUND_UP)

    if final_amount <= 0:
        raise Exception(f"Insufficient funds after fee deduction. Total: {total_amount}, Fee: {fee}")

    # Prepare inputs
    inputs = [{
        "txid": utxo['txid'],
        "vout": utxo['vout']
    } for utxo in utxos]

    # Prepare outputs
    outputs = {
        destination_address: float(final_amount)
    }

    payload = {
        "method": "createrawtransaction",
        "params": [inputs, outputs],
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
        print(f"Error creating transaction: {e}")
        return None

def sign_and_send_transaction(wallet_name, raw_tx):
    """Sign and broadcast the transaction"""
    try:
        # Sign transaction
        sign_payload = {
            "method": "signrawtransactionwithwallet",
            "params": [raw_tx],
            "jsonrpc": "1.0",
            "id": 1
        }
        
        response = requests.post(
            f"{rpc_url}/wallet/{wallet_name}",
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=sign_payload
        )
        
        signed_tx = response.json().get('result', {}).get('hex')
        if not signed_tx:
            return None

        # Broadcast transaction
        send_payload = {
            "method": "sendrawtransaction",
            "params": [signed_tx],
            "jsonrpc": "1.0",
            "id": 1
        }
        
        response = requests.post(
            rpc_url,
            auth=HTTPBasicAuth(rpc_user, rpc_password),
            json=send_payload
        )
        
        return response.json().get('result')
    except requests.exceptions.RequestException as e:
        print(f"Error in sign_and_send_transaction: {e}")
        return None

def main():
    print("\nGetting available wallets...")
    if not get_available_wallets():
        print("Failed to retrieve wallet list. Exiting.")
        return

    # Display available wallets and their balances
    print("\nAvailable wallets:")
    for i, wallet_name in enumerate(WALLET_LIST, 1):
        balance = get_wallet_balance(wallet_name)
        print(f"{i}. {wallet_name} (Balance: {balance} BTC)")

    # Let user select a wallet
    while True:
        try:
            wallet_choice = input("\nEnter the number of the wallet you want to sweep: ")
            wallet_index = int(wallet_choice) - 1
            if 0 <= wallet_index < len(WALLET_LIST):
                selected_wallet = WALLET_LIST[wallet_index]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nSelected wallet: {selected_wallet}")
    
    # Get destination address
    destination_address = input("\nEnter the Coordinate address to sweep funds to: ").strip()
    
    # Get unspent outputs
    utxos = get_unspent_from_wallet(selected_wallet)
    if not utxos:
        print(f"No unspent outputs found in wallet {selected_wallet}, exiting...")
        return

    # Create the sweep transaction
    print("\nCreating sweep transaction...")
    unsigned_hex = create_sweep_transaction(selected_wallet, utxos, destination_address)
    
    if unsigned_hex:
        print("\nTransaction created successfully!")
        choice = input("\nPress 1 to sign and broadcast transaction, anything else to cancel: ")
        
        if choice == "1":
            txid = sign_and_send_transaction(selected_wallet, unsigned_hex)
            if txid:
                print(f"\nTransaction broadcast successfully!")
                print(f"Transaction ID: {txid}")
            else:
                print("\nFailed to broadcast transaction")
        else:
            print("\nTransaction cancelled")
    else:
        print(f"Failed to create transaction for wallet {selected_wallet}")

if __name__ == "__main__":
    main()