import tushare as ts
import json
from info_holder import info_holder
from calculation import *


MINIMUN_TRADE_AMOUNT = 3000

class strategy:
    def __init__(self, start_date, end_date, position_control_strategy, stock_selection_strategies, buy_strategies, sell_strategies, exchange_fee=0.0003):
        self._position_control_strategy = position_control_strategy
        self._stock_selection_strategies = stock_selection_strategies
        self._buy_strategies = buy_strategies
        self._sell_strategies = sell_strategies
        self._stocks_lasting_day = min(s.lasting_day for s in stock_selection_strategies)
        self._trace_day = max(max(s.trace_day for s in buy_strategies), max(s.trace_day for s in sell_strategies))
        self._start_date = get_trade_date_from_date(start_date, -self._trace_day)
        self._end_date = end_date
        self._info_holder = info_holder()
        self._exchange_fee = exchange_fee
        # use relative path, only correct when call by ../
        with open('data/suspend.json') as json_file:
            self._suspend_info = json.load(json_file)
        with open('data/stock_list.json') as json_file:
            self._all_stocks = json.load(json_file)
        

    def stock_selection(self, date):
        # needs stock pass all the requirement to be in the stock list
        # pass a list to each functions, at the end this function returns the final list
        stocks_left = self._all_stocks
        for strategy in self._stock_selection_strategies:
            stocks_left = strategy.run(stocks_left, date)
        self.prepare_data(date, stocks_left)
        return stocks_left

    def control_position(self, date):
        return self._position_control_strategy.run(date)

    def buy(self, date, stock_list, fund):
        # base on the date and the stock_list and available fund
        # return a dictionary of stocks:(price, amount) that is going to buy today
        # this strategy will decide to buy if any requirement is passed
        buy_dict = {}
        for stock in stock_list:
            if fund <= MINIMUN_TRADE_AMOUNT:
                break
            if date not in self._suspend_info:
                pro = ts.pro_api()
                df = pro.query('suspend', ts_code='', suspend_date=date, resume_date='', fields='ts_code')
                self._suspend_info[date] = list(df['ts_code'])
            if stock not in self._suspend_info[date]:
                for strategy in self._buy_strategies:
                    (decision, price, amount) = strategy.run(date, stock, fund)
                    if decision and amount != 0:
                        buy_dict[stock] = (price, amount)
                        trading_amount = price * amount
                        exchange_fee = calculate_buy_exchange_fee(trading_amount, self._exchange_fee)
                        fund -= (trading_amount + exchange_fee)
                        break
        return buy_dict
        

    def sell(self, date, holding_stocks):
        # base on the date and the stock_list
        # return a dictionary of stocks:amount that is going to sell today
        sell_dict = {}
        for index, row in holding_stocks.iterrows():
            if date not in self._suspend_info:
                pro = ts.pro_api()
                df = pro.query('suspend', ts_code='', suspend_date=date, resume_date='', fields='ts_code')
                self._suspend_info[date] = list(df['ts_code'])
            if (row['stock'] not in self._suspend_info[date]):
                for strategy in self._sell_strategies:
                    (decision, price, amount) = strategy.run(date, row['stock'], row['amount'], row['cost'], row['buy_date'])
                    if decision:
                        sell_dict[row['stock']] = (price, amount)
                        break
        return sell_dict

    def prepare_data(self, date, stocks):
        # prepare data for buy and sell strategies
        start_date = get_trade_date_from_date(date, -self._trace_day)
        self._info_holder.get_daily_info(stocks, start_date, self._end_date)
        self._info_holder.get_qfq_daily_info(stocks, start_date, self._end_date)
        self._info_holder.get_ex_date_info(stocks)
        for stock in stocks:
            for strategy in self._buy_strategies:
                strategy.get_data(stock)
            for strategy in self._sell_strategies:
                strategy.get_data(stock)

    def set_exchange_fee(self, exchange_fee):
        self._exchange_fee = exchange_fee

    @property
    def stock_selection_strategies(self):
        return self._stock_selection_strategies

    @property
    def buy_strategies(self):
        return self._buy_strategies

    @property
    def sell_strategies(self):
        return self._sell_strategies

    @property
    def stocks_lasting_day(self):
        return self._stocks_lasting_day
        

