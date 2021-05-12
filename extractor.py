# from pm4py.objects.log.importer.xes import importer as xes_importer
from base64 import b64decode
from datetime import datetime
import json
import sys
from opyenxes.classification.XEventAttributeClassifier import XEventAttributeClassifier
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from opyenxes.factory.XFactory import XFactory
# from opyenxes.id.XIDFactory import XIDFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
# from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager, XTimeExtension, XConceptExtension, XIdentityExtension
from os import system

def attributeFactory(key, value, type):
    attribute = None
    if(type in ["bool", "boolean"]):
        if(value.lower() in ["True", "true"]): value = True
        elif(value.lower() in ["False", "false"]): value = False
        else: value = None
        attribute = XFactory.create_attribute_boolean(key, value)
    elif(type == "float"):
        attribute = XFactory.create_attribute_continuous(key, float(value))
    elif(type == "int"):
        attribute = XFactory.create_attribute_discrete(key, int(value))
    elif(type == "string"):
        attribute = XFactory.create_attribute_literal(key, value)
    elif(type == "date"):
        attributeValue = datetime.utcfromtimestamp(float(value))
        attribute = XFactory.create_attribute_timestamp(key, attributeValue)
    else:
        print('Not supported attribute type: "' + type + '"')
        sys.exit(1)
    # Not yet implemented: map, id, list, container
    return attribute

def setExtension(log, extList):
    for ext in extList:
        if(ext["name"] == "Time"): log.get_extensions().add(XTimeExtension())
        elif(ext["name"] == "Identity"): log.get_extensions().add(XIdentityExtension())
        elif(ext["name"] == "Concept"): log.get_extensions().add(XConceptExtension())

def setGlobals(log, globalAttributes):
    logAttrList = None
    for element in globalAttributes:
        if(element["scope"] == "event"):
            logAttrList = log.get_global_event_attributes()
        elif(element["scope"] == "trace"):
            logAttrList = log.get_global_trace_attributes()
        logAttrList.append(attributeFactory(element["key"], element["value"], element["type"]))

def setClassifiers(log, classifierList):
    for classifier in classifierList:
        log.get_classifiers().append(XEventAttributeClassifier(classifier["name"], classifier["keys"]))

def getTransactions(indexer, indexerFilters):
    searchString = "indexer.search_transactions("
    for filter in indexerFilters: # da sistemare in base agli argomenti di search_transactions e al loro tipo
        if(filter["type"] == "address" or filter["type"] == "string"):
            searchString += filter["key"] + "='" + filter["val"] + "', "
        elif(filter["type"] == "int"):
            searchString += filter["key"] + "=" + filter["val"] + ", "
    searchString = searchString + "next_page='')"

    transactions = []
    nexttoken = ""
    numtx = 1
    while (numtx > 0):
        searchString = searchString[:searchString.find("next_page=")] + "next_page='" + nexttoken + "')"
        response = eval(searchString)
        numtx = len(response["transactions"])
        if (numtx > 0):
            for tx in response["transactions"]: transactions.append(tx)
            nexttoken = response["next-token"]

    # if(genTxsJson):
    #     with open("./transactions/"+ txnsFileName +".json", "w") as f:
    #         json.dump(transactions, f, indent=2, sort_keys=True)
    return transactions    

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
    if(position[:5] == "note." or position == "note"):
        if("." in position):
            # print(unicode(b64decode(transaction["note"])), errors='ignore')
            try:
                value = json.loads(b64decode(transaction["note"]).decode())
            except:
                return None
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


def getAttributeData(transaction, attributeKey, mapping, switches):
    attributeValue = ""
    attributeType = ""
    if("static" in mapping[attributeKey]):
        attributeType = mapping[attributeKey]["static"]["type"]
        attributeValue = mapping[attributeKey]["static"]["value"]
    elif("parameter" in mapping[attributeKey]):
        attributeType = mapping[attributeKey]["parameter"]["type"]
        valuePosition = mapping[attributeKey]["parameter"]["key"]
        attributeValue = extractFromTransaction(transaction, valuePosition)
        if(attributeValue == None):
            return None
    elif("selector" in mapping[attributeKey]):
        attributeType = mapping[attributeKey]["selector"]["type"]
        position = mapping[attributeKey]["selector"]["key"]
        txnValue = str(extractFromTransaction(transaction, position))
        if(txnValue == None): 
            return None
        case = mapping[attributeKey]["selector"]["value"]
        switch = switches[mapping[attributeKey]["selector"]["switch"]]
        if(case == txnValue and case in switch):
            attributeValue = switch[case]
        else: 
            return None
    elif("switch" in mapping[attributeKey]):
        attributeType = mapping[attributeKey]["switch"]["type"]
        position = mapping[attributeKey]["switch"]["key"]
        txnValue = str(extractFromTransaction(transaction, position))
        if(txnValue == None): 
            return None
        switch = switches[mapping[attributeKey]["switch"]["switch"]]
        if(txnValue in switch):
            attributeValue = switch[txnValue]
        else: 
            return None
    return (attributeValue, attributeType)

