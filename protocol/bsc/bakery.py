#!/usr/bin/env python3

from rich.table import Table

from chain.bsc import w3
from protocol import YieldFarmingBase

pool_address = {
    'BAKE': '0xE02dF9e3e622DeBdD69fb838bB799E3F168902c5',
}

base_reward_token = {
    'BAKE': 'BAKE'
}


class Bakery(YieldFarmingBase):
    BAKE = '0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51'

    def __init__(self, master_abi):
        self.master = w3.eth.contract(
            abi=master_abi, address='0x20eC291bB8459b6145317E7126532CE7EcE5056f')

    @property
    def name(self):
        return 'Bakery'

    @staticmethod
    def token_name():
        return 'BAKE'

    @staticmethod
    def token_slug_name():
        return 'bakerytoken'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return original_token_name

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        pool = pool_address[pool_name]
        amount, _ = self.master.functions.poolUserInfoMap(
            pool, user).call(block_identifier=block_number)
        return amount, amount

    def reward(self, user, pool_name, block_number='latest'):
        pool = pool_address[pool_name]
        amount = self.master.functions.pendingBake(
            pool, user).call(block_identifier=block_number)
        return {
            'BAKE': amount / 10 ** 18
        }

    def apy(self, pool_name):
        return 0

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://www.bakeryswap.org][bold blue]Bakery Swap[/][/link] on BSC"
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
