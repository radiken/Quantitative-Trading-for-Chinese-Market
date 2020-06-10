import tushare as ts
import json
import datetime
from tqdm import tqdm

def init_trade_cal():
    pro = ts.pro_api()
    trade_cal = pro.trade_cal()
    open_day = trade_cal[trade_cal.is_open == 1]
    cal = list(open_day['cal_date'])
    print(cal[-1])
    with open('../data/trade_cal.json', 'w') as trade_cal:
        json.dump(cal, trade_cal)

def init_suspend_info():
    # takes a long time
    pro = ts.pro_api()
    with open('../data/trade_cal.json') as json_file:
        trade_cal = json.load(json_file)
    save_dict = {}
    for trade_date in tqdm(trade_cal):
        df = pro.query('suspend', ts_code='', suspend_date=trade_date, resume_date='', fields='ts_code')
        if len(df) != 0:
            stock_list = list(df['ts_code'])
            save_dict[trade_date] = stock_list
    with open('../data/suspend.json', 'w') as json_file:
        json.dump(save_dict, json_file)

def init_stock_list():
    pro = ts.pro_api()
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
    stock_list = list(data['ts_code'])
    with open('../data/stock_list.json', 'w') as json_file:
        json.dump(stock_list, json_file)

def update_suspend_info():
    today = str(datetime.date.today()).replace("-", "")
    pro = ts.pro_api()
    cal = pro.trade_cal(start_date=today, end_date=today, fields='is_open, pretrade_date').loc[0]
    date = today if cal['is_open']==1 else cal['pretrade_date']
    with open('../data/suspend.json') as json_file:
        suspend_info = json.load(json_file)
    with open('../data/trade_cal.json') as json_file:
        trade_cal = json.load(json_file)

    update_range = trade_cal[trade_cal.index(list(suspend_info.keys())[-1])+1:trade_cal.index(date)+1]
    for trade_date in update_range:
        print("getting %s" %trade_date)
        try:
            df = pro.query('suspend', ts_code='', suspend_date=trade_date, resume_date='', fields='ts_code')
        except:
            df = pro.query('suspend', ts_code='', suspend_date=trade_date, resume_date='', fields='ts_code')
        stock_list = list(df['ts_code'])
        suspend_info[trade_date] = stock_list
    with open('../data/suspend.json', 'w') as json_file:
        json.dump(suspend_info, json_file)

def save_standard_data(start_date, end_date):
    pro = ts.pro_api()
    standard = pro.index_daily(ts_code='000001.SH', start_date = start_date, end_date = end_date)
    standard.to_json('../data/standard_daily.json')

def save_stock_data(stock, start_date, end_date):
    # does not take care of directory creating
    pro = ts.pro_api()
    daily = pro.daily(ts_code=stock, start_date = start_date, end_date = end_date)
    daily.to_json(f'../data/{stock}/daily.json')

    ex_date = pro.dividend(ts_code=stock, fields='ex_date, stk_div')
    ex_date.to_json(f'../data/{stock}/ex_date.json')

    qfq_daily = ts.pro_bar(stock, adj='qfq', start_date=start_date, end_date=end_date)
    qfq_daily.to_json(f'../data/{stock}/qfq_daily.json')

    daily_basic = pro.daily_basic(ts_code=stock, start_date=start_date, end_date=end_date, fields='ts_code,trade_date,close,turnover_rate_f,volume_ratio')
    daily_basic.to_json(f'../data/{stock}/daily_basic.json')

    moneyflow = pro.moneyflow(ts_code=stock, start_date=start_date, end_date=end_date)
    moneyflow.to_json(f'../data/{stock}/moneyflow.json')


if __name__ == '__main__':
    init_trade_cal()
    init_suspend_info()
    init_stock_list()
    save_standard_data('20100101', '20200101')

    