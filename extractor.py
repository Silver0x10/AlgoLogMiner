# from pm4py.objects.log.importer.xes import importer as xes_importer
from base64 import b64decode
from datetime import datetime
import json
import sys
from opyenxes.factory.XFactory import XFactory
# from opyenxes.id.XIDFactory import XIDFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
# from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager, XTimeExtension, XConceptExtension, XIdentityExtension
from os import system
import string

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


# def jsonContains(position, jsonArray):
    # return False


###
def extractFromDict(dict, position):
    value = dict
    for pos in position.split("."):
        if(pos in value.keys()):
            value = value[pos]
        else: return None
    return value

def extractFromTransaction(transaction, position):
    value = transaction
    if(position[:4] == "note"):
        if("." in position):
            value = json.loads(b64decode(transaction["note"]).decode())
            value = extractFromDict(value, position[5:])
        else:
            value = b64decode(transaction["note"]).decode()
    else:
        value = extractFromDict(transaction, position)

    return value
###

def filterTransactions(transactions, txnFilters):
    filteredTxs = []
    for txn in transactions:
        ok = True
        for filter in txnFilters:
            value = extractFromTransaction(txn, filter)
            if(value == None):
                ok = False
                break
            if(str(value) not in txnFilters[filter]): 
                print(txnFilters[filter])
                ok = False
                break
        if(ok): filteredTxs.append(txn)
    return filteredTxs

def setEvent(txn, eventMapping, trace, switches):
    event =XFactory.create_event()
    ok = True
    for attributeKey in eventMapping:
        attributeValue = ""
        attributeType = ""
        if("static" in eventMapping[attributeKey]):
            attributeType = eventMapping[attributeKey]["static"]["type"]
            attributeValue = eventMapping[attributeKey]["static"]["value"]
        elif("parameter" in eventMapping[attributeKey]):
            attributeType = eventMapping[attributeKey]["parameter"]["type"]
            valuePosition = eventMapping[attributeKey]["parameter"]["key"]
            attributeValue = extractFromTransaction(txn, valuePosition)
            if(attributeValue == None): continue
        elif("selector" in eventMapping[attributeKey]):
            attributeType = eventMapping[attributeKey]["selector"]["type"]
            position = eventMapping[attributeKey]["selector"]["key"]
            txnValue = extractFromTransaction(txn, position)
            if(txnValue == None): 
                ok = False
                break
            case = eventMapping[attributeKey]["selector"]["value"]
            switch = switches[eventMapping[attributeKey]["selector"]["switch"]]
            if(case == txnValue and case in switch):
                attributeValue = switch[case]
            else: 
                ok = False
                break
        elif("switch" in eventMapping[attributeKey]):
            attributeType = eventMapping[attributeKey]["switch"]["type"]
            position = eventMapping[attributeKey]["switch"]["key"]
            txnValue = extractFromTransaction(txn, position)
            if(txnValue == None): 
                ok = False
                break
            switch = switches[eventMapping[attributeKey]["selector"]["switch"]]
            if(txnValue in switch):
                attributeValue = switch[txnValue]
            else: 
                ok = False
                break

        if(attributeType == "string"):
            event.get_attributes()[attributeKey] = XFactory.create_attribute_literal(attributeKey, attributeValue)
        elif(attributeType == "int"):
            event.get_attributes()[attributeKey] = XFactory.create_attribute_discrete(attributeKey, attributeValue)
        elif(attributeType == "date"):
            attributeValue = datetime.utcfromtimestamp(float(attributeValue))
            event.get_attributes()[attributeKey] = XFactory.create_attribute_timestamp(attributeKey, attributeValue)
        # event.get_attributes()[attributeKey] = XFactory.create_attribute_literal(attributeKey, attributeValue)
    # if(ok): trace.append(event)
    if(ok): trace.insert_ordered(event)


# def setTrace(transaction, trace, traceMap, eventMapping):
#     for attributeKey in traceMap:
#         if(attributeKey != "identifier:id"):
#             # ToDo
#             pass

def setTraces(transactions, traces, traceMap, eventMappings, switches):
    idAttrKey = "identifier:id"
    idAttrType = None
    idAttrValue = None
    idAttrPosition = None
    trace = None

    if("static" in traceMap[idAttrKey]):
        idAttrType = traceMap[idAttrKey]["static"]["type"]
        idAttrValue = traceMap[idAttrKey]["static"]["value"]

    elif("parameter" in traceMap[idAttrKey]):
        idAttrType = traceMap[idAttrKey]["parameter"]["type"]
        idAttrPosition = traceMap[idAttrKey]["parameter"]["key"]

    for txn in transactions:
        if("parameter" in traceMap[idAttrKey]): idAttrValue = extractFromTransaction(txn, idAttrPosition)
        
        try:
            if(idAttrValue != None):
                trace = traces[idAttrValue]
        except:
            trace = XFactory.create_trace()
            if(idAttrType == "int"):
                trace.get_attributes()[idAttrKey] = XFactory.create_attribute_discrete(idAttrKey, idAttrValue)
            elif(idAttrType == "string"):
                trace.get_attributes()[idAttrKey] = XFactory.create_attribute_literal(idAttrKey, attributeValue)
            elif(idAttrType == "date"):
                attributeValue = datetime.utcfromtimestamp(float(attributeValue))
                trace.get_attributes()[idAttrKey] = XFactory.create_attribute_timestamp(idAttrKey, attributeValue)
            traces[idAttrValue] = trace
        
        for eventMap in eventMappings:
            setEvent(txn, eventMap, trace, switches)

def sortEventsByTimestamp(trace):
    print(type(trace))

def mapLog(log, mappings, indexer, switches):
    # defaultTrace = XFactory.create_trace()
    traces = {}

    for map in mappings:
        transactions = []
        for filter in map["indexerFilters"]:
            for txn in getTransactions(indexer, filter):
                transactions.append(txn)
            
        for logMap in map["logMappings"]:
            usefulTransactions = filterTransactions(transactions, logMap["singleTxnFilters"]) # da sistemare
            # usefulTransactions = transactions

            for traceMap in logMap["traceMappings"]:
                setTraces(usefulTransactions, traces, traceMap, logMap["eventMappings"], switches)

    for traceId in traces:
        log.append(traces[traceId])
    # log.append(defaultTrace)

def extract(indexer, manifestPath):
    manifest = json.load(open(manifestPath))
    xesFilePath = "extractedEventLog.xes"

    log = XFactory.create_log()

    switches = {}
    for key in manifest:
        if(key == "xesExtensions"): setExtension(log, manifest[key])
        elif(key == "xesClassifiers"): setClassifiers(log, manifest[key])
        elif(key == "xesGlobals"): setGlobals(log, manifest[key])
        elif(key == "switches"): switches = manifest[key]
    
    try:
        mapLog(log, manifest["mappings"], indexer, switches)
    except:
        print("Missing mappings!")

    #  print(log.get_extensions().add(XTimeExtension()))

    with open(xesFilePath, "w") as file:
        XesXmlSerializer().serialize(log, file)

    # xesFile = open(xesFilePath, "w")
    # xesFile.write("""<?xml version='1.0' encoding='UTF-8'?><log></log>""")
    # xesFile.close()
    # log = xes_importer.apply(xesFilePath)
    # log = pm4py.read_xes(xesFilePath)
    # print(type(log))


