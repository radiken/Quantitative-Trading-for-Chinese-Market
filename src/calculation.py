from __future__ import division
import re
import json
import os
from pytz import timezone
import datetime

def buy_portion(fund, price, percentage):
    percentage /= 100
    can_buy = fund / price
    want = can_buy * percentage
    want = int(want - (want % 100))
    return want

def buy_around(fund, price, wanted):
    a_unit = price * 100
    units = round((wanted / a_unit), 0)
    if units == 0 and fund >= a_unit:
        units = 1
    while fund < units*a_unit:
        units -= 1
    return units*100

def sell_portion(holdingAmount, percentage):
    if holdingAmount == 100 and percentage > 0:
        return 100
    percentage /= 100
    sellAmount = holdingAmount * percentage
    sellAmount = int(sellAmount - (sellAmount % 100))
    return sellAmount

def calculate_average_price(oldPrice, oldAmount, newPrice, newAmount):
    if newPrice == 0:
        average = (oldPrice*oldAmount) / (oldAmount + newAmount)
    else:
        average = (oldPrice*oldAmount + newPrice*newAmount) / (oldAmount + newAmount)
    return average

def calculate_total_worth(holdingStocks, prices):
    worth = 0
    for stock in holdingStocks:
        worth += holdingStocks[stock] * prices[stock]
    return worth

def calculate_buy_exchange_fee(trading_amount, exchange_fee):
    return max(trading_amount * exchange_fee, 5)

def calculate_sell_exchange_fee(trading_amount, exchange_fee):
    return (max(trading_amount * exchange_fee, 5) + trading_amount*0.001 + max(trading_amount*0.00002, 1))
    
def get_rows_from_df_by_date(df, start_date, end_date):
    return df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]

def get_fixed_rows_before_date_from_df(df, start_date, number_of_rows):
    start_index = df.index[df['trade_date'] == start_date].tolist()[0]
    end_index = start_index + number_of_rows
    if end_index >= df.tail(1).index.values.astype(int)[0]:
        return df.tail(df.tail(1).index.values.astype(int)[0]-start_index+1)
    else:
        return df.loc[start_index:end_index]

def get_trade_date_from_date(date, days_from_date):
    script_dir = os.path.dirname(__file__) 
    rel_path = "data/trade_cal.json"
    data_path = os.path.join(script_dir, rel_path)
    with open(data_path) as trade_cal:
        data = json.load(trade_cal)
        while(date not in data):
            date = str(int(date) + 1)
        index = data.index(date)
        return data[index+days_from_date]

def get_trade_date_distance(from_date, to_date):
    script_dir = os.path.dirname(__file__) 
    rel_path = "data/trade_cal.json"
    data_path = os.path.join(script_dir, rel_path)
    with open(data_path) as trade_cal:
        data = json.load(trade_cal)
        while(from_date not in data):
            from_date = get_tomorrow_of_date(from_date)
        while(to_date not in data):
            to_date = get_tomorrow_of_date(to_date)
        distance = data.index(to_date) - data.index(from_date)
        return distance

def get_closest_trade_date(date, prev=False):
    script_dir = os.path.dirname(__file__) 
    rel_path = "data/trade_cal.json"
    data_path = os.path.join(script_dir, rel_path)
    with open(data_path) as trade_cal:
        data = json.load(trade_cal)
        if not prev:
            while(date not in data):
                date = get_tomorrow_of_date(date)
        else:
            while(date not in data):
                date = get_yesterday_of_date(date)
    return date

def get_Chinese_datetime():
    China = timezone('Asia/Shanghai')
    sa_time = datetime.datetime.now(China).strftime('%Y%m%d%H%M%S')
    return sa_time

def get_yesterday_date():
    China = timezone('Asia/Shanghai')
    sa_time = (datetime.datetime.now(China) - datetime.timedelta(1)).strftime('%Y%m%d')
    return sa_time

def is_limit_up(old_price, new_price):
    if new_price/old_price >= 1.099: return True 
    else: return False

def is_limit_down(old_price, new_price):
    if new_price/old_price <= 0.901: return True 
    else: return False

def get_yesterday_of_date(date):
    if(date[6:] != "01"):
        date = str(int(date) - 1)
    else:
        if(date[4:6] != "01"):
            # last month
            date = f"{date[:4]}{int(date[4:6])-1}31"
        else:
            # last year
            date = f"{int(date[:4])-1}1231"
    return date

def get_tomorrow_of_date(date):
    if(date[6:] != "31"):
        date = str(int(date) + 1)
    else:
        if(date[4:6] != "12"):
            # next month
            date = f"{date[:4]}{int(date[4:6])+1}01"
        else:
            # next year
            date = f"{int(date[:4])+1}0101"
    return date

def get_trade_cal(start_date, end_date):
    try:
        start_date = get_closest_trade_date(start_date)
        end_date = get_closest_trade_date(end_date, prev=True)
        script_dir = os.path.dirname(__file__) 
        rel_path = "data/trade_cal.json"
        data_path = os.path.join(script_dir, rel_path)
        with open(data_path) as trade_cal:
            data = json.load(trade_cal)
        if start_date == end_date:
            return [start_date]
        else:
            return data[data.index(start_date):data.index(end_date)]
    except:
        import tushare as ts
        pro = ts.pro_api()
        trade_cal = pro.trade_cal(start_date = start_date, end_date = end_date)
        open_day = trade_cal[trade_cal.is_open == 1]
        return list(open_day['cal_date'])