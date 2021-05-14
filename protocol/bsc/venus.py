#!/usr/bin/env python3

from rich.table import Table
from web3.contract import get_abi_output_types

from oracle.apy import venus_apy
from chain.bsc import w3
from protocol import LendingBase

venus_vault = {
    'vSXP': '0x2fF3d0F6990a40261c66E1ff2017aCBc282EB6d0',
    'vXVS': '0x151B1e2635A717bcDc836ECd6FbB62B674FE3E1D',
    'vUSDC': '0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8',
    'vUSDT': '0xfD5840Cd36d94D7229439859C0112a4185BC0255',
    'vBUSD': '0x95c78222B3D6e262426483D42CfA53685A67Ab9D',
    'vBNB': '0xA07c5b74C9B40447a954e1466938b865b6BBea36',
    'vBTC': '0x882C173bC7Ff3b7786CA16dfeD3DFFfb9Ee7847B',
    'vETH': '0xf508fCD89b8bd15579dc79A6827cB4686A3592c8',
    'vLTC': '0x57A5297F2cB2c0AaC9D554660acd6D385Ab50c6B',
    'vXRP': '0xB248a295732e0225acd3337607cc01068e3b9c10',
    'vBCH': '0x5F0388EBc2B94FA8E123F404b79cCF5f40b29176',
    'vDOT': '0x1610bc33319e9398de5f57B33a5b184c806aD217',
    'vLINK': '0x650b940a1033B8A1b1873f78730FcFC73ec11f1f',
    'vDAI': '0x334b3eCB4DCa3593BCCC3c7EBD1A1C1d1780FBF1',
    'vFIL': '0xf91d58b5aE142DAcC749f58A49FCBac340Cb0343',
    'vBETH': '0x972207A639CC1B374B893cc33Fa251b55CEB7c07',
    'vADA': '0x9A0AF7FDb2065Ce470D72664DE73cAE409dA28Ec',
    'vDOGE': '0xec3422Ef92B2fb59e84c8B02Ba73F1fE84Ed8D71',
}


class Venus(LendingBase):
    XVS = '0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63'

    def __init__(self, multicall, xvs_abi, controller_abi, vault_abi):
        self.vaults = {}
        for token_name, address in venus_vault.items():
            self.vaults[token_name] = w3.eth.contract(
                abi=vault_abi, address=address)
        self.controller = w3.eth.contract(
            abi=controller_abi, address='0xfD36E2c2a6789Db23113685031d7F16329158384')
        self.multicall = multicall
        self.xvs = w3.eth.contract(abi=xvs_abi, address=self.XVS)
        self.farm_info = None

    @property
    def name(self):
        return 'Venus'

    @staticmethod
    def token_name():
        return 'XVS'

    @staticmethod
    def token_slug_name():
        return 'venus'

    @property
    def share_decimals(self):
        return 8

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return 'v' + original_token_name

    # return shares, asset and apy
    def supply(self, user, pool_name, block_number='latest', optimizer=None):
        if optimizer is None:
            pool_addr = venus_vault[pool_name]
            shares = self.vaults[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
        else:
            _, shares = optimizer.staked(user, pool_name, block_number)
        token_price = self.vaults[pool_name].functions.exchangeRateCurrent().call(
            block_identifier=block_number)
        return shares, shares * token_price // 10 ** 18

    def borrow(self, user, pool_name, block_number='latest'):
        pool_addr = venus_vault[pool_name]
        return self.vaults[pool_name].functions.borrowBalanceCurrent(user).call(block_identifier=block_number)

    def borrow_interest_rate(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        return self.farm_info[pool_name]['borrow_interest_rate']

    def supply_interest_rate(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        return self.farm_info[pool_name]['supply_interest_rate']

    def reward(self, user, pool_name, block_number='latest'):
        market = venus_vault[pool_name]
        return {'XVS': self._get_reward(user, [market], True, True, block_number) / 10 ** 18}

    def supply_reward(self, user, pool_name, block_number='latest'):
        market = venus_vault[pool_name]
        return {'XVS': self._get_reward(user, [market], False, True, block_number) / 10 ** 18}

    def borrow_reward(self, user, pool_name, block_number='latest'):
        market = venus_vault[pool_name]
        return {'XVS': self._get_reward(user, [market], True, False, block_number) / 10 ** 18}

    def borrow_apy(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        return self.farm_info[pool_name]['borrow_apy']

    def supply_apy(self, user, pool_name, block_number='latest'):
        self._get_farm_info()
        return self.farm_info[pool_name]['supply_apy']

    def supply_value(self, user, block_number='latest'):
        return 0

    def borrow_value(self, user, block_number='latest'):
        return 0

    def _get_farm_info(self):
        if self.farm_info is not None:
            return
        self.farm_info = venus_apy()

    def _get_reward(self, user, markets, borrow, supply, block_number='latest'):
        xvs_balance = self.xvs.functions.balanceOf(user)
        claim_venus = self.controller.functions.claimVenus(
            [user],
            markets,
            borrow,
            supply)
        xvs_balance_data = xvs_balance._encode_transaction_data()
        claim_venus_data = claim_venus._encode_transaction_data()

        ret = self.multicall.functions.aggregate([
            {'target': xvs_balance.address, 'callData': xvs_balance_data},
            {'target': claim_venus.address, 'callData': claim_venus_data},
            {'target': xvs_balance.address, 'callData': xvs_balance_data},
        ]).call(transaction={'from': user}, block_identifier=block_number)

        xvs_balance_output_types = get_abi_output_types(xvs_balance.abi)

        initial_balance = xvs_balance.web3.codec.decode_abi(
            xvs_balance_output_types, ret[1][0])[0]
        claim_balance = xvs_balance.web3.codec.decode_abi(
            xvs_balance_output_types, ret[1][2])[0]
        return claim_balance - initial_balance

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

        title_str = " [link=https://app.venus.io/][bold blue]Venus[/][/link] on BSC"
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
