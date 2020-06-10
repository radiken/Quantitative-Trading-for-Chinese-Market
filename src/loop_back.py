import tushare as ts
from info_holder import info_holder
from calculation import *
from report import report
import re
import pandas as pd
import time
from tqdm import tqdm

'''
Loop back function execute every trading day, it sells before it buys.
Result comes out with words on the terminal at the moment. 
Get report when finished.
'''

# 

class loop_back():
    def __init__(self, strategy, fund = 100000, start_date = '20180101', end_date = '20190101', frequency = 1, exchange_fee = 0.0003):
        self._strategy = strategy
        strategy.set_exchange_fee(exchange_fee)
        self._fund = fund
        self._starting_fund = fund
        self._start_date = start_date
        self._end_date = end_date
        self._frequency = frequency
        self._stock_pool = []
        self._exchange_fee = exchange_fee
        self._holding_stocks = pd.DataFrame(columns = ('stock', 'amount', 'cost', 'buy_date'))
        self._fund_record = pd.DataFrame(columns = ('trade_date', 'fund', 'fund_pct_chg'))
        self._daily_info = {}
        self._info_holder = info_holder()
        self._stock_pool_info = pd.DataFrame(columns = ('stock_pool', 'start_date', 'end_date'))
        self._buy_info = pd.DataFrame(columns = ('stock', 'price', 'amount', 'date', 'exchange_fee'))
        self._sell_info = pd.DataFrame(columns = ('stock', 'price', 'amount', 'date', 'exchange_fee'))
        self._trade_info = pd.DataFrame(columns = ('stock', 'cost', 'price_sold', 'amount', 'buy_date', 'sell_date'))


    def run(self):
        counter = 0
        trade_cal = get_trade_cal(self._start_date, self._end_date)
        it = iter(trade_cal)
        next(it)
        prices = {}
        print('starting with fund %s' %self._fund)

        # main loop
        for day in tqdm(trade_cal):
            if counter % self._frequency == 0:
                next_day = next(it, 0)
                if next_day != 0:
                    if counter % self._strategy.stocks_lasting_day == 0:
                        # set stocks list
                        self._stock_pool = self._strategy.stock_selection(day)
                        try:
                            end_date = get_trade_date_from_date(day, self._strategy.stocks_lasting_day)
                        except:
                            # longer then end date
                            end_date = self._end_date
                        if len(self._stock_pool) == 0: 
                            self._stock_pool_info = self._stock_pool_info.append(pd.DataFrame({'stock_pool':['none'], 'start_date':[day], 'end_date':[end_date]}), ignore_index = True)
                        else:
                            self._stock_pool_info = self._stock_pool_info.append(pd.DataFrame({'stock_pool':[self._stock_pool], 'start_date':[day], 'end_date':[end_date]}), ignore_index = True)
                        # get daily info
                        self._daily_info = self._info_holder.daily_info

                    buy_fund = self._fund

                    # sell
                    sell_dict = self._strategy.sell(day, self._holding_stocks)
                    for stock in sell_dict:
                        (price, amount) = sell_dict[stock]
                        if price == -1:
                            # is ex date, get the amount of div for free
                            self.buy(stock, -1, amount, day)
                        else:
                            next_day_info = get_rows_from_df_by_date(self._daily_info[stock], next_day, next_day)
                            if(len(next_day_info) == 1):
                                if (next_day_info['open'].iloc[0] >= price) & (not is_limit_down(next_day_info['pre_close'].iloc[0], next_day_info['open'].iloc[0])):
                                    self.sell(stock, next_day_info['open'].iloc[0], amount, next_day)
                                elif(next_day_info['high'].iloc[0] >= price) & (not is_limit_down(next_day_info['pre_close'].iloc[0], next_day_info['high'].iloc[0])):
                                    self.sell(stock, price, amount, next_day)

                    # buy
                    buy_dict = self._strategy.buy(day, self._stock_pool, buy_fund)
                    for stock in buy_dict:
                        (price, amount) = buy_dict[stock]
                        next_day_info = get_rows_from_df_by_date(self._daily_info[stock], next_day, next_day)
                        if(len(next_day_info == 1)):
                            if (next_day_info['open'].iloc[0] <= price) & (not is_limit_up(next_day_info['pre_close'].iloc[0], next_day_info['open'].iloc[0])):
                                self.buy(stock, next_day_info['open'].iloc[0], amount, next_day)
                            elif (next_day_info['low'].iloc[0] <= price)  & (not is_limit_up(next_day_info['pre_close'].iloc[0], next_day_info['low'].iloc[0])):
                                self.buy(stock, price, amount, next_day)

                hold_shares = {}
                for index, row in self._holding_stocks.iterrows():
                    stock = row['stock']
                    info = get_rows_from_df_by_date(self._daily_info[stock], day, day)
                    if len(info) == 1:
                        prices[stock] = float(info.close)
                    hold_shares[stock] = row['amount']
                total_worth = calculate_total_worth(hold_shares, prices) + self._fund
                if len(self._fund_record) > 0:
                    last_total_worth = self._fund_record['fund'].iloc[-1]
                else:
                    last_total_worth = total_worth
                self._fund_record = self._fund_record.append(pd.DataFrame({'trade_date':[day], 'fund':[total_worth], 'fund_pct_chg':[(total_worth/last_total_worth) - 1]}), ignore_index = True)

            counter += 1
            
        print('Finished, generating report...')
        self.format_report()
        return self._fund
        
    def buy(self, stock, price, amount, date):
        # sending shares
        if price == -1:
            for index, row in self._holding_stocks.iterrows():
                if row['stock']==stock:
                    average = calculate_average_price(row['cost'], row['amount'], price, amount)
                    self._holding_stocks.at[index,'amount'] += amount
                    self._holding_stocks.at[index,'cost'] = average
                    row['buy_date'][date] = amount
                    return
            return
            
        if amount != 0:
            trading_amount = price * amount
            exchange_fee = calculate_buy_exchange_fee(trading_amount, self._exchange_fee)
            self._fund -= (trading_amount + exchange_fee)
            self._buy_info = self._buy_info.append(pd.DataFrame({'stock':[stock], 'price':[price], 'amount':[amount], 'date':[date], 'exchange_fee':[exchange_fee]}), ignore_index = True)
            for index, row in self._holding_stocks.iterrows():
                if row['stock']==stock:
                    average = calculate_average_price(row['cost'], row['amount'], price, amount)
                    self._holding_stocks.at[index,'amount'] += amount
                    self._holding_stocks.at[index,'cost'] = average
                    row['buy_date'][date] = amount
                    return
            self._holding_stocks = self._holding_stocks.append(pd.DataFrame({'stock':[stock], 'amount':[amount], 'cost':[price], 'buy_date':[{date:amount}]}), ignore_index = True)

    def sell(self, stock, price, amount, date):
        trading_amount = price * amount
        exchange_fee = calculate_sell_exchange_fee(trading_amount, self._exchange_fee)
        self._fund += (trading_amount - exchange_fee)
        self._sell_info = self._sell_info.append(pd.DataFrame({'stock':[stock], 'price':[price], 'amount':[amount], 'date':[date], 'exchange_fee':[exchange_fee]}), ignore_index = True)
        row = self._holding_stocks[self._holding_stocks.stock.isin([stock])]
        cost = row['cost'].iloc[0]
        new_amount = row['amount'].iloc[0] - amount
        if new_amount != 0:
            # update buy date dict
            to_decrease = amount
            to_delete = []
            buy_date_dict = row['buy_date'].iloc[0]
            for key, value in buy_date_dict.items():
                new_value = value - to_decrease
                if new_value <= 0: 
                    to_delete.append(key)
                    if new_value == 0:
                        self._trade_info = self._trade_info.append(pd.DataFrame({'stock':[stock], 'cost':[cost], 'price_sold':[price], 'amount':[value], 'buy_date':[key], 'sell_date':[date]}), ignore_index = True)
                        break
                    else:
                        to_decrease = -new_value
                else:
                    buy_date_dict[key] -= to_decrease
                    self._trade_info = self._trade_info.append(pd.DataFrame({'stock':[stock], 'cost':[cost], 'price_sold':[price], 'amount':[to_decrease], 'buy_date':[key], 'sell_date':[date]}), ignore_index = True)
                    break
            for key in to_delete:
                del buy_date_dict[key]
            # update amount
            self._holding_stocks.at[row.index.values.astype(int)[0],'amount'] = new_amount
        else:
            buy_date = next(iter(row['buy_date'].iloc[0]))
            self._trade_info = self._trade_info.append(pd.DataFrame({'stock':[stock], 'cost':[cost], 'price_sold':[price], 'amount':[amount], 'buy_date':[buy_date], 'sell_date':[date]}), ignore_index = True)
            self._holding_stocks = self._holding_stocks[self._holding_stocks.stock != stock]


    def format_report(self):
        r = report(self._start_date, self._end_date)
        try:
            r.stock_selection_analysis(self._stock_pool_info)
        except Exception as e:
            print(e)
        try:
            r.trade_analysis(self._trade_info, self._buy_info, self._sell_info)
        except Exception as e:
            print(e)
        try:
            r.fund_analysis(self._starting_fund, self._fund_record)
        except Exception as e:
            print(e)
    

