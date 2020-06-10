import tushare as ts
import threading
import pandas as pd
from os import path
from calculation import *
import pymongo
from pymongo import MongoClient

def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton

@Singleton
class info_holder:
    def __init__(self):
        self._daily_info = {}
        self._ex_date_info = {}
        self._qfq_daily_info = {}
        self._moneyflow = {}
        self._pro = ts.pro_api()

    @staticmethod
    def get_standard_info(start_date, end_date):
        try:
            with open('data/standard_daily.json') as json_file:
                standard = pd.read_json(json_file)
            standard['trade_date'] = standard['trade_date'].astype(str)
            standard = get_rows_from_df_by_date(standard, start_date, end_date)
        except:
            pro = ts.pro_api()
            standard = pro.index_daily(ts_code='000001.SH', start_date = start_date, end_date = end_date)
        return standard

    def get_daily_news(self, date, news_type=None):
        start_date = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:]
        end_date = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:]
        df = self._pro.news(src='sina', start_date=start_date, end_date=end_date, fields="datetime, content, channels")
        if news_type is not None:
            filtered = pd.DataFrame()
            for index, row in df.iterrows():
                for channel in row.channels:
                    if channel['name'] == news_type:
                        filtered = filtered.append(row)
                        break
            return filtered
        else: 
            return df
        
    def get_daily_info(self, stocks, start_date, end_date):
        threads = []
        for stock in stocks:
            if path.exists(f'data/{stock}'):
                with open(f'data/{stock}/daily.json') as json_file:
                    daily = pd.read_json(json_file)
                daily['trade_date'] = daily['trade_date'].astype(str)
                daily = get_rows_from_df_by_date(daily, start_date, end_date)
                if len(daily) != 0:
                    self._daily_info[stock] = daily

            if stock not in self._daily_info:
                t = threading.Thread(target=self.get_single_stock_daily_info, args=(stock, start_date, end_date))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()
        return self._daily_info

    def get_qfq_daily_info(self, stocks, start_date, end_date):
        threads = []
        for stock in stocks:
            if path.exists(f'data/{stock}'):
                with open(f'data/{stock}/qfq_daily.json') as json_file:
                    qfq_daily = pd.read_json(json_file)
                qfq_daily['trade_date'] = qfq_daily['trade_date'].astype(str)
                qfq_daily = get_rows_from_df_by_date(qfq_daily, start_date, end_date)
                if len(qfq_daily) != 0:
                    self._qfq_daily_info[stock] = qfq_daily
                
            if stock not in self._qfq_daily_info:
                t = threading.Thread(target=self.get_single_stock_qfq_daily_info, args=(stock, start_date, end_date))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()
        return self._qfq_daily_info

    def get_ex_date_info(self, stocks):
        threads = []
        for stock in stocks:
            if path.exists(f'data/{stock}'):
                with open(f'data/{stock}/ex_date.json') as json_file:
                    ex_date = pd.read_json(json_file)
                ex_date['ex_date'] = ex_date['ex_date'].astype(str)
                self._ex_date_info[stock] = ex_date

            if stock not in self._ex_date_info:
                t = threading.Thread(target=self.get_single_stock_ex_date_info, args=(stock, ))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()
        return self.ex_date_info

    def get_moneyflow(self, stocks, start_date, end_date):
        threads = []
        for stock in stocks:
            if path.exists(f'data/{stock}'):
                with open(f'data/{stock}/moneyflow.json') as json_file:
                    moneyflow = pd.read_json(json_file)
                moneyflow['trade_date'] = moneyflow['trade_date'].astype(str)
                moneyflow = get_rows_from_df_by_date(moneyflow, start_date, end_date)
                if len(moneyflow) != 0:
                    self._moneyflow[stock] = moneyflow
                
            if stock not in self._moneyflow:
                t = threading.Thread(target=self.get_moneyflow, args=(stock, start_date, end_date))
                threads.append(t)
                t.start()
        for t in threads:
            t.join()
        return self._moneyflow

    def get_single_stock_daily_info(self, stock, start_date, end_date):
        self._daily_info[stock] = self._pro.daily(ts_code=stock, start_date=start_date, end_date=end_date)

    def get_single_stock_ex_date_info(self, stock):
        self._ex_date_info[stock] = self._pro.dividend(ts_code=stock, fields='record_date, ex_date, stk_div, cash_div')

    def get_single_stock_qfq_daily_info(self, stock, start_date, end_date):
        self._qfq_daily_info[stock] = ts.pro_bar(stock, adj='qfq', start_date=start_date, end_date=end_date)

    def get_single_stock_moneyflow(self, stock, start_date, end_date):
        self._moneyflow[stock] = self._pro.moneyflow(ts_code=stock, start_date=start_date, end_date=end_date)

    @property
    def daily_info(self):
        return self._daily_info

    @property
    def ex_date_info(self):
        return self._ex_date_info

    @property
    def qfq_daily_info(self):
        return self._qfq_daily_info

    @property
    def moneyflow(self):
        return self._moneyflow
