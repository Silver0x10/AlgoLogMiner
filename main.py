#!/usr/bin/python3

from os import MFD_ALLOW_SEALING
from algosdk.v2client import algod, indexer
import json
from extractor import extract
# from sys import argv
import sys, getopt
# from os import system

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

def main(argv):
    indexer_token=""
    indexer_address="http://localhost:8980"
    manifestPath = ""
    xesFilePath = "extractedEventLog.xes"
    
    try:
        opts, args = getopt.getopt(argv,"hm:o:a:t:",["help", "manifest=", "output=", "indexerAddress=", "indexerToken="])
    except getopt.GetoptError:
        print('main.py <manifestPath> [-o <outputFilePath>] [-a <indexerAddress>] [-t <indexerToken>]')
        sys.exit(2)
    
    missingManifest = True
    for opt, arg in opts:
        if( opt in ("-h", "--help") ):
            print('main.py <manifestPath> [-o <outputFilePath>] [-a <indexerAddress>] [-t <indexerToken>]')
            sys.exit()
        elif( opt in ("-m", "--manifest")):
            manifestPath = arg
            missingManifest = False
        elif( opt in ("-o", "--output") ):
            xesFilePath = arg if arg.lower().endswith(('.xes')) else arg + ".xes"
        elif( opt in ("-a", "--indexerAddress") ):
            indexer_address = arg
        elif( opt in ("-t", "--indexerToken") ):
            indexer_token = arg

    if(missingManifest):
        print("Missing json manifest!")
        sys.exit(1)
    if(not manifestPath.lower().endswith(('.json'))):
        print("The manifest must be a json")
        sys.exit(1)

    theIndexer = indexer.IndexerClient(indexer_token, indexer_address)

    extract(theIndexer, manifestPath, xesFilePath)
    sys.exit(0)
    

if __name__ == "__main__":
    main(sys.argv[1:])



# algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
# algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'

# algod_client = connectToNode(algod_address, algod_token)

# response = theIndexer.search_transactions(address='PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU', )
# print(json.dumps(response, indent=2, sort_keys=True))
# return
# test(myIndexer)

# theIndexer.search_transactions(txn_type=)