#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import bunny_apy
from chain.bsc import w3
from protocol import YieldFarmingBase

pool_address = {
    'CAKE': '0xEDfcB78e73f7bA6aD2D829bf5D462a0924da28eD',
    'USDT': '0x0Ba950F0f099229828c10a9B307280a450133FFc',
    'BTC': '0x549d2e2B4fA19179CA5020A981600571C2954F6a',
    'BUSD': '0x0243A20B20ECa78ddEDF6b8ddb43a0286438A67A',
    'BNB': '0x52cFa188A1468A521A98eaa798E715Fbb9eb38a3',
}

base_reward_token = {
    'CAKE': 'CAKE',
    'USDT': 'USDT',
    'BTC': 'BTC',
    'BUSD': 'BUSD',
    'BNB': 'BNB'
}


class Bunny(YieldFarmingBase):
    BUNNY = '0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51'

    def __init__(self, dashboard_abi):
        self.dashboard = w3.eth.contract(
            abi=dashboard_abi, address='0xb3C96d3C3d643c2318E4CDD0a9A48aF53131F5f4')
        self.farm_info = None
        self.pool_cache = {}

    @property
    def name(self):
        return 'PancakeBunny'

    @staticmethod
    def token_name():
        return 'BUNNY'

    @staticmethod
    def token_slug_name():
        return 'pancakebunny'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return original_token_name

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        pool_info = self._get_pool_info(user, pool_name, block_number)
        return pool_info['deposit'], pool_info['deposit']

    def reward(self, user, pool_name, block_number='latest'):
        pool_info = self._get_pool_info(user, pool_name, block_number)
        base = pool_info['base_reward']
        bunny = pool_info['bunny_reward']
        if base_reward_token[pool_name] == 'BUNNY':
            return { 'BUNNY': base }
        else:
            return {
                base_reward_token[pool_name]: base,
                'BUNNY': bunny,
            }

    def apy(self, pool_name):
        self._get_farm_info()
        if pool_name not in pool_address:
            return 0
        pool_addr = pool_address[pool_name]
        if pool_addr not in self.farm_info:
            return 0
        return self.farm_info[pool_addr]
    
    def _get_pool_info(self, user, pool_name, block_number):
        if user in self.pool_cache and pool_name in self.pool_cache[user]:
            return self.pool_cache[user][pool_name]
        pool = pool_address[pool_name]
        _, balance, deposit, _, _, _, _, base, bunny, _, _, _ = self.dashboard.functions.infoOfPool(pool, user).call(block_identifier=block_number)
        self.pool_cache.setdefault(user, {})
        self.pool_cache[user][pool_name] = {
            'balance': balance,
            'deposit': deposit,
            'base_reward': base / 10 ** 18,
            'bunny_reward': bunny / 10 ** 18,
        }
        return self.pool_cache[user][pool_name]

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = bunny_apy()

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://pancakebunny.finance/][bold blue]Pancake Bunny[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]${:.0f}[/]".format(usd_total, usd_delta)
        console.print(title_str, style='italic')
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        table.add_column('Pool')
        table.add_column('Shares', justify='center')
        table.add_column('Assets', justify='center')
        table.add_column('Rewards', justify='center')
        table.add_column('Farm APY', justify='right')
        table.add_column('USD Value', justify='right')
        for pool in pools:
            table.add_row(
                pool['name'],
                pool['shares'],
                pool['assets'],
                pool['rewards'],
                pool['farm_apy'],
                pool['usd'])
        console.print(table)
