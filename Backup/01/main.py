from algosdk.v2client import algod, indexer
import json
from extractor import extract
from sys import argv
from os import system

def connectToNode(algod_address, algod_token, verbose=False):
    # create an algod client
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # check node status
    status = algod_client.status()
    if(verbose): print(json.dumps(status, indent=4))

    # check suggested transansaction parameters
    try:
        params = algod_client.suggested_params()
        if(verbose): 
            # print(json.dumps(params, indent=4)) # is not JSON serializable
            print('{\n    "fee": ' + str(params.fee)) 
            print('    "genesis-hash": ' + params.gh)
            print('    "genesis-id": ' + params.gen)
            print('    "last-round": ' + str(params.last))
            print('    "min-fee": ' + str(params.min_fee) + '\n}')
    except Exception as e:
        print(e)

    return algod_client

def test(myIndexer):
    nexttoken = ""
    numtx = 1
    while (numtx > 0):
        response = myIndexer.search_transactions(min_round=16000, max_round=18500, next_page=nexttoken)
        transactions = response["transactions"]
        numtx = len(transactions)
        if (numtx > 0):
            nexttoken = response["next-token"]
            print(json.dumps(response, indent=2, sort_keys=True))

def main():
    # algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
    # algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
    # algod_client = connectToNode(algod_address, algod_token)

    theIndexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")
    # response = theIndexer.search_transactions(address='GAJNKNP55OKQJ3SYLTJWNL5Z5I6SF2X42LGKETLVPKMGLJGS2IXVCXR4CI')
    # print(json.dumps(response, indent=2, sort_keys=True))
    # response = myIndexer.search_transactions(address="LDTTNQK5JZUDY3PI7AKXQ6XRNQN3AG4PFY5R7YDNWD2XJEZU6CE2DLJ4SU")
    # test(myIndexer)

    # theIndexer.search_transactions(txn_type=)

    manifestPath = argv[1] #"./algoNimManifest.json"
    extract(theIndexer, manifestPath)

# system("mkdir ./transactions")
# system("rm ./transactions/*")
main()
