#!/usr/bin/env python3

import sys
import json

from rich.console import Console
from rich.table import Table

from oracle import price
from protocol.bsc import protocols
from chain.bsc import w3
from tokens.bsc import wallet_token_balance
from datetime import datetime

def load_account(account_name):
    account_info = json.load(open('./accounts/{}.json'.format(account_name)))
    account = account_info['account']
    token_slug_set = set()
    portfolio = {}
    for token, strategies in account_info['portfolio']['bsc']['single-asset'].items():
        for strategy in strategies:
            if strategy['yield'] not in protocols:
                raise RuntimeError("Protocol[{}] not supported".format(strategy['yield']))
            strategy['token'] = token
            if 'optimizer' in strategy:
                target_protocol = strategy['optimizer']
            else:
                target_protocol = strategy['yield']
            if target_protocol in protocols:
                token_slug_set.add(protocols[target_protocol].token_slug_name())
            else:
                raise RuntimeError("Protocol[{}] not supported".format(target_protocol))
            portfolio.setdefault(target_protocol, [])
            portfolio[target_protocol].append(strategy)
    return account, portfolio, token_slug_set


def print_records(records):
    table = Table(show_header=True, header_style="bold magenta")
    table.add


def format_reward_info(rewards, token_prices):
    result = []
    for token, value in rewards.items():
        result.append('{:.2f} {} (${:.0f})'.format(value, token, value * token_prices.get(token, 0)))
    return '+'.join(result)


def get_usd_value(rewards, token_prices):
    result = 0
    for token, value in rewards.items():
        result += token_prices.get(token, 0) * value
    return result


account_name = sys.argv[1]
account, portfolio, token_slug_set = load_account(account_name)

token_prices = price.token_prices(token_slug_set)

try:
    accounts_history = json.load(open('./store/store.json'))
except Exception as e:
    accounts_history = {}

last_checkpoint = accounts_history.get(account_name, [{}])[-1]

checkpoint = {}
checkpoint['time'] = str(datetime.now())
checkpoint['protocols'] = {}
checkpoint['tokens'] = {}

console = Console()

console.print('Portfolio of account\[{}] address[{}]:'.format(account_name, account), style="bold")
console.print(checkpoint['time'])
console.print('')

total_asset_usd = 0
for protocol_name, strategies in portfolio.items():
    protocol = protocols[protocol_name]
    pools = []
    protocol_usd_total = 0

    for strategy in strategies:
        type = strategy['type']
        token_name = strategy['token']
        token_price = token_prices[token_name]
        yield_pool = protocols[strategy['yield']]
        pool_name = yield_pool.pool_name(token_name)
        if 'optimizer' in strategy:
            optimizer = protocols[strategy['optimizer']]
        else:
            optimizer = None
        if type == 'lend':
            shares, token_amount = yield_pool.supply(account, pool_name, optimizer=optimizer)
            token_amount /= 10 ** 18
            shares /= 10 ** yield_pool.share_decimals
            if optimizer is None:
                rewards = yield_pool.supply_reward(account, pool_name)
                interest_rate = yield_pool.supply_interest_rate(account, pool_name)
                farm_apy = yield_pool.supply_apy(account, pool_name)
                pools.append({
                    'type': 'lend',
                    'name': token_name,
                    'balance': '{:.3f} {}'.format(token_amount, token_name),
                    'rewards': format_reward_info(rewards, token_prices),
                    'interest_rate': '{:.2f}%'.format(interest_rate),
                    'farm_apy': '{:.2f}%'.format(farm_apy),
                    'usd': '${:.0f}'.format(token_amount * token_price + get_usd_value(rewards, token_prices))
                })
            else:
                pool_name = optimizer.pool_name(pool_name)
                rewards = optimizer.reward(account, pool_name)
                farm_apy = optimizer.apy(pool_name)
                pools.append({
                    'name': pool_name,
                    'shares': '{:.3f}'.format(shares),
                    'assets': '{:.3f} {}'.format(token_amount, token_name),
                    'rewards': format_reward_info(rewards, token_prices),
                    'farm_apy': '{:.2f}%'.format(farm_apy),
                    'usd': '${:.0f}'.format(token_amount * token_price + get_usd_value(rewards, token_prices))
                })
        elif type == 'stake':
            shares, token_amount = yield_pool.staked(account, pool_name, optimizer=optimizer)
            shares /= 10 ** yield_pool.share_decimals
            token_amount /= 10 ** 18
            if optimizer is None:
                rewards = yield_pool.reward(account, pool_name)
                farm_apy = yield_pool.apy(pool_name)
            else:
                pool_name = optimizer.pool_name(pool_name)
                rewards = optimizer.reward(account, pool_name)
                farm_apy = optimizer.apy(pool_name)
            pools.append({
                'name': pool_name,
                'shares': '{:.3f}'.format(shares),
                'assets': '{:.3f} {}'.format(token_amount, token_name),
                'rewards': format_reward_info(rewards, token_prices),
                'farm_apy': '{:.2f}%'.format(farm_apy),
                'usd': '${:.0f}'.format(token_amount * token_price + get_usd_value(rewards, token_prices))
            })
        elif type == 'loan':
            token_amount = yield_pool.borrow(account, pool_name)
            rewards = yield_pool.borrow_reward(account, pool_name)
            interest_rate = yield_pool.borrow_interest_rate(account, pool_name)
            farm_apy = yield_pool.borrow_apy(account, pool_name)
            token_amount = -token_amount / 10 ** 18
            usd_value = token_amount * token_price + get_usd_value(rewards, token_prices)
            pools.append({
                'type': 'loan',
                'name': token_name,
                'balance': '{:.3f} {}'.format(token_amount, token_name),
                'rewards': format_reward_info(rewards, token_prices),
                'interest_rate': '{:.2f}%'.format(interest_rate),
                'farm_apy': '{:.2f}%'.format(farm_apy),
                'usd': '{}${:.0f}'.format('' if usd_value >= 0 else '-', abs(usd_value))
            })
        checkpoint['tokens'].setdefault(token_name, {'amount': 0, 'usd_value': 0})
        checkpoint['tokens'][token_name]['amount'] += token_amount
        for reward_token_name, reward_amount in rewards.items():
            checkpoint['tokens'].setdefault(reward_token_name, {'amount': 0, 'usd_value': 0})
            checkpoint['tokens'][reward_token_name]['amount'] += reward_amount
        last_protocol_record = last_checkpoint.get('protocols', {}).get(protocol_name, {})
        protocol_usd_total += token_amount * token_price + get_usd_value(rewards, token_prices)
        protocol_usd_delta = protocol_usd_total - last_protocol_record.get('usd_value', 0)
    checkpoint['protocols'].setdefault(protocol_name, {})
    checkpoint['protocols'][protocol_name]['usd_value'] = protocol_usd_total
    if protocol.type == 'Lending':
        supply_value = protocol.supply_value(account)
        borrow_value = protocol.borrow_value(account)
        protocol.print_pools(console, supply_value, borrow_value, pools, protocol_usd_total, protocol_usd_delta)
    else:
        protocol.print_pools(console, pools, protocol_usd_total, protocol_usd_delta)
    total_asset_usd += protocol_usd_total

