#!/usr/bin/env python3

from rich.table import Table

from oracle.apy import belt_apy
from chain.bsc import w3
from protocol import YieldFarmingBase

belt_vaults = {
    'beltBTC': '0x51bd63F240fB13870550423D208452cA87c44444',
    'beltETH': '0xAA20E8Cb61299df2357561C2AC2e1172bC68bc25',
    'beltBNB': '0xa8Bb71facdd46445644C277F9499Dd22f6F0A30C',
    'beltDAI': '0x9A86fc508a423AE8a243445dBA7eD5364118AB1D',
    'beltUSDT': '0x55E1B1e49B969C018F2722445Cd2dD9818dDCC25',
    'beltUSDC': '0x7a59bf07D529A5FdBab67D597d63d7D5a83E61E5',
    'beltBUSD': '0x9171Bf7c050aC8B4cf7835e51F7b4841DFB2cCD0',
    '4Belt': '0x9cb73F20164e399958261c289Eb5F9846f4D1404',
}

belt_stake_pool = {
    '4Belt': 3,
    'beltBTC': 7,
    'beltETH': 8,
    'beltBNB': 9,
}


class Belt(YieldFarmingBase):
    BELT = '0xE0e514c71282b6f4e823703a39374Cf58dc3eA4f'
    BeltLPToken = '0x9cb73F20164e399958261c289Eb5F9846f4D1404'  # 4Belt
    StableSwapB = '0xAEA4f7dcd172997947809CE6F12018a6D5c1E8b6'
    DepositB = '0xF6e65B33370Ee6A49eB0dbCaA9f43839C1AC04d5'
    MasterBelt = '0xD4BbC80b9B102b77B21A06cb77E954049605E6c1'

    def __init__(self, vault_abi, swap_abi, master_abi):
        self.vaults = {}
        for token_name, address in belt_vaults.items():
            self.vaults[token_name] = w3.eth.contract(
                abi=vault_abi, address=address)
        self.stable_swap = w3.eth.contract(
            abi=swap_abi, address=self.StableSwapB)
        self.master_belt = w3.eth.contract(
            abi=master_abi, address=self.MasterBelt)
        self.farm_info = None

    @property
    def name(self):
        return 'Belt.fi'

    @staticmethod
    def token_name():
        return 'BELT'

    @staticmethod
    def token_slug_name():
        return 'belt'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        if original_token_name in ['USDT', 'DAI', 'BUSD', 'USDC', 'USD']:
            return '4Belt'
        return 'belt' + original_token_name

    def staked_all(self, user, block_number='latest'):
        pass

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        if pool_name == '4Belt':
            return self._usd_staked(user, block_number, optimizer)
        if optimizer is None:
            shares = self.vaults[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
            if pool_name in belt_stake_pool:
                pid = belt_stake_pool[pool_name]
                shares += self.master_belt.functions.stakedWantTokens(
                    pid, user).call(block_identifier=block_number)
        else:
            _, shares = optimizer.staked(user, pool_name, block_number)
        if shares > 0:
            return shares, self.vaults[pool_name].functions.sharesToAmount(shares).call(block_identifier=block_number)
        else:
            return shares, 0

    def _usd_staked(self, user, block_number='latest', optimizer=None):
        pool_name = '4Belt'
        if optimizer is None:
            shares = self.vaults[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
            pid = belt_stake_pool[pool_name]
            shares += self.master_belt.functions.stakedWantTokens(
                pid, user).call(block_identifier=block_number)
        else:
            _, shares = optimizer.staked(
                user, pool_name, block_number=block_number)
        if shares > 0:
            token_price = self.stable_swap.functions.get_virtual_price().call(
                block_identifier=block_number)
            return shares, token_price * shares // 10 ** 18
        else:
            return 0, 0

    def reward(self, user, pool_name, block_number='latest'):
        pid = belt_stake_pool[pool_name]
        return {'BELT': self.master_belt.functions.pendingBELT(pid, user).call(block_identifier=block_number) / 10 ** 18}

    def _usd_reward(self, user, block_number='latest'):
        return {'BELT': 0}

    def apy(self, pool_name):
        self._get_farm_info()
        if pool_name not in self.farm_info:
            return 0
        return float(self.farm_info[pool_name]['totalAPR'])

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = belt_apy()

    def print_pools(self, console, pools, usd_total, usd_delta):
        title_str = " [link=https://belt.fi/][bold blue]Belt.fi[/][/link] on BSC"
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
