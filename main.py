from metatrader.get_data import getData
from strategy.monitor import run_strategy
from strategy.sar_rsi_sr import SarRsiSr
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pytz
from plot.raw_data import displayRawData, displaySupportResistance

ACCOUNT_ID = 30971759


if __name__ == '__main__':
    get_data = getData()
    # get_data.connect(account_id=ACCOUNT_ID)

    # print("Get data from MT5")
    # time_frame = mt5.TIMEFRAME_H1
    # date_from = datetime(2019, 3, 1, tzinfo=pytz.timezone('Europe/Berlin'))
    # date_to = datetime(2019, 3, 31, tzinfo=pytz.timezone('Europe/Berlin'))
    # pairs = ['EURJPY']
    # pair_data = get_data.get_data(time_frame=time_frame, begin = date_from, end = date_to, pairs = pairs)
    # get_data.save_data_csv(pair_data=pair_data, pair=pairs[0])
    # print("Prepare data for backtesting")
    # data = get_data.prepare_data_backtesting(pair_data=pair_data, pair=pairs[0])

    # print("Run backtesting")
    # run_strategy(strategy=SarRsiSr, data=data)
    # print("Backtesting complete, now exiting ...")

    df = get_data.read_data()
    # displayRawData(df)
    displaySupportResistance(df)
