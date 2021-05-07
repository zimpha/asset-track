from web3 import Web3

provider = Web3.HTTPProvider('https://bsc-dataseed.binance.org/')
chainid = 56
w3 = Web3(provider)