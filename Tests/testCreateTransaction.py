# from algosdk.v2client import algod
# from algosdk import account, mnemonic
# from algosdk.future.transaction import PaymentTxn
# import base64, json
from algorandUtility import connectToNode, newTransaction

algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
algod_client = connectToNode(algod_address, algod_token)


# Wallet name: AmazonWallet
# New account: PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU

sender = "TNPPM566QZLEUFZHP4J4F3D2BHKOD22WYXPKN4ZBHOLDCA2PVCXBVX224Y"
passphrase = "another despair autumn flash lawn bomb popular over tennis art gap stairs derive whip property gap green fade rookie summer feature laptop drift about worry"
receiver = "PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU"
amount = 1000000000000000
note = "Ciao"

newTransaction(algod_client, sender, passphrase, receiver, amount, note)



