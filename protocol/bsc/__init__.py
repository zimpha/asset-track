#!/usr/bin/env python3

import os
import json

from . import belt as _belt
from . import autofarm as _autofarm
from . import beefy as _beefy
from . import bzx as _bzx
from . import flux as _flux
from . import bunny as _bunny
from . import bakery as _bakery

_abi_dir = '/'.join(os.path.dirname(__file__).split('/')[:-2])

_autofarm_abi = json.load(open(_abi_dir + '/abi/autofarm.json'))
Autofarm = _autofarm.Autofarm(abi=_autofarm_abi)

_beefy_abi = json.load(open(_abi_dir + '/abi/beefy.json'))
Beefy = _beefy.Beefy(vault_abi=_beefy_abi)

_belt_vault_abi = json.load(open(_abi_dir + '/abi/belt_vault.json'))
_belt_swap_abi = json.load(open(_abi_dir + '/abi/belt_swap.json'))
_belt_master_abi = json.load(open(_abi_dir + '/abi/belt_master.json'))
Belt = _belt.Belt(_belt_vault_abi, _belt_swap_abi, _belt_master_abi)

_bzx_vault_abi = json.load(open(_abi_dir + '/abi/bzx_vault.json'))
_bzx_master_abi = json.load(open(_abi_dir + '/abi/bzx_master.json'))
BZX = _bzx.BZX(master_abi=_bzx_master_abi, vault_abi=_bzx_vault_abi)

_flux_market_abi = json.load(open(_abi_dir + '/abi/flux_market.json'))
_flux_provider_abi = json.load(open(_abi_dir + '/abi/flux_provider.json'))
Flux = _flux.Flux(_flux_provider_abi, _flux_market_abi)

_bunny_abi = json.load(open(_abi_dir + '/abi/bunny.json'))
Bunny = _bunny.Bunny(dashboard_abi=_bunny_abi)

_bakery_abi = json.load(open(_abi_dir + '/abi/bakery.json'))
Bakery = _bakery.Bakery(master_abi=_bakery_abi)

protocols = {
    'Autofarm': Autofarm,
    'Beefy': Beefy,
    'Belt': Belt,
    'BZX': BZX,
    'Flux': Flux,
    'Bunny': Bunny,
    'Bakery': Bakery,
}