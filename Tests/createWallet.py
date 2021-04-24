from algosdk import kmd, mnemonic
from algosdk.wallet import Wallet

kmd_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
kmd_address = "http://localhost:4002" # "[::]:4002"
# create a kmd client
kcl = kmd.KMDClient(kmd_token, kmd_address)

def createWallet(name, password):
    # create a wallet object
    wallet = Wallet(name, password, kcl)

    # get wallet information
    info = wallet.info()
    print("Wallet name:", info["wallet"]["name"])

    # create an account
    address = wallet.generate_key()
    print("New account:", address)

createWallet("AmazonWallet", "AmazonPW1")