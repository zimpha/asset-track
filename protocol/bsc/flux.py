#!/usr/bin/env python3

from rich.table import Table

from chain.bsc import w3
from protocol import LendingBase

name_to_market = {
    'fCFX': '0xd4a16acCC595D958074283a592A924B08377beE9',
    'fBTC': '0x57CF28ee005c2980c2ce5468bb8C52E401C786f3',
    'fETH': '0xeFB1f48A1a367A509Ecef1578E5004d4013fc7A6',
    'fBNB': '0x7318724420F0aEec23d8919cC5effd6F4c6AbB4f',
    'fUSDT': '0x831b0AfAA3B22e1435169c7585CCC1861A2C9cbC',
    'fBUSD': '0xAb087D84cd75c31Ace78EC025ADFF21954a9A8a2',
    'fUSDC': '0xbCaD63dcfcF65D9eaDD99E344e327E65432f222E',
    'fDAI': '0x77eD25296855b88bd3C0b3Bf429B816555525115',
    'fMDX': '0x71B2047ad554bEC42b83b10A5fcB3128bd5E0986',
    'fDOT': '0xe5C257082550D0F23cCb7f20D383b02a3F74f69A',
    'fXRP': '0xd3639F2473F30751a7eAD8E26072161CDb404b28',
}

market_to_name = {}
for name, market in name_to_market.items():
    market_to_name[market] = name


class Flux(LendingBase):
    bcFLUX = '0x0747CDA49C82d3fc6B06dF1822E1DE0c16673e9F'

    def __init__(self, provider_abi, market_abi):
        self.contract = w3.eth.contract(
            abi=provider_abi, address='0xbbf0f936045cb99c60EAFddb03A830a2dFa5Fb94')
        self.markets = {}
        for token_name, address in name_to_market.items():
            self.markets[token_name] = w3.eth.contract(
                abi=market_abi, address=name_to_market[token_name])
        self.cache = {}

    @property
    def name(self):
        return 'Flux'

    @staticmethod
    def token_name():
        return 'FLUX'

    @staticmethod
    def token_slug_name():
        return ''

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        return 'f' + original_token_name

    def supply(self, user, pool_name, block_number='latest', optimizer=None):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0, 0, 0
        else:
            shares = self.markets[pool_name].functions.balanceOf(
                user).call(block_identifier=block_number)
            return shares, user_info['supply']

    def borrow(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0
        else:
            return user_info['borrow']

    def reward(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return {'FLUX': 0}
        else:
            return {'FLUX': (user_info['flux_supply'] + user_info['flux_borrow']) / 10 ** 18}

    def supply_interest_rate(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0
        return user_info['supply_apy'] - user_info['flux_supply_apy']

    def borrow_interest_rate(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0
        return user_info['flux_borrow_apy'] - user_info['borrow_apy']

    def borrow_apy(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0
        return user_info['borrow_apy']

    def supply_apy(self, user, pool_name, block_number='latest'):
        user_info = self._get_user_info(
            user, block_number).get(pool_name, None)
        if user_info is None:
            return 0
        return user_info['supply_apy']

    def supply_value(self, user, block_number='latest'):
        user_info = self._get_user_info(user, block_number)
        return user_info.get('supply_value', 0)

    def borrow_value(self, user, block_number='latest'):
        user_info = self._get_user_info(user, block_number)
        return user_info.get('borrow_value', 0)

    def _get_user_info(self, user, block_number='latest'):
        if user in self.cache:
            return self.cache[user]
        user_info = {}
        _, markets, flux_supplies, flux_borrows = self.contract.functions.unclaimedFluxAtLoan(
            user).call(block_identifier=block_number)
        for (market, flux_supply, flux_borrow) in zip(markets, flux_supplies, flux_borrows):
            token_name = market_to_name[market]
            user_info[token_name] = {
                'flux_supply': flux_supply,
                'flux_borrow': flux_borrow,
                'supply_apy': 0,
                'borrow_apy': 0,
                'flux_supply_apy': 0,
                'flux_borrow_apy': 0,
                'supply': 0,
                'borrow': 0,
            }
        _, _, _, _, supply_value, borrow_value, markets, supply_apys, borrow_apys, borrow_flux_apys, supply_flux_apys, supplies, borrows = self.contract.functions.getProfitability(
            user).call(block_identifier=block_number)
        for (market, supply_apy, borrow_apy, flux_supply_apy, flux_borrow_apy, supply, borrow) in zip(markets, supply_apys, borrow_apys, supply_flux_apys, borrow_flux_apys, supplies, borrows):
            token_name = market_to_name[market]
            user_info.setdefault(token_name, {})
            user_info['supply_value'] = supply_value / 10 ** 18
            user_info['borrow_value'] = borrow_value / 10 ** 18
            user_info[token_name].update({
                'supply_apy': supply_apy / 10 ** 16,
                'borrow_apy': borrow_apy / 10 ** 16,
                'flux_supply_apy': flux_supply_apy / 10 ** 16,
                'flux_borrow_apy': flux_borrow_apy / 10 ** 16,
                'supply': supply,
                'borrow': borrow,
            })
        self.cache[user] = user_info
        return user_info

    def print_pools(self, console, supply_value, borrow_value, pools, usd_total, usd_delta):
        total_supply = 0
        total_borrow = 0
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
        for pool in pools:
            if pool['type'] == 'lend':
                supply_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['rewards'],
                    pool['interest_rate'],
                    pool['farm_apy'],
                    pool['usd'])
            else:
                borrow_table.add_row(
                    pool['name'],
                    pool['balance'],
                    pool['rewards'],
                    pool['interest_rate'],
                    pool['farm_apy'],
                    pool['usd'])

        title_str = " [link=https://flux.01.finance/bsc/][bold blue]Flux[/][/link] on BSC"
        if usd_delta >= 0:
            title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(
                usd_total, usd_delta)
        else:
            title_str += "    [bold white]${:.0f}[/]  [red]${:.0f}[/]".format(
                usd_total, usd_delta)
        console.print(title_str, style='italic')
        if supply_value > 0:
            console.print(' Collateralization Ratio: {:.2f}%'.format(
                supply_value / borrow_value * 100))
        console.print(supply_table)
        console.print(borrow_table)
