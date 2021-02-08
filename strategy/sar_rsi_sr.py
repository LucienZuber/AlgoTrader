from backtesting import Backtest
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.lib import SignalStrategy, TrailingStrategy
import talib
from indicators.rsi import spotRsiExceed
from indicators.sar import spotSarInversion

class SarRsiSr(Strategy):
    """A strategy where we will use Sar, Rsi and support/resistance level to enter or not trades
    """
    def init(self):
        """We generate the indicators for our strategy
        """
        # the SAR indicators calculated for the complete dataset
        self.sar = talib.SAR(self.data.High, self.data.Low, acceleration=0.02, maximum=0.2)

        # the RSI indicators calculated for the complete dataset
        self.rsi = talib.RSI(self.data.Close)

        # this will be used in the next method to keep a track of where we are
        self.index = 0

    def next(self):
        """Where the magic happen, it will iterate over each entry of the dataset and execute what is listed inside of this method (the strategy implementation)
        """
        # we skip the first entries to prepare our indicators
        if self.index < 1000:
            self.index+=1
            return

        # the score is used to calculate the awareness of the method
        score = 0

        # we check if during the last 6 entry, the SAR has been reversed, in this case we enter the trader
        score += spotSarInversion(current_sar=self.sar[self.index], current_data_close=self.data.Close[self.index], previous_sar=self.sar[self.index-5], previous_data_close=self.data.Close[self.index-5])

        # we check if we are currently on an RSI exceed situation
        score += spotRsiExceed(current_rsi=self.rsi[self.index])

        # if we have a score of 2, we are in a bullish situation and should buy
        if score >= 2:
            self.position.close()
            self.buy()

        # if we have a score of -2, we are in a bullish situation and should sell
        elif score <= -2:
            self.position.close()
            self.sell()

        # we increment the index by one before finishing the loop
        self.index+=1