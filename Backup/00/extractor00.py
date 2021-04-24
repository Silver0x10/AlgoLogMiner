# from pm4py.objects.log.importer.xes import importer as xes_importer
from datetime import datetime
import json
from time import time
from opyenxes.factory.XFactory import XFactory
# from opyenxes.id.XIDFactory import XIDFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
# from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager, XTimeExtension, XConceptExtension, XIdentityExtension


def setExtension(log, extList):
    for ext in extList:
        if(ext["name"] == "Time"): log.get_extensions().add(XTimeExtension())
        elif(ext["name"] == "Identity"): log.get_extensions().add(XIdentityExtension())
        elif(ext["name"] == "Concept"): log.get_extensions().add(XConceptExtension())

def setClassifiers(log, clsList):
    return

def setGlobals(log, glbList):
    return 

def getTransactions(indexer, minRound, maxRound, genTxsJson=False):
    transactions = []
    nexttoken = ""
    numtx = 1
    while (numtx > 0):
        response = indexer.search_transactions(min_round=minRound, max_round=maxRound, next_page=nexttoken)
        numtx = len(response["transactions"])
        if (numtx > 0):
            for tx in response["transactions"]: transactions.append(tx)
            # print(type(response["transactions"]))
            nexttoken = response["next-token"]
    if(genTxsJson):
        with open("./transactions.json", "w") as f:
            json.dump(transactions, f, indent=2, sort_keys=True)
    return transactions    

