import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule


class getData():
    def connect(self, account_id: int):
        """connect to the specific MT5 account

        Args:
            account_id (int):the MT5 account you want to connect to
        """
        mt5.initialize()
        authorized=mt5.login(account_id)

        if authorized:
            print("Connected: Connecting to MT5 Client")
        else:
            print("Failed to connect at account #{}, error code: {}".format(account_id, mt5.last_error()))

    def get_data(self, time_frame: int, begin: datetime, end: datetime, pairs: dict):
        """fetch data to a given time_frame

        Args:
            time_frame (int): the required time frame
            begin (datetime): The begin of the data to fetch
            end (datetime): the end of the data to fetch
            pairs (dict): the different pair you want to trade

        Returns:
            dict: the data for all needed pairs
        """
        # TODO: the array shouldn't be hard-coded and be passed as parameter
        pair_data = dict()
        for pair in pairs:
            rates = mt5.copy_rates_range(pair, time_frame, begin, end)
            rates_frame = pd.DataFrame(rates)
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
            rates_frame.drop(rates_frame.tail(1).index, inplace = True)
            pair_data[pair] = rates_frame
        return pair_data

    def prepare_data_backtesting(self, pair_data: pd.DataFrame, pair: str):
        """Prepare the data for the backtesting operations

        Args:
            pair_data (pd.DataFrame): the dataframe to save
            pair (str): the pair to select
        """
        df = pair_data[pair]
        df.drop(columns=["time", "tick_volume", "spread"], inplace=True)
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'real_volume': 'Volume'}, inplace=True)
        return df

    def save_data_csv(self, pair_data: pd.DataFrame, pair: str, path: str = 'data.csv'):
        """save the specific pair in a data frame into a .csv file

        Args:
            pair_data (pd.DataFrame): the dataframe to save
            pair (str): the pair to select
            path (str, optional): the path of the file to save. Defaults to 'data.csv'.
        """
        df = self.prepare_data_backtesting(pair_data=pair_data, pair=pair)
        df.to_csv("data/data.csv", index=False)

