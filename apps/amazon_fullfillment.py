#!/usr/bin/python3

import sys
sys.path.insert(1, '/media/InterOS/Condivise/Università/Terzo Anno/Tirocinio/ExtractingLogs/Tests')
from algorandUtility import connectToNode, newTransaction
# from Tests.algorandUtility import connectToNode, newTransaction
import json
from random import random
import os
from multiprocessing import Process
from threading import Thread

# base64.b64decode(txn["txn"]["txn"]["note"]).decode()

def receiveItems(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItemsReceived):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 10 # "Receive Items"
    data["actor"] = "Customer"
    data["n-items"] = str(nItemsReceived)
    json_data = json.dumps(data, indent=2)
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
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
    # print(json_data)
    
    return accepted


def checkout(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems):
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
        newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)
        # print(json_data)

        paymentAccepted = takePayment(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client)
        
        if(paymentAccepted): # Send Order
            # sendOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItems)
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
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)

    # Done Shopping?
    if(random() > 0.5): # No
        return browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)
    else: # Yes
        return checkout(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)

def browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart):
    data = {}
    data["trace-id"] = str(TraceId)
    data["event-name"] = 0 # "Browse Products on Amazon"
    data["actor"] = "Customer"
    json_data = json.dumps(data, indent=2)
    newTransaction(algod_client, managerAddr, managerPassphrase, receiverAddr, 0, json_data)

    return addItemToCart(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, itemsInTheCart)
    

def newOrderTrace(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client):
    nItemsOrdered = browseProducts(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, 0)
    if(nItemsOrdered): sendOrder(TraceId, managerAddr, managerPassphrase, receiverAddr, algod_client, nItemsOrdered)

def test(id):
    print(id)

def mainMultiprocess(idFirstNewTrace, nuoveTracce):
    algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
    algod_client = connectToNode(algod_address, algod_token)

    manager1 = "PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU"
    passphrase = "wolf profit edge place venture once fatal rifle iron able bounce capital section poet dignity artefact mandate mutual music tree hover mimic moment ability hotel"
    fantoccio = "IWBZYBPTO4INJBALPJ3PDUPPSBKTGIYVIY3PCGL6LRJCIBEIIIKSF7UL2Y"
    
    processes = []
    while(nuoveTracce > 0):
        x = min(os.cpu_count(), nuoveTracce)
        for i in range(x):
            print("Trace Id: " + str(idFirstNewTrace+i))
            processes.append(Process(target=newOrderTrace(idFirstNewTrace+i, manager1, passphrase, fantoccio, algod_client)))
            # processes.append(Process(target=test(idFirstNewTrace+i)))

        for process in processes:
            process.start()

        for process in processes:
            process.join()
        nuoveTracce = nuoveTracce - x


def main(idFirstNewTrace):
    algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
    algod_client = connectToNode(algod_address, algod_token)

    manager1 = "PF3G3CHB4F2AFYNB5U2GM7Z3MZ4CQKXH65J4GBQHXJIYOIQ6VEGJXBPBXU"
    passphrase = "wolf profit edge place venture once fatal rifle iron able bounce capital section poet dignity artefact mandate mutual music tree hover mimic moment ability hotel"
    fantoccio = "IWBZYBPTO4INJBALPJ3PDUPPSBKTGIYVIY3PCGL6LRJCIBEIIIKSF7UL2Y"

    newOrderTrace(idFirstNewTrace, manager1, passphrase, fantoccio, algod_client)


with open("./nextTraceId.txt", "r") as file:
    idFirstNewTrace = int(file.readline())

nuoveTracce = int(sys.argv[1])
print(nuoveTracce)

# main(idFirstNewTrace)
mainMultiprocess(idFirstNewTrace, nuoveTracce)

idFirstNewTrace = idFirstNewTrace + nuoveTracce
with open("./nextTraceId.txt", "w") as file:
    file.write(str(idFirstNewTrace))
