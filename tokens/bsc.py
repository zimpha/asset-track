#!/usr/bin/env python3

import json
import os
import requests

from chain.bsc import w3

token_dict = {
    'FLUX': '0x0747CDA49C82d3fc6B06dF1822E1DE0c16673e9F',
    'DAI': '0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3',
    'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    'ETH': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
    'USDT': '0x55d398326f99059fF775485246999027B3197955',
    'BUSD': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
    'BTC': '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
    'BAKE': '0xE02dF9e3e622DeBdD69fb838bB799E3F168902c5',
    'CAKE': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
    'AUTO': '0xa184088a740c695E156F91f5cC086a06bb78b827',
    'BIRD': '0x7f1296e5aA692a98d86EaAe3ac1CD7723E74878d',
    'lowb': '0x843D4a358471547f51534e3e51fae91cb4Dc3F28',
    'CFX': '0x045c4324039dA91c52C55DF5D785385Aab073DcF',
    'AUTO': '0xa184088a740c695E156F91f5cC086a06bb78b827',
    'BELT': '0xE0e514c71282b6f4e823703a39374Cf58dc3eA4f',
    'BUNNY': '0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51',
    'BGOV': '0xf8E026dC4C0860771f691EcFFBbdfe2fa51c77CF',
    'XVS': '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63',
    'ALPACA': '0x8F0528cE5eF7B51152A59745bEfDD91D97091d2F',
}

token_name_mapping = {
    'BTCB': 'BTC',
    'bcFLUX': 'FLUX',
    'bCFX': 'CFX',
    'cFLUX': 'FLUX',
}

custom_token_list = ['FLUX', 'BIRD', 'lowb', 'CFX', 'BGOV']

_abi_dir = '/'.join(os.path.dirname(__file__).split('/')[:-1])

bep20_abi = json.load(open(_abi_dir + '/abi/BEP20.json'))

def wallet_token_balance(account, block_number='latest'):
    # use debank api first
    try:
        balance_list = requests.get('https://api.debank.com/token/balance_list?user_addr=' + account).json()['data']
        possible_token_list = [x['symbol'] for x in balance_list] + custom_token_list
    except Exception as e:
        possible_token_list = token_dict.keys()
    token_balance = {}
    token_balance['BNB'] = w3.eth.get_balance(account) / 10 ** 18
    for token in possible_token_list:
        if token == 'BNB':
            continue
        token_name = token_name_mapping.get(token, token)
        if token_name not in token_dict:
            continue
        address = token_dict[token_name]
        token_contract = w3.eth.contract(abi=bep20_abi, address=address)
        balance = token_contract.functions.balanceOf(account).call(block_identifier=block_number)
        if balance > 0:
            token_balance[token_name] = balance / 10 ** 18
    return token_balance
