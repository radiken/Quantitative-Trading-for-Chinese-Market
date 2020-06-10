from loop_back import loop_back
from strategies.strategy import strategy
from strategies.single_factor_strategies.stock_selection_strategies import example_stock_selection_strategy, second_example_stock_selection_strategy
from strategies.single_factor_strategies.buy_strategies import example_buy_strategy
from strategies.single_factor_strategies.sell_strategies import example_sell_strategy

start_date = '20190101'
end_date = '20200101'

stock_selection_strategy1 = example_stock_selection_strategy()
stock_selection_strategy2 = second_example_stock_selection_strategy()
buy_strategy = example_buy_strategy()
sell_strategy = example_sell_strategy()

my_strategy = strategy(start_date, end_date, [stock_selection_strategy1, stock_selection_strategy2], [buy_strategy], [sell_strategy])
loop = loop_back(strategy=my_strategy, frequency=1, fund=50000, start_date=start_date, end_date=end_date, exchange_fee=0.0003)
loop.run()