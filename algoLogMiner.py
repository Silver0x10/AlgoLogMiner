#!/usr/bin/python3

import argparse
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


def main(indexer_token, indexer_address, manifestPath, outputXesPath):
    theIndexer = indexer.IndexerClient(indexer_token, indexer_address, headers={'User-Agent': '?'})

    extract(theIndexer, manifestPath, outputXesPath)
    sys.exit(0)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("manifest", help="Manifest path. This document is needed by the extractor to generate the xes file")
    parser.add_argument("-o", "--output", help="Path of the xes that will be generated", default="extractedEventLog.xes")
    parser.add_argument("-t", "--indexerToken", help="Token of the indexer", default="")
    parser.add_argument("-a", "--indexerAddress", help="Address of the indexer. Do not use with option -b", default="http://localhost:8980")
    parser.add_argument("-b", "--blockchain", choices=["testnet", "betanet", "mainnet"], help="Select the network between: Testnet indexer at https://testnet.algoexplorerapi.io/idx2; Betanet indexer at https://betanet.algoexplorerapi.io/idx2; Mainnet indexer at https://algoexplorerapi.io/idx2. Do not use with option -a. ")
    args = parser.parse_args()

    manifestPath = args.manifest
    if(not manifestPath.lower().endswith(('.json'))):
        print("The manifest must be a json")
        sys.exit(1)

    xesFilePath = args.output if args.output.lower().endswith(('.xes')) else args.output + ".xes"
    indexer_token = args.indexerToken
    if(args.blockchain == "testnet"):
        indexer_address = "https://testnet.algoexplorerapi.io/idx2"
    elif(args.blockchain == "betanet"):
        indexer_address = "https://betanet.algoexplorerapi.io/idx2"
    elif(args.blockchain == "mainnet"):
        indexer_address = "https://algoexplorerapi.io/idx2"
    else:
        indexer_address = args.indexerAddress

    main(indexer_token, indexer_address, manifestPath, xesFilePath)
