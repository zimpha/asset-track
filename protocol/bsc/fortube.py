#!/usr/bin/env python3

from rich.table import Table

from chain.bsc import w3
from protocol import LendingBase

fortube_vault = {
    'fUSDT': ('0xBf9213D046C2c1e6775dA2363fC47F10C4471255', 0),
    'fBUSD': ('0x57160962Dc107C8FBC2A619aCA43F79Fd03E7556', 1),
    'fDAI': ('0x312e1635BCB5D1410F1BC52640592EA4F63820ef', 2),
    'fETH': ('0xE2272A850188B43E94eD6DF5b75f1a2FDcd5aC26', 3),
    'fBNB': ('0xf330b39f74e7f71ab9604A5307690872b8125aC8', 4),
    'fBTC': ('0xb5C15fD55C73d9BeeC046CB4DAce1e7975DcBBBc', 5),
    'fBCH': ('0x33d6D5F813BF78163901b1e72Fb1fEB90E72fD72', 6),
    'fLTC': ('0x3Ccc8A3D59F8277bF0d598EA3199418c55cD6CA9', 7),
    'fXRP': ('0x5Aa9FD16FF5D336BeFC87ED0c7B4B5194530AA9B', 8),
    'fDOT': ('0x534CD786C2907ABb600feC375D4B513700e592D3', 9),
    'fLINK': ('0xF8C5965BfBAE9c429F91BA357d930Ed78ffd4cF9', 10),
    'fONT': ('0x0C2F5921681a7dd956e223fae5DC23502BcB43cD', 11),
    'fXTZ': ('0x9435e4B80FaA75E2ec770d134dCeA1B590A4E6FB', 12),
    'fEOS': ('0x8CCDba35C3E3c6ce513B4cB058c1cF2f9bEfc9B3', 13),
    'fFOR': ('0x53345F3B9FCb873783FfA5C8F043233AfD4991a6', 14),
    'fYFII': ('0x2c2ca6abAcb43f38d86253d8d762687DB43Dc0d0', 15),
    'fZEC': ('0xcdBcD1c5237DE8954b5E76149Bad0aAFc114df99', 16),
    'fCREAM': ('0x25a7c3A4f1ceffB5C8907Ce28719FC5f8f2962B6', 17),
    'fBAND': ('0x77CCecaF88DF25E29A2BE941aBdcB8F98a33EAE3', 18),
    'fADA': ('0xe4F621719D6b9f1C392DA83e8d766D55b5663805', 19),
    'fATOM': ('0x5f6ffEE82666Db203d89fcf5ea730113455503Cb', 20),
    'fFIL': ('0xEe65F5eD0767D935318CBA04D68e7931Ad0B508b', 21),
    'fQUSD': ('0x13902753864b13e486E573661Af919A7AD080F19', 22),
    'fBETH': ('0xf1f3147cebc1D74C88dFA56941E802ADcF788E03', 23),
    'fCAKE': ('0xa339C0ae7e47596017CCe2ac1459349A4f0aeb6C', 24),
    'fARPA': ('0x136CfE9c6601CC08d5F4500a03f2179F80f37B10', 25),
    'fUSDC': ('0xb2CB0Af60372E242710c42e1C34579178c3D2BED', 26),
    'fLINA': ('0x37d38C20b8AA0A1d89841d9f47d31757CF74835F', 27),
    'fvCAKE-BNB': ('0x8e2dbfc3b8ce40209a5211d76a780C97611C5eFf', 28),
    'fvBUSD-BNB': ('0x5993233d88B4424D9c12e468A39736D5948c2835', 29),
    'fvBTC-BNB': ('0x3CE92b88DEAec1037335E614Eb6409C95edcAC76', 30),
    'fvETH-BNB': ('0x93B9B852FcD2f964Faa7E50EC1374e016260718c', 31),
    'fvBETH-ETH': ('0x51da0A7340874674C488b67200D007E422667650', 32),
    'fvUSDT-BUSD': ('0xfDD543Ed2701dEB2a172Df4876E60918E28Ba217', 33),
    'fvUSDT-BNB': ('0x556be90ea81e8abceEc2737cf6AE0a6cfEe58b40', 34),
    'fvFOR-BUSD': ('0x52d61a0AA88170b6EbDEA25Be1561E5665e6481B', 35),
    'fvCAKE-BNB-v2': ('0xA16d9C88c129d282882F2B4e914c8E5c78aadBE3', 36),
    'fvBUSD-BNB-v2': ('0xCb1f33e226Db44B1c86B92284aD68b6C483AE294', 37),
    'fvBTC-BNB-v2': ('0xa09993Af1Ac4E278f440E1F413f1217dAbb35609', 38),
    'fvETH-BNB-v2': ('0x486047AF6d0cD9848e6AcF1Ad7aAF239A52d7874', 39),
    'fvUSDT-BUSD-v2': ('0x9aeD165cE81F0E82aF2cBc75445193b1d4365E07', 40),
    'fvUSDT-BNB-v2': ('0xB4Fc48088968714A4B7F3fF1b5EF388E7c686127', 41),
    'fvFOR-BUSD-v2': ('0x6704E5e4eD72C00aF94aa9cCe4232FB1379441c3', 42),
    'fTKO': ('0x8B2ef6d7d4Cc334D003398007722FdF8ca3f5E55', 43),
    'fCFX': ('0x2eafB53977eC7Ae95D1945eDD896E0565c816B1E', 44),
}


