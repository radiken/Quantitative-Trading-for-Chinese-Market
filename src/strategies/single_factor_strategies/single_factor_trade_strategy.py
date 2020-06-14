import tushare as ts
import sys
import logging
sys.path.append("..") 
from calculation import *
from info_holder import info_holder

class single_factor_trade_strategy:
    def __init__(self):
        self._pro = ts.pro_api()
        self._info_holder = info_holder()
        self._TRACE_DAY = 0
        self._daily_info = {}
        self._ex_date_info = {}

    def get_data(self, stock):
        # rewrite if more data needed
        self._daily_info = self._info_holder.daily_info
        self._ex_date_info = self._info_holder.ex_date_info
        self._qfq_daily_info = self._info_holder.qfq_daily_info
            
    def is_checking_ex_date(self, stock, date):
        # is the date range inspecting in this strategy in ex_date
        start_date = get_trade_date_from_date(date, -self._TRACE_DAY)
        if start_date != date:
            date_range = get_trade_cal(start_date, date)
        else:
            date_range = [date]
        for date in date_range:
            if date in self._ex_date_info[stock].ex_date:
                return True
        return False

    def get_today_info(self, stock, date):
        info = {}
        if self.is_checking_ex_date(stock, date):
            info['daily'] = get_fixed_rows_before_date_from_df(self._qfq_daily_info[stock], date, self._TRACE_DAY)
        else:
            info['daily'] = get_fixed_rows_before_date_from_df(self._daily_info[stock], date, self._TRACE_DAY)
        return info

    @property
    def trace_day(self):
        return self._TRACE_DAY

class single_factor_buy_strategy(single_factor_trade_strategy):
    def run(self, date, stock, fund):
        try:
            info = self.get_today_info(stock, date)
        except:
            return (False, 0, 0)

        if buy_portion(fund, info['daily']['close'].iloc[0], 100) == 0:
            return False, 0, 0
        elif len(info['daily']) < self._TRACE_DAY+1:
            return False, 0, 0
        else:
            return self.make_decision(date, stock, fund, info)

    def make_decision(self, date, stock, fund, info):
        # override this
        logging.warning('Decision making in buy strategy has not been overridden!')
        return False, 0, 0

        
class single_factor_sell_strategy(single_factor_trade_strategy):
    def is_ex_date(self, stock, date):
        info = self._ex_date_info[stock][(self._ex_date_info[stock]['ex_date'] == date)]
        if(len(info) == 0):
            return 0
        elif(info['stk_div'] is None):
            return 0
        else:
            return info['stk_div'].tolist()[0]

    def run(self, date, stock, holding_amount, cost, buy_date):
        stk_div = self.is_ex_date(stock, date)
        if(stk_div != 0):
            # for now if it is the day then do not consider selling
            return True, -1, self.is_ex_date(stock, date)*holding_amount

        try:
            info = self.get_today_info(stock, date)
        except:
            logging.info(f"{stock} data empty on {date} for unknown error!")
            return (False, 0, 0)

        return self.make_decision(date, stock, holding_amount, cost, buy_date, info)

    def make_decision(self, date, stock, holding_amount, cost, buy_date, info):
        # override this
        logging.warning('Decision making in sell strategy has not been overridden!')
        return False, 0, 0


