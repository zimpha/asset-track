#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import autofarm_apy
from chain.bsc import w3
from protocol import YieldFarmingBase

coinwind_vault = {
    'MDX': ('0x9C65AB58d8d978DB963e63f2bfB7121627e3a739', 0),
}


class CoinWind(YieldFarmingBase):
    MDX = '0x9C65AB58d8d978DB963e63f2bfB7121627e3a739'

    def __init__(self, abi):
        self.contract = w3.eth.contract(
            abi=abi, address='0x6bA7d75eC6576F88a10bE832C56F0F27DC040dDD')
        self.farm_info = None

    @property
    def name(self):
        return 'CoinWind'

    @staticmethod
    def token_name():
        return 'MDX'

    @staticmethod
    def token_slug_name():
        return 'mdex'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return original_token_name

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        addr, _ = coinwind_vault[pool_name]
        amount = self.contract.functions.getDepositAsset(
            addr, user).call(block_identifier=block_number)
        return amount, amount

    def reward(self, user, pool_name, block_number='latest'):
        addr, _ = coinwind_vault[pool_name]
        return {
            'MDX': self.contract.functions.earned(addr, user).call(block_identifier=block_number) / 10 ** 18
        }

    def apy(self, pool_name):
        addr, _ = coinwind_vault[pool_name]
        apy = self.contract.functions.getApy(addr).call()
        return apy / 100

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://www.coinwind.com/][bold blue]CoinWind[/][/link] on BSC"
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
