from web3 import Web3

w3 = Web3(Web3.HTTPProvider(
'https://ropsten.infura.io/v3/7e2dfeac05f54977aa26e267adff9145'))
account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address

print(f"Your address: {address}\nYour key: {privateKey}")
