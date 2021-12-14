from web3 import Web3


def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider(
        'https://ropsten.infura.io/v3/7e2dfeac05f54977aa26e267adff9145'))
    address = '0xd4B9539C3bBc23FEf71F38562Ae36E0374a4B691'
    privateKey = '0x3180fb7d4ac7b6a6cab8406cc8b24e27b62a0cbf420851f0c8d18ea2fd752b1d'
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=message.encode('utf-8'),
    ), privateKey)

    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId
