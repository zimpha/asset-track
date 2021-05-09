#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import autofarm_apy
from chain.bsc import w3
from protocol import YieldFarmingBase

pool_index = {
    'lowb': 0,
}


class Loserswap(YieldFarmingBase):
    lowb = '0x843D4a358471547f51534e3e51fae91cb4Dc3F28'

    def __init__(self, master_abi):
        self.master = w3.eth.contract(
            abi=master_abi, address='0x4b6080917a8333D5DB16345642D9899e9A870d9f')

    @property
    def name(self):
        return 'Loserswap'

    @staticmethod
    def token_name():
        return 'lowb'

    @staticmethod
    def token_slug_name():
        return ''

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return original_token_name

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        pid = pool_index[pool_name]
        amount = self.master.functions.userInfo(
            pid, user).call(block_identifier=block_number)[0]
        return amount, amount

    def reward(self, user, pool_name, block_number='latest'):
        pid = pool_index[pool_name]
        return {
            'lowb': self.master.functions.pendingCake(pid, user).call(block_identifier=block_number) / 10 ** 18
        }

    def apy(self, pool_name):
        return 0

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://app.loserswap.com/][bold blue]LoserSwap[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(
                usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]-${:.0f}[/]".format(
                usd_total, -usd_delta)
        console.print(title_str, style='italic')
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        table.add_column('Pool')
        table.add_column('Shares', justify='center')
        table.add_column('Assets', justify='center')
        table.add_column('Rewards', justify='right')
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
