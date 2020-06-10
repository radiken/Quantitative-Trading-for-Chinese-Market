import tushare as ts
import pandas as pd
from calculation import *
from info_holder import info_holder
import matplotlib.pyplot as plt
import numpy as np
import math

class report:
    def __init__(self, start_date, end_date):
        self._start_date = start_date
        self._end_date = end_date
        holder = info_holder()
        self._stocks_info = holder.daily_info
        self._standard = holder.get_standard_info(start_date, end_date)
        # self._standard = ts.pro_api().index_daily(ts_code='000001.SH', start_date = self._start_date, end_date = self._end_date)

    def stock_selection_analysis(self, stock_pool_history):
        empty_time = len(stock_pool_history[stock_pool_history.stock_pool == "none"])
        stock_pool_history = stock_pool_history[stock_pool_history.stock_pool != "none"]
        success_list = []
        failing_list = []

        changes = {}
        highest_price_df = pd.DataFrame(columns = ('stock', 'start_date', 'highest_date', 'highest_distance', 'highest_pct_chg', 
                                                    'lowest_date', 'lowest_distance', 'lowest_pct_chg', 'exist_length'))
        for index, row in stock_pool_history.iterrows():
            start_sum = 0
            end_sum = 0
            for stock in row['stock_pool']:
                stock_info = get_rows_from_df_by_date(self._stocks_info[stock], row['start_date'], row['end_date'])
                if len(stock_info) >= 2:
                    start_sum += float(stock_info['close'].iloc[-1])
                    end_sum += float(stock_info['close'].iloc[0])
            total_change = end_sum/start_sum

            standard_info = get_rows_from_df_by_date(self._standard, row['start_date'], row['end_date'])
            standard_start = float(standard_info['close'].iloc[-1])
            standard_end = float(standard_info['close'].iloc[0])
            standard_total_change = standard_end/standard_start

            if total_change/standard_total_change > 1:
                success_list.append(total_change - standard_total_change)
            else:
                failing_list.append(standard_total_change - total_change)

        print('\nstock pool analysis:')
        if empty_time > 0:
            print(f'stock pool was empty for {empty_time} times.')
        if len(success_list) > 0:
            print(f'{len(success_list)} stock selection choices were better than benchmark, in that period, they were {sum(success_list)/len(success_list)} better than benchmark')
        else:
            print('no choice better than benchmark')
        if len(failing_list) > 0:
            print(f'{len(failing_list)} stock selection choices were worses than benchmark, in that period, they were {sum(failing_list)/len(failing_list)} worse than benchmark')
        else:
            print('no choice worse than benchmark')


    def trade_analysis(self, trade_history, buy_history, sell_history):
        # try:
        #     trade_history.to_excel("output.xlsx")
        # except Exception as e:
        #     print(e)
        earn_counter = 0
        lost_counter = 0
        hold_time = []
        pct_earned = []
        pct_lost = []
        for index, row in trade_history.iterrows():
            change = row['price_sold']/row['cost']
            if change >= 1:
                earn_counter += 1
                pct_earned.append(change-1)
            else:
                lost_counter += 1
                pct_lost.append(1-change)
            hold_time.append(get_trade_date_distance(row['buy_date'], row['sell_date']))
        
        if len(hold_time) > 0:
            avg_hold_time = sum(hold_time)/len(hold_time)
            print('\ntrade analysis:')
            print(f'{len(hold_time)} trades made, average stock hold time was {int(avg_hold_time)} days, {earn_counter} trades earned money and {lost_counter} trades lost money')
            if earn_counter != 0:
                print(f'average percentage earned in earned trades is {sum(pct_earned)/len(pct_earned)}')
            if lost_counter != 0:
                print(f'average percentage lost in lost trades is {sum(pct_lost)/len(pct_lost)}')

        print(f'exchange fee: {sum(list(sell_history.exchange_fee))+sum(list(buy_history.exchange_fee))}')


    def fund_analysis(self, start_fund, fund_history):
        rf = 0.02

        loop_length = get_trade_date_distance(self._start_date, self._end_date)
        end_fund = fund_history.tail(1)['fund'].iloc[0]
        annualized_return = math.pow(end_fund/start_fund, 250/loop_length) - 1
        average_daily_return = sum(list(fund_history['fund_pct_chg']))/len(fund_history)
        earn_rate_sqrt_sum = sum([math.pow(i-average_daily_return, 2) for i in list(fund_history['fund_pct_chg'])])
        volatility = (250/(loop_length - 1)*earn_rate_sqrt_sum)**0.5

        benchmark_start = self._standard['open'].iloc[-1]
        benchmark_end = self._standard['close'].iloc[0]
        benchmark_returns = math.pow(benchmark_end/benchmark_start, 250/loop_length) - 1

        df = pd.merge(fund_history, self._standard, on='trade_date')
        df.dropna(inplace=True)
        beta = ((np.cov(df['fund_pct_chg'], df['pct_chg']))[0][1]/np.var(df['pct_chg']))
        sharp = (annualized_return-rf)/volatility
        
        print('\nfund analysis:')
        print(f'total percentage change: {end_fund/start_fund}, start fund: {start_fund}, end fund: {end_fund}, highest point: {max(fund_history["fund"])}, lowest point: {min(fund_history["fund"])}')
        print(f'annualized return: {annualized_return}, benchmark annualized return:{benchmark_returns}, volatility:{volatility}, sharpe ratio:{sharp}')

        data = list(self._standard.pop('close'))
        data.reverse()
        data = [int(i*(start_fund/data[0])) for i in data]
        benchmark = pd.DataFrame(data, columns = ['benchmark'])
        fund_history.insert(2, 'benchmark', benchmark)
        fund_history.drop(['fund_pct_chg'],axis=1, inplace=True)
        fund_history.plot(kind = 'line')
        plt.show()

    