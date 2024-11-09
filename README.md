# Coordinate Workshop
This workshop is to better explain and define the capabilities and tradeoffs of Coordinate; A Bitcoin L2 Sidechain. What this document doesn't cover is the security side of L2s on Bitcoin and the complete feature set of Coordinate. Instead focusing on the interactions that a user can have with a Coordinate node and existing infrastructure. 

## Hello World - Overview 🌎
 - Wallets and RPC - Using Python to Interact with a Node.
 - Asset Transfers - Browser Extension Wallet
 - Asset Creation [NFT]
 - Testnet 3/4 Giveaway

## Requirements ✅
 - Laptop
 - [Latest Version of Python](https://www.python.org/)
 - [Chrome / Chromium](https://www.google.com/chrome/) - _brave might work?_
 - [Coordinate Browser Extension Wallet](https://chromewebstore.google.com/detail/anduro/khebhoaoppjeidmdkpdglmlhghnooijn)

## Phase One - Get your Wallet ID (BIP39)
To get the soft introduction to Coordinate going and avoid any delays in transaction confirmation please download the [Chrome Browser Wallet](https://chromewebstore.google.com/detail/anduro/khebhoaoppjeidmdkpdglmlhghnooijn) and set it up with the defaults. For the sake of the demo and because we are dealing with Testnet Bitcoins only, security of a seed phase backup can be foregone and the wallet recreated later with a more secure seed phrase at a later time. 

After you have create your seed phrase, please fetch your Testnet(3/4) address from the browser wallet in the Bitcoin category. *NOTE* Your Testnet3/4 address will be the same on both networks but carry a different balance depending on which network you have selected. Please also Fetch your testnet Coordinate address.

The next step is to visit my simple TABConf6 [Testnet Distribution Portal](https://tabconf.testnet4.io) and enter your Testnet Address AND Coordinate Testnet Address.

## Phase Two - Connect and Use Python Script to Get Balance
In this phase we will start interacting with a Coordinate Sidechain node, *Please note for the sake of this demo lets not deliberately attack the public node or drain the wallets.* The first script that we will be interacting with is one that simply will let you check your ballance.

You will / should use a python virtual environment.
```
source venv/bin/activate
pip install -r requirements.txt
```
## Phase Three - Asset Transfer
THe next phase of the Coordinate demo is demonstrating asset transfers onchain. These assets have already been settled onchain and are intended to be distributed today as a little token/momento of your experience here at TABConf6. Mike will be in charge of distribution to your addresses and we will show settlement properties of the Coordinate pre-confirmed transactions that are signed for every 1 minute by the federation. To do this we will have you use my [TABConf6 Demo Admin Panel](tabconf.testnet4.io) and select the users address below your own seed word. Follow the steps below to do this. 

 1. Using the Anduro Browser wallet select Coordinate as the asset
 2. Click Send
 3. Paste in the address you fetched earlier
 4. Using the toggle select 'Premium Transaction'
 5. Send and Broadcast your transaction 

Bonus you can view your new TX on [Coordiscan](https://coordiscan.io)

After one minute at most for this group size you should notice your transaction has confirmed and a new one should enter your wallet under the assets category.

## Phase Four - Asset Creation

Now we have seen how assets can move around from address to address using the signed block method. Now be because of deliberate design decisions. Remember Coordinate pays the miners. Support for asset creation which is a large consumer of blockspace is currently limited to only occurring in the merge mined blocks that are _permissionless_

Now there are a bunch of different rules about asset creation and storage on coordinate. First of which is though it's defined as an asset. The asset can be any data even if it's not human readable or for that matter just electronic noise. It can be stored on Coordinate. The caveat is that nodes do support pruning out the blob portion of the asset after validation that the data matches the hash.

*Coordinate Consensus Rules*
1. All assets must be created in a version 10 transactions
2. Version 10 transactions have various fields
    - Precision _The divisibility of the underlying asset_
    - Ticker _The consensus level displayed Ticker (Non-Unique)
    - Tagline _Description of Asset_
    - payload _Sha256_ of the payload data
    - payload_data _The data to be stored onchain_
    - payload_type _This is a hint to the type of data the payload is storing._
3. There additional consensus rules to how a controller output can be used, these will not be discussed today.

Inside of the ```tabconf_wallet_asset_tools``` directory there is a script named ```tabconf_wallet_asset_loader.py``` we are going to use this
script to issue a 'NFT' asset using the public Coordinate node that I m hosting. Again don't attack the node until the demo is done please.
Afterward everything is fair game. 

This tool is pretty simple but will require some interaction.
 1. Fetch a coordinate address from the Anduro browser wallet you will need this to send your onchain UTXO asset to.
 2. You will also need to still use your assigned seed word.



## Conclusion
