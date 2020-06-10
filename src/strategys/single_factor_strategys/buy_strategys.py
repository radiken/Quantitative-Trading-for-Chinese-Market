from strategys.single_factor_strategys.single_factor_trade_strategy import single_factor_buy_strategy
import tushare as ts
import sys
sys.path.append("..") 
from calculation import *

class example_buy_strategy(single_factor_buy_strategy):
    def make_decision(self, date, stock, fund, info):
        # if price went up today, order 50% tomorrow at the close price of today
        daily_info = info['daily']
        if daily_info['pct_chg'].iloc[0] > 0:
            return True, daily_info['close'].iloc[0], buy_portion(fund, daily_info['close'].iloc[0], 50)
        else:
            return False, 0, 0