def setEvent(txn, eventMapping, trace, switches):
    event =XFactory.create_event()
    ok = True

    for attributeKey in eventMapping:
        attributeData = getAttributeData(txn, attributeKey, eventMapping, switches)
        if(attributeData != None):
            event.get_attributes()[attributeKey] = attributeFactory(attributeKey, attributeData[0], attributeData[1])
        elif("nullable" not in eventMapping[attributeKey] or not eventMapping[attributeKey]["nullable"]):
            ok = False
            break
    
    if(ok and len(event.get_attributes()) != 0): trace.insert_ordered(event)

def setTrace(idAttrKey, idAttrValue, idAttrType, transaction, traceMap, switches):
    trace = XFactory.create_trace()
    trace.get_attributes()[idAttrKey] = attributeFactory(idAttrKey, idAttrValue, idAttrType)
    for attributeKey in traceMap:
        if(attributeKey != "identifier:id"):
            attributeData = getAttributeData(transaction, attributeKey, traceMap, switches)
            if(attributeData != None):
                attributeValue = attributeData[0]
                attributeType = attributeData[1]
                trace.get_attributes()[attributeKey] = attributeFactory(attributeKey, attributeValue, attributeType)
            elif("nullable" not in traceMap[attributeKey] or not traceMap[attributeKey]["nullable"]):
                return None
    return trace

def setTraces(transactions, traces, traceMap, eventMappings, switches):
    idAttrKey = "identifier:id"

    for txn in transactions:
        data = getAttributeData(txn, idAttrKey, traceMap, switches)
        if(data == None): continue
        idAttrValue, idAttrType = data

        try:
            if(idAttrValue != None):
                trace = traces[idAttrValue]
        except:
            trace = setTrace(idAttrKey, idAttrValue, idAttrType, txn, traceMap, switches)
            if(trace == None): continue
            traces[idAttrValue] = trace
        
        for eventMap in eventMappings:
            setEvent(txn, eventMap, trace, switches)

def mapLog(log, mappings, indexer, switches):
    traces = {}

    for map in mappings:
        transactions = []
        for filter in map["indexerFilters"]:
            for txn in getTransactions(indexer, filter):
                transactions.append(txn)
            
        for logMap in map["logMappings"]:
            usefulTransactions = filterTransactions(transactions, logMap["singleTxnFilters"])
            usefulTransactions.reverse()
            for traceMap in logMap["traceMappings"]:
                setTraces(usefulTransactions, traces, traceMap, logMap["eventMappings"], switches)

    
    for traceId in traces:
        log.append(traces[traceId])

def extract(indexer, manifestPath, xesFilePath):
    manifest = json.load(open(manifestPath))

    log = XFactory.create_log()

    switches = {}
    for key in manifest:
        if(key == "xesExtensions"): setExtension(log, manifest[key])
        elif(key == "xesClassifiers"): setClassifiers(log, manifest[key])
        elif(key == "xesGlobals"): setGlobals(log, manifest[key])
        elif(key == "switches"): switches = manifest[key]
    
    try:
        mappings = manifest["mappings"]
    except:
        print("Missing mappings in the manifest!")
    mapLog(log, mappings, indexer, switches)

    with open(xesFilePath, "w") as file:
        XesXmlSerializer().serialize(log, file)


    # xesFile = open(xesFilePath, "w")
    # xesFile.write("""<?xml version='1.0' encoding='UTF-8'?><log></log>""")
    # xesFile.close()
    # log = xes_importer.apply(xesFilePath)
    # log = pm4py.read_xes(xesFilePath)
    # print(type(log))