#!/usr/bin/python3

import sys
from urllib import parse
# sys.path.insert(1, '/media/InterOS/Condivise/Università/Terzo Anno/Tirocinio/ExtractingLogs/Tests')
from algorandUtility import newTransaction
import json
from random import random
import os
from multiprocessing import Process
from threading import Thread
import argparse
from algosdk.v2client import algod

# base64.b64decode(txn["txn"]["txn"]["note"]).decode()

def receiveItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItemsReceived):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 10 # "Receive Items"
    data["actor"] = "Customer"
    data["n-items"] = str(nItemsReceived)
    json_data = json.dumps(data, indent=2)
    print("receive items")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return nItemsReceived


def deliverItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 9 # "Deliver Items"
    data["actor"] = "Carrier"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("deliver items")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return receiveItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def loadTruck(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 8 # "Load Truck"
    data["actor"] = "Carrier"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("load truck")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return deliverItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def sendToCarrierDock(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 7 # "Send to Carrier Dock"
    data["actor"] = "Amazon Packager"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("send to carrier dock")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return loadTruck(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def receiveAndPackageItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 6 # "Receive and Package Items"
    data["actor"] = "Amazon Packager"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("receive and package items")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return sendToCarrierDock(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def placeInBin(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 5 # "Place in Bin"
    data["actor"] = "Amazon Picker"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("place in bin")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return receiveAndPackageItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def pickItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 4 # "Pick Items"
    data["actor"] = "Amazon Picker"
    data["n-items"] = str(nItems)
    json_data = json.dumps(data, indent=2)
    print("pick items")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)

    return placeInBin(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def sendOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    return pickItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)


def takePayment(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client):
    accepted = False
    if(random() <= 0.7):
        accepted = True
    
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 3 # "Take Payment"
    data["actor"] = "Credit Card Company"
    data["accepted"] = str(accepted)
    json_data = json.dumps(data, indent=2)
    print("take payment")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)
    
    return accepted


def payOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
    tryPayment = True
    attempts = 1
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 2 # "Pay Order"
    data["actor"] = "Customer"
    data["n-items"] = str(nItems)

    while(tryPayment):
        data["attempt-num"] = str(attempts)
        json_data = json.dumps(data, indent=2)
        print("pay order")
        newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
        # print(json_data)

        paymentAccepted = takePayment(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client)
        
        if(paymentAccepted): # Send Order
            return nItems
        elif(random() > 0.9):
            tryPayment = False
        else:
            tryPayment = True
        
        attempts += 1

    print("Not retry")
    return 0 # Not Retry
                

def addItemToCart(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart):
    itemsInTheCart += 1
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 1 # "Add Item to Cart"
    data["n-items"] = str(itemsInTheCart)
    data["actor"] = "Customer"
    json_data = json.dumps(data, indent=2)
    print("add item to cart")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)

    # Done Shopping?
    if(random() > 0.5): # No
        return browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)
    else: # Yes
        return payOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)

def browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 0 # "Browse Products on Amazon"
    data["actor"] = "Customer"
    json_data = json.dumps(data, indent=2)
    print("browse products")
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)

    return addItemToCart(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)
    

def newOrderTrace(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client):
    nItemsOrdered = browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, 0)
    if(nItemsOrdered): sendOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItemsOrdered)



def main(algod_client,idFirstNewTrace, newTraces):
    manager = "AIRPL6IIM55OMANZL52HFUYYKXDS3LEROEVZ4SJLRDWS4D3MOHMRQWTVL4"
    passphrase = "smooth simple elegant orchard grass aware much stuff all soup spy pilot ring country marriage dirt spy claw canvas yard lucky book marriage able coffee"
    fantoccio = "V63MNOIIVZFST63GSWDVAIDSWUFSV5UXSKMN3T3EB4DHNGFUPFFZIG3A6Y"

    
    for i in range(newTraces):
        print("Trace Id: " + str(idFirstNewTrace+i))
        newOrderTrace(idFirstNewTrace+i, manager, passphrase, fantoccio, algod_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("traces", help="Number of new traces", type=int)
    parser.add_argument("--testnet", help="New transactions on the testnet", action="store_true")
    parser.add_argument("--address", help="Algorand Node address", default="http://localhost:4001")
    parser.add_argument("--token", help="Algorand Node token", default="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    parser.add_argument("--nextTraceIdFile", help="File containing the id of the next trace", default="./nextTraceId.txt")
    args = parser.parse_args()
    if args.testnet:
        algod_address = "https://testnet.algoexplorerapi.io" 
        algod_token = ""
        nextIdFile = "./nextTraceId.txt"
    else:
        algod_address = args.address 
        algod_token = args.token
        nextIdFile = args.nextTraceIdFile

    with open(nextIdFile, "r") as file:
        idFirstNewTrace = int(file.readline())

    newTraces = int(args.traces)
    algod_client = algod.AlgodClient(algod_token, algod_address, headers={'User-Agent': '?'})
    main(algod_client, idFirstNewTrace, newTraces)

    idFirstNewTrace = idFirstNewTrace + newTraces
    with open(nextIdFile, "w") as file:
        file.write(str(idFirstNewTrace))