class ForTube(LendingBase):
    FOR = '0x658A109C5900BC6d2357c87549B651670E5b0539'

    def __init__(self, interest_rate_model_abi, controller_abi, vault_abi):
        self.vaults = {}
        for token_name, (address, _) in fortube_vault.items():
            self.vaults[token_name] = w3.eth.contract(
                abi=vault_abi, address=address)
        self.controller = w3.eth.contract(
            abi=controller_abi, address='0xc78248D676DeBB4597e88071D3d889eCA70E5469')
        self.interest_rate_model_abi = interest_rate_model_abi
        self.blocks_per_year = None

    @property
    def name(self):
        return 'ForTube'

    @staticmethod
    def token_name():
        return 'FOR'

    @staticmethod
    def token_slug_name():
        return 'the-force-protocol'

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return 'f' + original_token_name

    # return shares, asset and apy
    def supply(self, user, pool_name, block_number='latest', optimizer=None):
        if optimizer is None:
            shares = self.vaults[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
        else:
            _, shares = optimizer.staked(user, pool_name, block_number)
        token_price = self.vaults[pool_name].functions.exchangeRateStored().call(
            block_identifier=block_number)
        return shares, shares * token_price // 10 ** 18

    def borrow(self, user, pool_name, block_number='latest'):
        return self.vaults[pool_name].functions.borrowBalanceStored(user).call(block_identifier=block_number)

    def borrow_interest_rate(self, user, pool_name, block_number='latest'):
        self._get_blocks_per_year(pool_name)
        return self.blocks_per_year * self.vaults[pool_name].functions.getBorrowRate().call(block_identifier=block_number) / 10 ** 16

    def supply_interest_rate(self, user, pool_name, block_number='latest'):
        self._get_blocks_per_year(pool_name)
        return self.blocks_per_year * self.vaults[pool_name].functions.getSupplyRate().call(block_identifier=block_number) / 10 ** 16

    def reward(self, user, pool_name, block_number='latest'):
        return {'FOR': 0}

    def supply_reward(self, user, pool_name, block_number='latest'):
        return {'FOR': 0}

    def borrow_reward(self, user, pool_name, block_number='latest'):
        return {'FOR': 0}

    def borrow_apy(self, user, pool_name, block_number='latest'):
        return -self.borrow_interest_rate(user, pool_name, block_number)

    def supply_apy(self, user, pool_name, block_number='latest'):
        return self.supply_interest_rate(user, pool_name, block_number)

    def supply_value(self, user, block_number='latest'):
        return 0

    def borrow_value(self, user, block_number='latest'):
        return 0

    def _get_blocks_per_year(self, pool_name):
        if self.blocks_per_year is not None:
            return
        interest_rate_model = self.vaults[pool_name].functions.interestRateModel().call()
        interest_rate_contract = w3.eth.contract(
            abi=self.interest_rate_model_abi, address=interest_rate_model)
        self.blocks_per_year = interest_rate_contract.functions.blocksPerYear().call()

    def print_pools(self, console, supply_value, borrow_value, pools, usd_total, usd_delta):
        supply_table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        supply_table.add_column('Supplied')
        supply_table.add_column('Balance', justify='center')
        supply_table.add_column('Interest Rate', justify='right')
        supply_table.add_column('USD Value', justify='right')
        borrow_table = Table(
            show_header=True,
            header_style="bold magenta",
            title_justify="left")
        borrow_table.add_column('Borrowed')
        borrow_table.add_column('Balance', justify='center')
        borrow_table.add_column('Interest Rate', justify='right')
        borrow_table.add_column('USD Value', justify='right')
        supply, borrow = 0, 0
        for pool in pools:
            if pool['type'] == 'lend':
                supply += 1
                supply_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['interest_rate'],
                    pool['usd'])
            else:
                borrow += 1
                borrow_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['interest_rate'],
                    pool['usd'])

        title_str = " [link=https://for.tube/][bold blue]ForTube[/][/link] on BSC"
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
