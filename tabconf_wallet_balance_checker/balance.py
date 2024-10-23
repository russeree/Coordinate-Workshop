import requests
import json

# Bitcoin Core RPC connection details
rpc_user = 'tabconf'
rpc_password = 'bitcoin'
rpc_base_url = 'http://testnet4.io:38332'  # Default testnet RPC port

def rpc_call(method, params=[], wallet_name=None):
    headers = {'content-type': 'application/json'}
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "tabconf",
        "method": method,
        "params": params
    })
    
    # Construct URL with wallet name if provided
    url = f"{rpc_base_url}/wallet/{wallet_name}" if wallet_name else rpc_base_url
    
    response = requests.post(url, headers=headers, data=payload, auth=(rpc_user, rpc_password))
    return response.json()['result']

def check_wallet(wallet_name):
    try:
        # Get wallet balance
        balance = rpc_call('getbalance', [], wallet_name)
        print(f"Wallet balance: {balance} BTC")

        # Generate new receive address
        address = rpc_call('getnewaddress', [], wallet_name)
        print(f"New receive address: {address}")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure the wallet name exists and Bitcoin Core is running")

def main():
    while True:
        print("\nEnter wallet name (or 'quit' to exit):")
        wallet_name = input().strip()
        
        if wallet_name.lower() == 'quit':
            break
            
        check_wallet(wallet_name)

if __name__ == "__main__":
    main()
