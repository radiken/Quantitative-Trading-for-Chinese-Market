import datetime
import pandas as pd
import tushare as ts
import pytz
from calculation import *

def tomorrow_strategy(today, strategy, fund_available, hold_shares):
    stock_pool = strategy.stock_selection(today)
    strategy.prepare_data(today, list(hold_shares['stock']))
    print(f"stocks considerable according to the strategies:\n {stock_pool}")
    sell_dict = strategy.sell(today, hold_shares)
    if not sell_dict:
        print("No sell operation recommended.")
    for stock in sell_dict:
        (price, amount) = sell_dict[stock]
        print(f"Sell {amount} of stock {stock} at price {price}.")
    buy_dict = strategy.buy(today, stock_pool, fund_available)
    if not buy_dict:
        print("No buy operation recommended.")
    for stock in buy_dict:
        (price, amount) = buy_dict[stock]
        print(f"Buy {amount} of stock {stock} at price {price}.")

def get_to_check_date():
    Chinese_datetime = str(get_Chinese_datetime())
    hour = Chinese_datetime[8:10]
    if int(hour)<= 17:
        print("Too early for to get today strategy, getting last trade day's strategy.")
        date = get_yesterday_date()
    else:
        date = Chinese_datetime[:8]

    cal = ts.pro_api().trade_cal(start_date=date, end_date=date, fields='is_open, pretrade_date').loc[0]
    last_trade_date = date if cal['is_open']==1 else cal['pretrade_date']
    return last_trade_date


if __name__ == "__main__":
    hold_shares = pd.DataFrame(columns=["stock", "amount", "cost", "buy_date"])
    num = int(input("Enter the number of holding stocks:"))
    for _ in range(num):
        stock = input("Enter stock: ")
        amount = int(input(f"Enter holding amount of {stock}: "))
        cost = float(input(f"Enter average cost of {stock}: "))
        buy_date = input(f"Enter buy date of {stock}: ")
        
        hold_shares = hold_shares.append(pd.DataFrame({'stock':[stock], 'amount':[amount], 'cost':[cost], 'buy_date':[{buy_date:amount}]}), ignore_index = True, sort = False)

    fund_available = int(input("Please enter available fund: "))

    # init strategy
    from strategies.strategy import strategy
    from strategies.single_factor_strategies.stock_selection_strategies import example_stock_selection_strategy
    from strategies.single_factor_strategies.buy_strategies import example_buy_strategy
    from strategies.single_factor_strategies.sell_strategies import example_sell_strategy

    last_trade_date = get_to_check_date()
    
    sss = example_stock_selection_strategy()
    bs = example_buy_strategy()
    ss = example_sell_strategy()

    my_strategy = strategy(last_trade_date, last_trade_date, [sss], [bs], [ss])

    # execute
    tomorrow_strategy(last_trade_date, my_strategy, fund_available, hold_shares)
    

