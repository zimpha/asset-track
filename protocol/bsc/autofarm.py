#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import autofarm_apy
from chain.bsc import w3
from protocol import YieldFarmingBase

pool_index = {
    'beltBNB': 338,
    'beltBTC': 339,
    'beltETH': 340,
    '4Belt': 341,
    'iBNB': 137,
    'iBUSD': 138,
    'iUSDT': 139,
    'iBTC': 140,
    'iETH': 141,
    'iLINK': 142,
    'BANANA': 348,
    'BGOV': 357,
    'KEBAB': 39,
    'CAKE': 7,
}


class Autofarm(YieldFarmingBase):
    AUTOv2 = '0xa184088a740c695E156F91f5cC086a06bb78b827'

    def __init__(self, abi):
        self.contract = w3.eth.contract(
            abi=abi, address='0x0895196562C7868C5Be92459FaE7f877ED450452')
        self.farm_info = None

    @property
    def name(self):
        return 'AutoFarm'

    @staticmethod
    def token_name():
        return 'AUTO'

    @staticmethod
    def token_slug_name():
        return 'auto'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return original_token_name

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        pid = pool_index[pool_name]
        amount = self.contract.functions.stakedWantTokens(
            pid, user).call(block_identifier=block_number)
        return amount, amount

    def user_info(self, user, pool_name, block_number='latest'):
        pid = pool_index[pool_name]
        return self.contract.functions.userInfo(pid, user).call(block_identifier=block_number)

    def reward(self, user, pool_name, block_number='latest'):
        pid = pool_index[pool_name]
        return {
            'AUTO': self.contract.functions.pendingAUTO(pid, user).call(block_identifier=block_number) / 10 ** 18
        }

    def apy(self, pool_name):
        self._get_farm_info()
        if pool_name not in pool_index:
            return 0
        pid = pool_index[pool_name]
        if pid not in self.farm_info:
            return 0
        return self.farm_info[pid]['APY_total'] * 100

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = autofarm_apy()

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://autofarm.network/][bold blue]Autofarm[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(
                usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]${:.0f}[/]".format(
                usd_total, usd_delta)
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
