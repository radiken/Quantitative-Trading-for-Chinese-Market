# Quantitative Trading for Chinese Stock Market v0.0.1 
# A股量化交易工具

## Background
To trade systematically and find outstanding strategies, a tool for writing, testing and applying strategies is needed, this tool is thereby appeared to help traders like me.

## Introduction
This app allows strategies writing, strategies testing by looping back, if you find your strategy outstanding, you can get your advised operation according to your strategies in the next trade day.

Time unit in this app is **day** for now, which means operation in hour, minute, and second is not supported temporarily.

Strategies include **stock selection strategy**, **buy strategy** and **sell strategy** three types of strategies, each strategy is a class instead of a function, as it can have its own attribute. An individual strategy, regardless of type, is meant to by controlling a single factor, which means multiple strategies of one type can be applied at the same time, but each type needs at least one strategy.

## Requirements
- Python 3
- A tushare account(Some of the interfaces may require higher account credits, please visit https://tushare.pro/ for details)

## Installation
In "src/initialize.py", replace you tushare token in:
```
ts.set_token('your token')
```
Then run this file(should take a while in order to save some necessary data, but will make later running process a lot faster).

## Usage
- Writing strategies
    Write your own stock selection strategies in "src/strategies/single_factor_strategies/stock_selection_strategies.py".
    Write your own buy strategies in "src/strategies/single_factor_strategies/buy_strategies.py".
    Write your own sell strategies in "src/strategies/single_factor_strategies/sell_strategies.py".
    Each file contains an example strategy.

- loop back
    See "src/example.py" for example of loop back process.

- applying strategies
    See bottom of "src/tomorrow_strategy.py".

## License
    GPL-3.0


