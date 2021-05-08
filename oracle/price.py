#!/usr/bin/env python3

import requests
import json

cmc_slug_map = {
    'BNB': 'binance-coin',
    'BTC': 'bitcoin',
    'CFX': 'conflux-network',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'BUSD': 'binance-usd',
    'DAI': 'multi-collateral-dai',
    'CAKE': 'pancakeswap',
    'BAKE': 'bakerytoken',
    'WBNB': 'wbnb',
}

def token_prices(token_slug_names):
    coin_cmc_price = {}

    # FLUX Price
    response = requests.get('https://bsc.flux.01defi.com/api/v1/flux/get_trade_statistics_info').json()
    coin_cmc_price['FLUX'] = float(response['data']['fluxPrice'])
    
    # price from pancake
    response = requests.get('https://api.pancakeswap.info/api/v2/tokens').json()
    for _, token_info in response['data'].items():
        symbol = token_info['symbol']
        coin_cmc_price[symbol] = float(token_info['price'])

    cmc_base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    cmc_slug = list(cmc_slug_map.values())
    for slug in token_slug_names:
        if slug == '':
            continue
        cmc_slug.append(slug)
    response = requests.get(
        cmc_base_url,
        params={
            'slug': ','.join(cmc_slug),
            'aux': '',
        },
        headers={
            'X-CMC_PRO_API_KEY': '5286b571-d5f7-4acb-8f68-099602517984',
            'Accept': 'application/json',
        },
    )
    cmc_data = response.json()['data']
    for id in cmc_data:
        symbol = cmc_data[id]['symbol']
        price = cmc_data[id]['quote']['USD']['price']
        coin_cmc_price[symbol] = price
    return coin_cmc_price