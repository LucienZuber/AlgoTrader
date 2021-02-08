from backtesting import Backtest
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.lib import SignalStrategy, TrailingStrategy
import talib

def run_strategy(strategy: Strategy, data: pd.DataFrame, cash:int = 10_000, commission: float = .002):
    """run the backtest for a specific strategy

    Args:
        strategy (Strategy): The strategy you want to execute
        path (pd.DataFrame): the data to backtest
        cash (int, optional): the entry cash you will have. Defaults to 10_000.
        commission (float, optional): the broker commision. Defaults to .002.
    """
    bt = Backtest(data, strategy, cash=10_000, commission=.002)
    stats = bt.run()

    print(stats)
    print(bt.plot())