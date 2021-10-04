#!/usr/bin/python3

from base64 import b64decode
import json
from apps.algorandUtility import connectToNode, newTransaction
from algosdk.v2client import indexer

indexer_token = ""
# indexer_address = "http://localhost:8980" # local
indexer_address = "https://testnet.algoexplorerapi.io/idx2" # testnet
# indexer_address = "https://algoexplorerapi.io/idx2" # mainnet

theIndexer = indexer.IndexerClient(indexer_token, indexer_address, headers={'User-Agent': '?'})


# nexttoken = ""
# numtx = 1
# while (numtx > 0):
#     # # amazon:
#     # response = theIndexer.search_transactions(address='PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU', next_page=nexttoken)
#     # PlanetWatch:
#     # response = theIndexer.search_transactions(address='BY6UJNZ2MD3AZC2K2KQJW7W7OWPGGIBNOSZGFZQ6L426BTGO5G2FOI6VPI', address_role="sender", asset_id=27165954, min_amount=1, min_round=8712119, next_page=nexttoken)
#     response = theIndexer.search_transactions(application_id=14877441, txid="7QVCLTBMDEM3ODWQBWTLSB2ZCBOCCCDLI4ZAPAYORVZ3MZQ36ZFA", next_page=nexttoken)
    
#     transactions = response['transactions']

#     numtx = len(transactions)
#     if (numtx > 0):
#         nexttoken = response['next-token']
#         # Pretty Printing JSON string
#         # print("Transaction Info: " + json.dumps(response, indent=2, sort_keys=True))


response = theIndexer.search_transactions(application_id=14877441, txid="3MLRCBNSOOMREY7KSJRS7B5MR6PMFEGYBYU4RYFHARLT2ACZNIVA")
# response = theIndexer.search_transactions(txid="3KQS45ZAOJN7TVQ6LP5SADYZ353NJXDX7NIZE5Q4CASEZVA4TAGA")
print(json.dumps(response, indent=2, sort_keys=True))


# algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
# algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
# algod_client = connectToNode(algod_address, algod_token)



def extractFromTransaction(collection, position):
    try:
        if(position.find(".") == -1):
            if(position == "note"):
                return b64decode(collection[position]).decode()
            elif(position.isnumeric()):
                return collection[int(position)]
            else:
                return collection[position]
        else: # nested position
            if(position[:5] == "note."):
                note = json.loads(b64decode(collection["note"]).decode())
                return extractFromTransaction(note, position[5:])
            elif(position.split(".")[0].isnumeric()):
                fieldIndex = int(position.split(".")[0])
                nextPositionStart = position.find(".") + 1
                return extractFromTransaction(collection[fieldIndex], position[nextPositionStart:])
            else:
                field = position.split(".")[0]
                nextPositionStart = position.find(".") + 1
                return extractFromTransaction(collection[field], position[nextPositionStart:])
    except KeyError:
        return None

# value = extractFromTransaction(response["transactions"][0], "local-state-delta.0.delta.0.value.a")
# print("\n\n" + str(value))