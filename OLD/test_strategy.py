from backtesting import Backtest
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.lib import SignalStrategy, TrailingStrategy
import talib

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 25

    def init(self):
        # Calculate the indicators we want to use later (they will be stored in an array)
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.sar = talib.SAR(self.data.High, self.data.Low, acceleration=0.02, maximum=0.2)
        self.rsi = talib.RSI(self.data.Close)
        self.index = 0

    def next(self):
        # this is where we will be able to test our strategy, for every entry of the array (every row), we can execute some test
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        self.index+=1
        score = 0
        # we skip the first entries to prepare our indicators
        if self.index < 1000:
            return

        score += SmaCross.spotSarInversion(current_sar=self.sar[self.index], current_data_close=self.data.Close[self.index], previous_sar=self.sar[self.index-5], previous_data_close=self.data.Close[self.index-5])
        score += SmaCross.spotRsiExceed(current_rsi=self.rsi[self.index])

        if score == 2:
            self.position.close()
            self.buy()

        elif score == -2:
            self.position.close()
            self.sell()


if __name__ == '__main__':
    data = pd.read_csv("data.csv")
    bt = Backtest(data, SmaCross, cash=10_000, commission=.002)
    stats = bt.run()
    # stats = bt.optimize(n1=range(5, 30, 5),
    #                 n2=range(10, 70, 5),
    #                 maximize='Equity Final [$]',
    #                 constraint=lambda param: param.n1 < param.n2)
    print(stats)
    print(bt.plot())