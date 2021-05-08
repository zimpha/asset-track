# Asset Tracking

Track your asset in BSC.

Install dependencies by pip3

```bash
pip3 install rich web3 requests
```

Use the following to show assets in BSC.

```bash
python3 portfolio.py 'example_account'
```

Add `--save` to make a checkpont.

```bash
python3 portfolio.py 'example_account' --save
```

Each single asset can have a list of yield farming strategies. And each strategy contains at most three fields:

+ `type` is the type of this strategy, which is one of `stake`, `loan` or `lend`.
+ `yield` is the original protocol where you stake/supply/borrow the token.
+ `optimizer` is the protocol where you put the `yield` protocol's token, such as `Autofarm` and `Beefy`. This is optional.

See `accounts/example_account.json` for more details.

## Supported Protocols

+ [Autofarm](https://autofarm.network/)
+ [Bakery](https://www.bakeryswap.org)
+ [Beefy](https://beefy.finance/) without boost
+ [Belt](https://belt.fi/)
+ [Bunny](https://pancakebunny.finance/)
+ [bZx](https://bsc.fulcrum.trade/farm)
+ [Flux](https://flux.01.finance/bsc/)

## TODO:
  + add more protocols
  + add liquidity pool
  + add ETH
  + add CFX
