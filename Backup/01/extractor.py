# from pm4py.objects.log.importer.xes import importer as xes_importer
from datetime import datetime
import json
import sys
from opyenxes.factory.XFactory import XFactory
# from opyenxes.id.XIDFactory import XIDFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
# from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager, XTimeExtension, XConceptExtension, XIdentityExtension
from os import system
def setExtension(log, extList):
    for ext in extList:
        if(ext["name"] == "Time"): log.get_extensions().add(XTimeExtension())
        elif(ext["name"] == "Identity"): log.get_extensions().add(XIdentityExtension())
        elif(ext["name"] == "Concept"): log.get_extensions().add(XConceptExtension())

def setClassifiers(log, clsList):
    return

def setGlobals(log, glbList):
    return 

def getTransactions(indexer, indexerFilters, genTxsJson=True):
    searchString = "indexer.search_transactions("
    for filter in indexerFilters:
        if(filter["type"] == "address" or filter["type"] == "string"):
            searchString += filter["key"] + "='" + filter["val"] + "', "
        elif(filter["type"] == "int"):
            searchString += filter["key"] + "=" + filter["val"] + ", "
    searchString = searchString + "next_page='')"

    transactions = []
    nexttoken = ""
    numtx = 1
    while (numtx > 0):
        # response = indexer.search_transactions(min_round=minRound, max_round=maxRound, next_page=nexttoken)
        searchString = searchString[:searchString.find("next_page=")] + "next_page='" + nexttoken + "')"
        response = eval(searchString)
        numtx = len(response["transactions"])
        if (numtx > 0):
            for tx in response["transactions"]: transactions.append(tx)
            nexttoken = response["next-token"]

    # if(genTxsJson):
    #     with open("./transactions/txs.json", "w") as f:
    #         json.dump(transactions, f, indent=2, sort_keys=True)
    return transactions    

def filterTransactions(transactions, filters):
    filteredTxs = []
    for tx in transactions:
        ok = True
        for f in filters:
            if("." in f):
                value = tx
                for pos in f.split("."):
                    if(pos in value): value = value[pos]
                    else:
                        ok = False
                        break
            elif(f in tx): 
                value = tx[f]
            else:
                ok = False
                break
            if(str(value) not in filters[f]): 
                ok = False
                break
        if(ok): filteredTxs.append(tx)
    return filteredTxs

# ????????????????????????????????????
def setTrace(transactions, trace):
    return

def setEvent(transactions, eventMappings, trace):

    for tx in transactions:
        event =XFactory.create_event()
        for attributeKey in eventMappings:
            attributeValue = ""
            attributeType = ""
            if("static" in eventMappings[attributeKey]):
                attributeType = eventMappings[attributeKey]["static"]["type"]
                attributeValue = eventMappings[attributeKey]["static"]["value"]
            elif("parameter" in eventMappings[attributeKey]):
                attributeType = eventMappings[attributeKey]["parameter"]["type"]
                valuePosition = eventMappings[attributeKey]["parameter"]["key"]
                if("." in valuePosition):
                    attributeValue = tx
                    for pos in valuePosition.split("."):
                        attributeValue = attributeValue[pos]
                else: attributeValue = tx[valuePosition]

            if(attributeType == "string"):
                event.get_attributes()[attributeKey] = XFactory.create_attribute_literal(attributeKey, attributeValue)
            elif(attributeType == "int"):
                event.get_attributes()[attributeKey] = XFactory.create_attribute_discrete(attributeKey, attributeValue)
            elif(attributeType == "date"):
                attributeValue = datetime.utcfromtimestamp(float(attributeValue))
                event.get_attributes()[attributeKey] = XFactory.create_attribute_timestamp(attributeKey, attributeValue)
        trace.append(event)

def mapAccount(log, accountMappings, indexer):
    defaultTrace = XFactory.create_trace()
    for map in accountMappings:
        transactions = getTransactions(indexer, map["indexerFilters"])

        for logMap in map["logMappings"]:
            usefulTransactions = filterTransactions(transactions, logMap["filters"])
            for trace in logMap["traceMappings"]:
                setTrace(usefulTransactions, trace)
            for event in logMap["eventMappings"]:
                setEvent(usefulTransactions, event, defaultTrace)
    log.append(defaultTrace)

def extract(indexer, manifestPath):
    manifest = json.load(open(manifestPath))
    xesFilePath = "extractedEventLog.xes"

    log = XFactory.create_log()

    
    for key in manifest:
        if(key == "xesExtensions"): setExtension(log, manifest[key])
        elif(key == "xesClassifiers"): setClassifiers(log, manifest[key])
        elif(key == "xesGlobals"): setGlobals(log, manifest[key])
        elif(key == "accountMappings"): mapAccount(log, manifest[key], indexer)

    #  print(log.get_extensions().add(XTimeExtension()))

    with open(xesFilePath, "w") as file:
        XesXmlSerializer().serialize(log, file)

    # xesFile = open(xesFilePath, "w")
    # xesFile.write("""<?xml version='1.0' encoding='UTF-8'?><log></log>""")
    # xesFile.close()
    # log = xes_importer.apply(xesFilePath)
    # log = pm4py.read_xes(xesFilePath)
    # print(type(log))


