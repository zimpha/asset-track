#!/usr/bin/env python3

from rich.table import Table

from chain.bsc import w3
from oracle.apy import beefy_apy

beefy_vault = {
    # 1Inch
    '1INCH': ('0xBa53AF4C2f1649F82e8070FB306DDBF2771A1950', '1inch-1inch'),
    # Alpaca
    'sALPACA': ('0xCd1C6adca69071F61EfE5aaa0BB63cA3419D5088', 'alpaca-salpaca'),
    # ApeSwap
    'BANANA': ('0xD307e7CC6a302046b7D91D83aa4B8324cFB7a786', 'banana-banana'),
    # Autofarm
    'autoCAKE': ('0xe0B473c0dD6D7Fea5B395c3Ce7ffd4FEF0ab4373', 'auto-cake'),
    # Bakery
    'BAKE': ('0xaC112E7744C129ae54E65F5D2cb4eA472E08eA0B', 'bakery-bake'),
    # Beefy
    'BIFI': ('0xf7069e41C57EcC5F122093811d8c75bdB5f7c14e', 'bifi-maxi'),
    # Belt
    'beltBTC': ('0xD411121C948Cff739857513E1ADF25ED448623f8', 'belt-beltbtc'),
    'beltETH': ('0xf2064C230b285AA6Cf45c6267DA86a8E3505D0AA', 'belt-belteth'),
    'beltBNB': ('0xC34Ae91312A3c3F9420691922040a5DEe1698E52', 'belt-beltbnb'),
    '4Belt': ('0xc1fcf50ccaCd1583BD9d3b41657056878C94e592', 'belt-4belt'),
    # Blizzard
    'xBLZD': ('0xf69bA3131029173Ca97aa43400B10689f5C23f59', 'blizzard-xblzd'),
    # Ellipsis
    '3EPS': ('0xE563c046147b4dF98bfCD3d00Dc54511F0c3b752', 'ellipsis-3eps'),
    'renBTC': ('0x24AE9e5424575690aCab61a384B6A76d69F4f89c', 'ellipsis-renbtc'),
    'fUSDT': ('0x8D3B7a0b20d490cbDACC2c555c05b7132B856e4b', 'ellipsis-fusdt-3eps'),
    # Kebab
    'KEBAB': ('0xE2231D4ca4921Cb35680bac714C9d40C8d217494', 'kebab-kebab'),
    # Pancake
    'CAKE': ('0xB0BDBB9E507dBF55f4aC1ef6ADa3E216202e06FD', 'cake-smart'),
    # Swamp
    'SWAMP': ('0x06C9e0b65ff4e02940c5b0f50b27D799622b2b39', 'swamp-swamp'),
    'swampCAKE': ('0x4d1A2b3119895d887b87509693338b86730bCE06', 'swamp-cake'),
    # Venus
    'BNB': ('0x6BE4741AB0aD233e4315a10bc783a7B923386b71', 'venus-bnb'),
    'WBNB': ('0x6BE4741AB0aD233e4315a10bc783a7B923386b71', 'venus-wbnb'),
}


class Beefy(object):
    BIFI = '0xCa3F508B8e4Dd382eE878A314789373D80A5190A'

    def __init__(self, vault_abi):
        self.vaults = {}
        for token_name, (address, _) in beefy_vault.items():
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
    def pool_name(original_token_name, original_protocol=None):
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
        if pool_name not in beefy_vault:
            return 0
        id = beefy_vault[pool_name][1]
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