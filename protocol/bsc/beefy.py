#!/usr/bin/env python3

from rich.table import Table

from chain.bsc import w3
from oracle.apy import beefy_apy

beefy_vault = {
    'beltBTC': '0xD411121C948Cff739857513E1ADF25ED448623f8',
    'beltETH': '0xf2064C230b285AA6Cf45c6267DA86a8E3505D0AA',
    'beltBNB': '0xC34Ae91312A3c3F9420691922040a5DEe1698E52',
    '4Belt': '0xc1fcf50ccaCd1583BD9d3b41657056878C94e592',
    'BAKE': '0xaC112E7744C129ae54E65F5D2cb4eA472E08eA0B',
}

beefy_id_map = {
    'beltBTC': 'belt-beltbtc',
    'beltETH': 'belt-belteth',
    'beltBNB': 'belt-beltbnb',
    '4Belt': 'belt-4belt',
    'BAKE': 'bakery-bake',
}


class Beefy(object):
    BIFI = '0xCa3F508B8e4Dd382eE878A314789373D80A5190A'

    def __init__(self, vault_abi):
        self.vaults = {}
        for token_name, address in beefy_vault.items():
            self.vaults[token_name] = w3.eth.contract(
                abi=vault_abi, address=address)
        self.farm_info = None

    @property
    def type(self):
        return 'Farming'

    @property
    def name(self):
        return 'Beefy'

    def token_address(self):
        return self.BIFI

    @staticmethod
    def token_name():
        return 'BIFI'

    @staticmethod
    def token_slug_name():
        return 'beefy-finance'

    @staticmethod
    def pool_name(original_token_name):
        return original_token_name

    def shares(self, user, pool_name, block_number='latest'):
        return self.vaults[pool_name].functions.balanceOf(user).call(block_identifier=block_number)

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        shares = self.shares(user, pool_name, block_number)
        price = self.vaults[pool_name].functions.getPricePerFullShare().call(
            block_identifier=block_number)
        return shares, shares * price // 10 ** 18

    def reward(self, user, pool_name, block_number='latest'):
        return { 'BIFI': 0 }

    def apy(self, pool_name):
        self._get_farm_info()
        if pool_name not in beefy_id_map:
            return 0
        id = beefy_id_map[pool_name]
        if id not in self.farm_info:
            return 0
        return self.farm_info[id] * 100

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = beefy_apy()

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://app.beefy.finance/][bold blue]Beefy[/][/link] on BSC"
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
        table.add_column('Farm APY', justify='right')
        table.add_column('USD Value', justify='right')
        for pool in pools:
            table.add_row(
                pool['name'],
                pool['shares'],
                pool['assets'],
                pool['farm_apy'],
                pool['usd'])
        console.print(table)