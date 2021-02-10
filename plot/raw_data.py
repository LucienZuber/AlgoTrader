import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import mplfinance as mpf
import pandas as pd
from indicators.support_resistance import detect_support_resistances


def displayRawData(df: pd.DataFrame):
    df.index = pd.to_datetime(df.index)
    mpf.plot(df, type='candle')


def displaySupportResistance(df: pd.DataFrame):
    result = detect_support_resistances(df=df, precision=2)
    df.index = pd.to_datetime(df.index)

    supports_plot = mpf.make_addplot(result, type='scatter', markersize=200, marker='_')

    mpf.plot(df, type='candle', addplot=supports_plot)
