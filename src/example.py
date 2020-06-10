import tushare as ts

ts.set_token('your token')


from loop_back import loop_back
from strategys.strategy import strategy
from strategys.single_factor_strategys.stock_selection_strategys import example_stock_selection_strategy, second_example_stock_selection_strategy
from strategys.single_factor_strategys.buy_strategys import example_buy_strategy
from strategys.single_factor_strategys.sell_strategys import example_sell_strategy

start_date = '20190101'
end_date = '20200101'

stock_selection_strategy1 = example_stock_selection_strategy()
stock_selection_strategy2 = second_example_stock_selection_strategy()
buy_strategy = example_buy_strategy()
sell_strategy = example_sell_strategy()

my_strategy = strategy(start_date, end_date, [stock_selection_strategy1, stock_selection_strategy2], [buy_strategy], [sell_strategy])
loop = loop_back(strategy=my_strategy, frequency=1, fund=50000, start_date=start_date, end_date=end_date, exchange_fee=0.0003)
loop.run()