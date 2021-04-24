from algosdk.v2client import algod
import json
from algosdk import account, mnemonic
from algosdk.v2client import indexer
from algosdk.future.transaction import PaymentTxn
import base64

def connectToNode(algod_address, algod_token):
    print("## START connection to node function ##\n")

    # create an algod client
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # check node status
    status = algod_client.status()
    print(json.dumps(status, indent=4))

    # check suggested transansaction parameters
    try:
        params = algod_client.suggested_params()
        # print(json.dumps(params, indent=4)) # is not JSON serializable
        print('{\n    "fee": ' + str(params.fee)) 
        print('    "genesis-hash": ' + params.gh)
        print('    "genesis-id": ' + params.gen)
        print('    "last-round": ' + str(params.last))
        print('    "min-fee": ' + str(params.min_fee) + '\n}')
    except Exception as e:
        print(e)
    
    print("# END connection to node function #\n")

    return algod_client

def generate_algorand_keypair():
    print("## START keypair generator ##\n")

    private_key, address = account.generate_account()
    print("New address: {}".format(address))
    print("New passphrase: {}".format(mnemonic.from_private_key(private_key)) + "\n")

    print("# END keypair generator #\n")

    return (private_key, address)

def configIndexer():
    print("## START Indexer configuration ##\n")

    # instantiate indexer client
    myIndexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")

    print("# END Indexer configuration #\n")

    return myIndexer

def createSignedTxn(algod_client, sender, passphrase, receiver, microAlgos, note):
    params = algod_client.suggested_params()
    note = note.encode()
    params.fee = 1000
    params.flat_fee = True
    unsigned_txn = PaymentTxn(sender, params, receiver, microAlgos, None, note)
    signed_txn = unsigned_txn.sign(mnemonic.to_private_key(passphrase))
    return signed_txn

def waitForConfirmation(client, txnId, timeout):
    startRound = client.status()["last-round"] + 1
    currentRound = startRound

    while currentRound < startRound + timeout:
        client.status_after_block(currentRound)
        try:
            pendingTxn = client.pending_transaction_info(txnId)
        except Exception:
            return
        if pendingTxn.get("confirmed-round", 0) > 0: return pendingTxn
        elif pendingTxn["pool-error"]:  
            raise Exception(
                'pool error: {}'.format(pendingTxn["pool-error"]))
        currentRound += 1
    raise Exception( 'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

def printAccountInfo(algodClient, address):
    print("Address: {}".format(address))
    account_info = algodClient.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

def newTransaction(algod_client, sender, passphrase, receiver, amount, note):
    signedTxn = createSignedTxn(algod_client, sender, passphrase, receiver, amount, note)
    txid = algod_client.send_transaction(signedTxn)
    try:
        confirmedTxn = waitForConfirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
    print("txID: {}".format(txid), " confirmed in round {}".format(confirmedTxn.get("confirmed-round", 0)))
    # print("Transaction info: {}".format(json.dumps(confirmedTxn, indent=2)))
    print("Decoded note: {}\n".format(base64.b64decode(confirmedTxn["txn"]["txn"]["note"]).decode()))

# def main():
#     algod_address = "http://localhost:4001" # see with 'cat $ALGORAND_DATA/algod.net' localhost:4001
#     algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # see with 'cat $ALGORAND_DATA/algod.token'
#     algod_client = connectToNode(algod_address, algod_token)

#     # new_private_key, new_address = generate_algorand_keypair()
#     address1 = "3MEL3EIAHOZCC7DO5MLH76WXCGQUN72ZPNMAB4TTMM2BL3J7O77QCZD4ZM" # Status: Code 200 OK: "JS6HWSRLD2J4WYW7AD3IOU5XFZ2JOFQ47HTFQNMKHVMVPM4AOYMQ" 
#     passphrase1 = "question manual hold shield point fashion trigger dress retire used salmon noble bonus lawn canyon humor thought absorb fancy escape oxygen egg zoo about cable"
#     address2 = "MLF742JMWBY56MKJXUJFQPKA64QXZIDNLG2RO5S4YZV5JRPRQFFEVANLLA"
#     passphrase2 = "truck patient scrap crowd install tennis patch drama talk common sample all present capable typical employ sausage special joke document chicken cart improve about area"
#     # private_key = mnemonic.to_private_key(passphrase1)
#     # my_address = mnemonic.to_public_key(passphrase1)
    
#     print("# Pre txn: ")
#     printAccountInfo(algod_client, address1)
#     printAccountInfo(algod_client, address2)

#     myindexer = configIndexer()

#     # testTransaction(algod_client, address1, passphrase1, address2, 700000, "Test Numero 1!!")
    
#     # using Indexer to query the Note field
#     # notePrefix = ""
#     # response = myindexer.search_transactions(address=address2)
#     # print("note-prefix = " + json.dumps(response, indent=2, sort_keys=True))
#     # # print first note that matches
#     # if (len(response["transactions"]) > 0):
#     #     print("Decoded note: {}".format(base64.b64decode(response["transactions"][0]["note"]).decode()))

#     # print("# Post txn: ")
#     # printAccountInfo(algod_client, address1)
#     # printAccountInfo(algod_client, address2)

#     response = myindexer.search_transactions(address=address2)
#     print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

# main()