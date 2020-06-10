import tushare as ts
from calculation import *
from info_holder import info_holder

class example_stock_selection_strategy:
    def __init__(self):
        self._pro = ts.pro_api()
        self._LASTING_DAY = 1

    def run(self, stocks_left, date):
        df = self._pro.hsgt_top10(trade_date=date)
        return list(df['ts_code'])

    @property
    def lasting_day(self):
        return self._LASTING_DAY


class second_example_stock_selection_strategy:
    def __init__(self):
        self._LASTING_DAY = 1

    def run(self, stocks_left, date):
        # exclude second board stock
        new_list = list(filter(lambda s: not s.startswith("300"), stocks_left))
        return new_list

    @property
    def lasting_day(self):
        return self._LASTING_DAY

