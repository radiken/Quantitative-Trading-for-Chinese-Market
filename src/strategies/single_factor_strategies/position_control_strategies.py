import tushare as ts
sys.path.append("..") 
from calculation import *

'''
position control strategies are more flexible then other strategies, many information can be considered, therefore each strategy has
be solely responsible for there required information 
'''

class example_position_control_strategy:
    def __init__(self):
        self._pro = ts.pro_api()
        self._data = {}

    def get_data(self, start_date, end_date):
        self._data['daily'] = self._pro.index_daily(ts_code='399300.SZ', start_date=start_date, end_date=end_date)

    def run(self, date):
        today_info = get_rows_from_df_by_date(self._data['daily'], date, date)
        if len(today_info != 1):
            #exception checking
            return 100
        else:
            pct_chg = today_info['pct_chg'].iloc[0]
            open_price = today_info['open'].iloc[0]
            highest_price = today_info['high'].iloc[0]
            if (pct_chg < -1) or (open_price == highest_price):
                return 50
            else:
                return 100