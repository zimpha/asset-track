#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import bzx_apy
from chain.bsc import w3
from protocol import LendingBase

alpaca_vault = {
    # address, pool_id
    'ibALPACA': ('0xf1bE8ecC990cBcb90e166b71E368299f0116d421', 11),
    'ibBNB': ('0xd7D069493685A581d27824Fc46EdA46B7EfC0063', 1),
    'ibBUSD': ('0x7C9e73d4C71dae564d41F78d56439bB4ba87592f', 3),
    'ibETH': ('0xbfF4a34A4644a113E8200D7F1D79b3555f723AfE', 9),
}

class Alpaca(LendingBase):
    ALPACA = '0x8F0528cE5eF7B51152A59745bEfDD91D97091d2F'

    def __init__(self, fair_launch_abi, vault_abi):
        self.vaults = {}
        for token_name, (address, _) in alpaca_vault.items():
            self.vaults[token_name] = w3.eth.contract(
                abi=vault_abi, address=address)
        self.fair_launch = w3.eth.contract(
            abi=fair_launch_abi, address='0xA625AB01B08ce023B2a342Dbb12a16f2C8489A8F')
        self.farm_info = None

    @property
    def name(self):
        return 'Alpaca'

    @staticmethod
    def token_name():
        return 'ALPACA'

    @staticmethod
    def token_slug_name():
        return 'alpaca-finance'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return 'ib' + original_token_name

    # return shares, asset and apy
    def supply(self, user, pool_name, block_number='latest', optimizer=None):
        if optimizer is None:
            _, pid = alpaca_vault[pool_name]
            shares = self.vaults[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
            shares += self.fair_launch.functions.userInfo(
                pid, user).call(block_identifier=block_number)[0]
        else:
            _, shares = optimizer.staked(user, pool_name, block_number)
        amount = shares * self.vaults[pool_name].functions.totalToken().call(block_identifier=block_number) / self.vaults[pool_name].functions.totalSupply().call(block_identifier=block_number)
        return shares, amount

    def supply_interest_rate(self, user, pool_name, block_number='latest'):
        return 0
        self._get_farm_info()
        pool_addr, _ = alpaca_vault[pool_name]
        return self.farm_info[pool_addr]['aprLending']

    def supply_reward(self, user, pool_name, block_number='latest'):
        _, pid = alpaca_vault[pool_name]
        amount = self.fair_launch.functions.pendingAlpaca(
            pid, user).call(block_identifier=block_number)
        return { 'ALPACA': amount / 10 ** 18 }

    def supply_apy(self, user, pool_name, block_number='latest'):
        return 0
        self._get_farm_info()
        pool_addr, _ = alpaca_vault[pool_name]
        return self.farm_info[pool_addr]['aprCombined']

    def supply_value(self, user, block_number='latest'):
        return 0

    def borrow_value(self, user, block_number='latest'):
        return 0

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = bzx_apy('bsc')

    def print_pools(self, console, supply_value, borrow_value, pools, usd_total, usd_delta):
        supply_table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        supply_table.add_column('Supplied')
        supply_table.add_column('Balance', justify='center')
        supply_table.add_column('Rewards', justify='right')
        supply_table.add_column('Interest Rate', justify='right')
        supply_table.add_column('Farm APY', justify='right')
        supply_table.add_column('USD Value', justify='right')
        borrow_table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        borrow_table.add_column('Borrowed')
        borrow_table.add_column('Balance', justify='center')
        borrow_table.add_column('Rewards', justify='right')
        borrow_table.add_column('Interest Rate', justify='right')
        borrow_table.add_column('Farm APY', justify='right')
        borrow_table.add_column('USD Value', justify='right')
        supply, borrow = 0, 0
        for pool in pools:
            if pool['type'] == 'lend':
                supply += 1
                supply_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['rewards'],
                    pool['interest_rate'],
                    pool['farm_apy'],
                    pool['usd'])
            else:
                borrow += 1
                borrow_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['rewards'],
                    pool['interest_rate'],
                    pool['farm_apy'],
                    pool['usd'])

        title_str = " [link=https://app.alpacafinance.org/lend][bold blue]Alpaca[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(
                usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]-${:.0f}[/]".format(
                usd_total, -usd_delta)
        console.print(title_str, style='italic')
        console.print(supply_table)
        if borrow:
            console.print(borrow_table)