# show wallet tokens
wallet_tokens = wallet_token_balance(account)
wallet_table = Table(
        show_header=True,
        header_style="bold magenta")
wallet_table.add_column('Token')
wallet_table.add_column('Balance', justify='right')
wallet_table.add_column('USD Value', justify='right')
wallet_usd_value = 0
wallet_usd_delta = 0
checkpoint['wallet'] = {}
for token_name, token_balance in wallet_tokens.items():
    token_usd_value = token_balance * token_prices.get(token_name, 0)
    checkpoint['wallet'][token_name] = {
        'amount': token_balance,
        'usd_value': token_usd_value,
    }
    checkpoint['tokens'].setdefault(token_name, {'amount': 0, 'usd_value': 0})
    checkpoint['tokens'][token_name]['amount'] += token_balance
    if token_usd_value < 1.0:
        continue
    wallet_usd_value += token_usd_value
    wallet_usd_delta += token_usd_value
    wallet_usd_delta -= last_checkpoint.get('wallet', {}).get(token_name, {}).get('usd_value', 0)
    wallet_table.add_row(
        token_name,
        '{:.3f}'.format(token_balance),
        '${:.0f}'.format(token_usd_value))
total_asset_usd += wallet_usd_value
title_str = " [bold blue]Wallet[/] on BSC"
if wallet_usd_delta >= 0:
    title_str += "    [bold white]${:.0f}[/]  [green]+${:.0f}[/]".format(wallet_usd_value, wallet_usd_delta)
else:
    title_str += "    [bold white]${:.0f}[/]  [red]-${:.0f}[/]".format(wallet_usd_value, -wallet_usd_delta)
console.print(title_str, style='italic')
console.print(wallet_table)

asset_usd_delta = total_asset_usd - last_checkpoint.get('net_worth', 0)
color = 'green' if asset_usd_delta >= 0 else 'red'
sign = '+' if asset_usd_delta >= 0 else ''
console.print("Net Worth: [bold]${:.0f}[/]    [{}]{}${:.0f}[/]".format(total_asset_usd, color, sign, asset_usd_delta))
asset_table = Table(
        show_header=True,
        header_style="bold magenta")
asset_table.add_column('Token')
asset_table.add_column('Balance', justify='right')
asset_table.add_column('Price', justify='right')
asset_table.add_column('USD Value', justify='right')
asset_table.add_column('Change', justify='right')
for token_name, token_info in checkpoint['tokens'].items():
    token_amount = token_info['amount']
    token_usd_value = token_amount * token_prices.get(token_name, 0)
    token_info['usd_value'] = token_usd_value
    if token_usd_value < 1.0:
        continue
    last_usd_value = last_checkpoint.get('tokens', {}).get(token_name, {}).get('usd_value', 0)
    token_usd_delta = token_usd_value - last_usd_value
    color = 'green' if token_usd_delta >= 0 else 'red'
    sign = '+' if token_usd_delta >= 0 else '-'
    asset_table.add_row(
        token_name,
        '{:.3f}'.format(token_info['amount']),
        '${:.5f}'.format(token_prices.get(token_name, 0)),
        '${:.0f}'.format(token_usd_value),
        '[{}]{}${:.0f}[/]'.format(color, sign, abs(token_usd_delta)))
console.print(asset_table)

checkpoint['net_worth'] = total_asset_usd
accounts_history.setdefault(account_name, [])
accounts_history[account_name].append(checkpoint)
if '--save' in sys.argv:
    with open('./store/store.json', 'w') as fp:
        fp.write(json.dumps(accounts_history, indent=2))