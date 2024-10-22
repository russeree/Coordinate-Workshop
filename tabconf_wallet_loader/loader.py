import requests
import json

# Bitcoin Core RPC connection details
rpc_user = 'tabconf'
rpc_password = 'bitcoin'
rpc_url = 'http://localhost:18332'  # Default testnet RPC port

# List of wallet names
wallet_names = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
    "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
    "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol"
]

def rpc_call(method, params=[]):
    headers = {'content-type': 'application/json'}
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": "minebet",
        "method": method,
        "params": params
    })
    response = requests.post(rpc_url, headers=headers, data=payload, auth=(rpc_user, rpc_password))
    return response.json()['result']

# File to log wallet names and addresses
log_file = 'wallet_addresses.txt'

with open(log_file, 'w') as f:
    for name in wallet_names:
        # Create wallet
        try:
            rpc_call('createwallet', [name])
            print(f"Created wallet: {name}")
        except:
            print(f"Wallet {name} might already exist, continuing...")

        # Load wallet
        rpc_call('loadwallet', [name])
        print(f"Loaded wallet: {name}")

        # Generate new address
        address = rpc_call('getnewaddress', [])

        # Log wallet name and address
        f.write(f"{name}: {address}\n")
        print(f"Generated address for {name}: {address}")

        # Unload wallet - DEPRECATED
        # rpc_call('unloadwallet', [name])
        # print(f"Unloaded wallet: {name}")
        print("---")

print(f"Wallet names and addresses have been logged to {log_file}")
