#!/usr/bin/env python3

import urllib.request
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
}

def token_prices(token_slug_names):
    coin_cmc_price = {}

    flux_statistics_url = 'https://bsc.flux.01defi.com/api/v1/flux/get_trade_statistics_info'
    f = urllib.request.urlopen(flux_statistics_url)
    flux_statistics = json.loads(f.read().decode('utf-8'))
    coin_cmc_price['FLUX'] = float(flux_statistics['data']['fluxPrice'])

    cmc_base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    cmc_slug = []
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