def setAlgoNimEvents(trace, traceData, indexer):
    trace.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Match 1")

    dealer = traceData["addresses"][0]
    opponent = traceData["addresses"][1]
    sink = traceData["addresses"][2]
    table = traceData["addresses"][3]
    escrowP1 = traceData["addresses"][4]
    escrowP2 = traceData["addresses"][5]
    minRound = int(traceData["minRound"])
    maxRound = int(traceData["maxRound"])
    piecesID = int(traceData["piecesAssetID"])
    turnID = int(traceData["turnAssetID"])

    trace.get_attributes()["dealer"] = XFactory.create_attribute_literal("dealer", dealer)
    attr = XFactory.create_attribute_literal("opponent", opponent)
    trace.get_attributes()["opponent"] = attr

    transactions = getTransactions(indexer, minRound, maxRound)
    for tx in transactions:
        txOfTheTrace = True
        event = XFactory.create_event()
        event.get_attributes()["round"] = XFactory.create_attribute_discrete("round", tx["confirmed-round"])
        
        if(tx["tx-type"] == "acfg" and tx["created-asset-index"] == piecesID):
            amount = tx["asset-config-transaction"]["params"]["total"]
            attr = XFactory.create_attribute_literal("concept:name", "Dealer gen. " + str(amount) + " AlgoNimP")
            attr.get_attributes()["test"] = XFactory.create_attribute_literal("test", "nested attr")
            event.get_attributes()["name"] = attr
        
        elif(tx["tx-type"] == "acfg" and tx["created-asset-index"] == turnID):
            amount = tx["asset-config-transaction"]["params"]["total"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Dealer gen. " + str(amount) + " AlgoNimT")
        
        elif(tx["tx-type"] == "pay" and tx["id"] == "YR7HI5IYSKSNKME5TRV3X5OA55YJZCA2XK7HWLEQM7TGAANYBBLA"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Sink generation")
        
        elif(tx["tx-type"] == "axfer"and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["id"] == "OEL4TDVPCFYCSOESBXFJTDZRDG3FS3EK7JHYWU35XP7PACDIJFJQ"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Sink to Sink 0 AlgoNimP")
        
        elif(tx["tx-type"] == "pay" and tx["id"] == "LFXWYYAHYC53LEASOGQBY6WOISHVV3XTHM5CTNRMHAFQBIIAA6AA"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Table generation")
        
        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["id"] == "Z5YUXBX2I2QUQ2HKJDFPILOQDDNFIZIPWEKXTK7LZBVVRS4X5Y4Q"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Table to Table 0 AlgoNimP")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])
        
        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["id"] == "XNUFDE3WVSU7GV44IPPO3E2HM5YB75IOOTY3MWM3EW2CHPLNGUBA"):
            amount = tx["asset-transfer-transaction"]["amount"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Dealer to Table " + str(amount) + " AlgoNimP")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])
        
        elif(tx["tx-type"] == "pay" and tx["id"] == "VBEWDNEF6WFTI7ICZTLZAXGCP4LZKBCIMI2AVCYHRJWGXXL6274Q"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Escrow1 creation")
        
        elif(tx["tx-type"] == "pay" and tx["id"] == "4FKCCZPNENGXPXMTNI23IXMWPJMGKWZL3L5ZZ7LBIL3CKVF2KXAA"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Escrow2 creation")

        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["id"] == "FH622WNEDGIUI6UPVX3B65J3Y6ESABKYDQ57RVJQAMSWTCJCEQTA"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Opponent to Opponent 0 AlgoNimP")

        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == turnID and tx["id"] == "BJULMBZP3WFKK7SFRG62RWOE7NR735UT7DLXG7WTLEOLPXOUVNQA"):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Opponent to Opponent 0 AlgoNimT")

        elif(tx["tx-type"] == "pay" and tx["id"] == "AKPFVHFMFM7TQI56MJQJLXT23APWZTVX7ZTL54B4PH5U2QJ5GPIQ"):
            amount = tx["payment-transaction"]["amount"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Dealer bets " + str(amount) + " microAlgos (to Escrow1)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        elif(tx["tx-type"] == "pay" and tx["id"] == "6WG7YBJT4QC3Q5KAN4RDEQQSTMWYBF5IXYLTDQZIDTWZTUZITAKQ"):
            amount = tx["payment-transaction"]["amount"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Opponent bets " + str(amount) + " microAlgos (to Escrow2)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        # Moves
        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == turnID and tx["sender"] == dealer and tx["asset-transfer-transaction"]["receiver"] == opponent):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Dealer Turn (AlgoNimT to Opponent)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == turnID and tx["sender"] == opponent and tx["asset-transfer-transaction"]["receiver"] == dealer):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Opponent Turn (AlgoNimT to Dealer)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["sender"] == table and tx["asset-transfer-transaction"]["receiver"] == sink):
            numPieces = tx["asset-transfer-transaction"]["amount"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", str(numPieces) + " AlgoNimP Moved (From Table to Sink)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        # End
        elif(tx["tx-type"] == "axfer" and tx["asset-transfer-transaction"]["asset-id"] == piecesID and tx["sender"] == sink and tx["asset-transfer-transaction"]["receiver"] == dealer):
            numPieces = tx["asset-transfer-transaction"]["amount"]
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "All " + str(numPieces) + " AlgoNimP to the winner (Dealer)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        # Bet to the winner
        elif(tx["tx-type"] == "pay" and tx["sender"] == escrowP2 and tx["payment-transaction"]["receiver"] == dealer):
            event.get_attributes()["name"] = XFactory.create_attribute_literal("concept:name", "Payment to the winner (Dealer)")
            event.get_attributes()["group"] = XFactory.create_attribute_literal("group", tx["group"])

        else: txOfTheTrace = False
        
        event.get_attributes()["time"] = XFactory.create_attribute_timestamp("time:timestamp", tx["round-time"])
        event.get_attributes()["round"] = XFactory.create_attribute_discrete("round", tx["confirmed-round"])
        if(txOfTheTrace): trace.append(event)

def setTraces(log, traces, indexer):
    for tr in traces:
        trace = XFactory.create_trace()
        
        # Specific for AlgoNim
        setAlgoNimEvents(trace, tr, indexer)

        log.append(trace)

def extract(indexer, manifestPath):
    manifest = json.load(open(manifestPath))
    xesFilePath = "extractedEventLog.xes"

    log = XFactory.create_log()

    
    for key in manifest:
        if(key == "xesExtensions"): setExtension(log, manifest[key])
        elif(key == "xesClassifiers"): setClassifiers(log, manifest[key])
        elif(key == "xesGlobals"): setGlobals(log, manifest[key])
        elif(key == "mappings"): setTraces(log, manifest[key], indexer)

    #  print(log.get_extensions().add(XTimeExtension()))

    with open(xesFilePath, "w") as file:
        XesXmlSerializer().serialize(log, file)

    # xesFile = open(xesFilePath, "w")
    # xesFile.write("""<?xml version='1.0' encoding='UTF-8'?><log></log>""")
    # xesFile.close()
    # log = xes_importer.apply(xesFilePath)
    # log = pm4py.read_xes(xesFilePath)
    # print(type(log))


