#!/usr/bin/env python3

import requests
import json


def autofarm_apy():
    apy_url = 'https://static.autofarm.network/bsc/farm_data.json'
    response = requests.get(apy_url)
    farm_data = response.json()
    apy_info = {}
    for pid, pool_info in farm_data['pools'].items():
        apy_info[int(pid)] = {
            'APR': pool_info['APR'],
            'APY': pool_info['APY'],
            'APR_AUTO': pool_info['APR_AUTO'],
            'APY_total': pool_info['APY_total'],
        }
    return apy_info


def beefy_apy():
    apy_url = 'https://api.beefy.finance/apy'
    response = requests.get(apy_url)
    return response.json()


def belt_apy():
    apy_url = 'https://s.belt.fi/status/A_getMainInfo.json'
    pool_info = requests.get(apy_url).json()
    apy_info = {}
    for info in pool_info['vaultPools']:
        if 'name' not in info:
            continue
        name = info['name']
        apy_info[name] = {
            'baseAPR': info['baseAPR'],
            'feeAPR': info['feeAPR'],
            'rewardAPR': info['rewardAPR'],
            'totalAPR': info['totalAPR'],
        }
    for info in pool_info['vaults']:
        if 'name' not in info:
            continue
        name = info['name']
        if name not in apy_info:
            apy_info[name] = {
                'baseAPR': info['baseAPR'],
                'feeAPR': "0",
                'rewardAPR': info['rewardAPR'],
                'totalAPR': info['totalAPR'],
            }
    return apy_info


def bunny_apy():
    apy_url = 'https://firestore.googleapis.com/v1/projects/pancakebunny-finance/databases/(default)/documents/apy_data?pageSize=100'
    pool_info = requests.get(apy_url).json()
    apy_info = {}
    for pools in pool_info['documents']:
        pool_addr = pools['fields']['pool']['stringValue']
        apy = pools['fields']['apyPool']['stringValue']
        apy_info[pool_addr] = float(apy)
    return apy_info


def bzx_apy(networks):
    apy_url = 'https://api.bzx.network/v1/farming-pools-info?networks={}'.format(
        networks)
    pool_info = requests.get(apy_url).json()['data']
    apy_info = {}
    for pools in pool_info['bsc']['pools']:
        pool_addr = pools['lpToken']
        apy_info[pool_addr] = {
            'aprCombined': float(pools['aprCombined']),
            'aprLending': float(pools['aprLending'])
        }
    return apy_info


def venus_apy():
    apy_url = 'https://api.venus.io/api/governance/venus'
    pool_info = requests.get(apy_url).json()['data']
    apy_info = {}
    for market in pool_info['markets']:
        symbol = market['symbol']
        apy_info[symbol] = {
            'borrow_interest_rate': float(market['borrowApy']),
            'supply_interest_rate': float(market['supplyApy']),
            'borrow_apy': float(market['borrowVenusApy']) - float(market['borrowApy']),
            'supply_apy': float(market['supplyApy']) + float(market['supplyVenusApy']),
            'exchange_rate': int(market['exchangeRate'])
        }
    return apy_info