#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import bzx_apy
from chain.bsc import w3

fulcrum_vault = {
    'iBNB': '0x49646513609085f39D9e44b413c74530Ba6E2c0F',
    'iUSDT': '0xf326b42A237086F1De4E7D68F2d2456fC787bc01',
    'iETH': '0x949cc03E43C24A954BAa963A00bfC5ab146c6CE7',
    'iBTC': '0x97eBF27d40D306aD00bb2922E02c58264b295a95',
    'iBUSD': '0x7343b25c4953f4C57ED4D16c33cbEDEFAE9E8Eb9',
    'iLINK': '0xacD39C8d46461bCa7D5Fb23eCD57A4CB0D31fAB5',
    'iBZRX': '0xA726F2a7B200b03beB41d1713e6158e0bdA8731F',
}

fulcrum_stake_pool = {
    'iBNB': 0,
    'iBUSD': 1,
    'iETH': 2,
    'iUSDT': 3,
    'iBTC': 4,
    'iBZRX': 5,
    'WBNB-BGOV-V1': 6,
    'BGOV': 7,
    'iLINK': 8,
    'WBNB-BGOV-V2': 9,
}

class BZX(object):
    BGOV = '0xf8E026dC4C0860771f691EcFFBbdfe2fa51c77CF'

    def __init__(self, master_abi, vault_abi):
        self.vaults = {}
        for token_name, address in fulcrum_vault.items():
            self.vaults[token_name] = w3.eth.contract(abi=vault_abi, address=address)
        self.master = w3.eth.contract(abi=master_abi, address='0x1FDCA2422668B961E162A8849dc0C2feaDb58915')
        self.farm_info = None

    @property
    def type(self):
        return 'Lending'

    @property
    def name(self):
        return 'bZx'

    def token_address(self):
        return self.BGOV

    @staticmethod
    def token_name():
        return 'BGOV'
    
    @staticmethod
    def token_slug_name():
        return ''

    @staticmethod
    def pool_name(original_token_name):
        return 'i' + original_token_name

    # return shares, asset and apy
    def lend(self, user, pool_name, block_number='latest', optimizer=None):
        if optimizer is None:
            pid = fulcrum_stake_pool[pool_name]
            shares = self.vaults[pool_name].functions.balanceOf(user).call(block_identifier=block_number)
            shares += self.master.functions.userInfo(pid, user).call(block_identifier=block_number)[0]
        else:
            _, shares = optimizer.staked(user, pool_name, block_number)
        token_price = self.vaults[pool_name].functions.tokenPrice().call(block_identifier=block_number)
        return shares, shares * token_price // 10 ** 18

    def borrow(self, user, pool_name, block_number='latest'):
        pass

    def interest_rate(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        pool_addr = fulcrum_vault[pool_name]
        return self.farm_info[pool_addr]['aprLending']

    def reward(self, user, pool_name, block_number='latest'):
        pid = fulcrum_stake_pool[pool_name]
        amount = self.master.functions.pendingBGOV(pid, user).call(block_identifier=block_number)
        return { 'BGOV': amount / 10 ** 18 }

    def apy(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        pool_addr = fulcrum_vault[pool_name]
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
        
        title_str = " [link=https://bsc.fulcrum.trade/lend][bold blue]bZx[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]${:.0f}[/]".format(usd_total, usd_delta)
        console.print(title_str, style='italic')
        console.print(supply_table)
        if borrow:
            console.print(borrow_table)