from strategys.single_factor_strategys.single_factor_trade_strategy import single_factor_sell_strategy
import tushare as ts
import sys
sys.path.append("..") 
from calculation import *

class example_sell_strategy(single_factor_sell_strategy):
    def make_decision(self, date, stock, holding_amount, cost, buy_date, info):
        daily_info = info['daily']
        newest_price = daily_info['close'].iloc[0]
        if newest_price/cost >= 1.05:
            # reached target profit
            return True, newest_price, holding_amount
        elif newest_price/cost <= 0.95:
            # stop loss
            return True, newest_price, holding_amount
        else:
            return False, 0, 0
