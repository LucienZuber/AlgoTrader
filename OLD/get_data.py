import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule
import pytz
import talib as ta

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

    def open_position(self, pair: str, order_type: str, size: float, tp_distance: int = None, stop_distance: int = None, comment: str = ""):
        """Open a position on the connected current metatrader account

        Args:
            pair (str): The pair you want to exchange (EURUSD for instance)
            order_type (str): the type of order you want to place (BUY for instance)
            size (float): volume of the order
            tp_distance (int, optional): Number of pip before taking profit. Defaults to None.
            stop_distance (int, optional): Number of pip before stop loss. Defaults to None.
            comment (str, optional): A comment you want to put on your order. Defaults to empty
        """
        symbol_info = mt5.symbol_info(pair)
        if symbol_info is None:
            print(pair, "not found")
            return
        if not symbol_info.visible:
            print(pair, "is not visible, trying to switch on")
            if not mt5.symbol_select(pair, True):
                print("symbol_select({}}) failed, exit",pair)
                return
        print(pair, "found!")

        point = symbol_info.point

        if(order_type == "BUY"):
            order = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(pair).ask
            if(stop_distance):
                sl = price - (stop_distance * point)
            if(tp_distance):
                tp = price + (tp_distance * point)
        if(order_type == "SELL"):
            order = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(pair).bid
            if(stop_distance):
                sl = price + (stop_distance * point)
            if(tp_distance):
                tp = price - (tp_distance * point)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": size,
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }


        result = mt5.order_send(request)
        print(result)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to send order :(")
        else:
            print ("Order successfully placed!")

    def positions_get(self, symbol: str = None):
        """Return all your open positions corresponding to the pair you gave (all open positions by default)

        Args:
            symbol (str, optional): the specific pair you want to have positions from (leave empty if you want all your positions ).

        Returns:
            pd.DataFrame: A list of matching pairs
        """
        if symbol is None:
            positions = mt5.positions_get()
        else:
            positions = mt5.positions_get(symbol=symbol)

        print(positions)

        if(positions is not None and positions != ()):
            df = pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df

        return pd.DataFrame()

    def close_position(self, deal_id, comment: str = "Close trade"):
        """Close a given position (will just create an order agains one that is open)

        Args:
            deal_id (str): the idea of the position to close
            comment (str, optional): A comment you want to put on your order. Defaults to Close trade
        """
        open_positions = positions_get()
        open_positions = open_positions[open_positions['ticket'] == deal_id]
        order_type  = open_positions["type"][0]
        symbol = open_positions['symbol'][0]
        volume = open_positions['volume'][0]

        if(order_type == mt5.ORDER_TYPE_BUY):
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask

        close_request={
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "position": deal_id,
            "price": price,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to close order :(")
        else:
            print ("Order successfully closed!")

    def close_positions_by_symbol(self, symbol):
        """Close all positions related to a given symbol

        Args:
            symbol (str): the pair you want to close
        """
        open_positions = positions_get(symbol)
        open_positions['ticket'].apply(lambda x: close_position(deal_id=x, comment="Close all "+symbol+" trades"))

    def get_data(self, time_frame: int, begin: datetime, end: datetime):
        """fetch data to a given time_frame

        Args:
            time_frame (int): the required time frame
            begin (datetime): The begin of the data to fetch
            end (datetime): the end of the data to fetch

        Returns:
            dict: the data for all needed pairs
        """
        # TODO: the array shouldn't be hard-coded and be passed as parameter
        pairs = ['EURJPY']
        pair_data = dict()
        for pair in pairs:
            rates = mt5.copy_rates_range(pair, time_frame, begin, end)
            rates_frame = pd.DataFrame(rates)
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
            rates_frame.drop(rates_frame.tail(1).index, inplace = True)
            pair_data[pair] = rates_frame
        return pair_data

    def check_timedout_positions(self, data: pd.DataFrame):
        """Check if a positions is timedOut

        Args:
            data (pd.DataFrame): all positions linked to a pair
        """
        last_row = data.tail(1)
        open_positions = positions_get()
        current_dt = datetime.now().astimezone(pytz.timezone('Europe/Athens'))
        for index, position in open_positions.iterrows():
            # Check to see if the trade has exceeded the time limit
            trade_open_dt = position['time'].replace(tzinfo = pytz.timezone('Europe/Athens'))
            deal_id = position['ticket']
            if(current_dt - trade_open_dt >= timedelta(hours = 2)):
                close_position(deal_id)

    def check_trades(self, time_frame: int, pair_data: dict):
        """Check the pair data and the given time frame, if it works with the conditions, a thread will open

        Args:
            time_frame (int): the time frame in which you are trading
            pair_data (dict): the pair data you are working with
        """
        for pair, data in pair_data.items():
            check_timedout_positions(data=data)
            data['SMA'] = ta.SMA(data['close'], 10)
            data['EMA'] = ta.EMA(data['close'], 50)
            last_row = data.tail(1)
            open_positions = positions_get(pair)
            current_dt = datetime.now().astimezone(pytz.timezone('Europe/Athens'))

            for index, last in last_row.iterrows():
                # Entry strategy
                if(last['close'] > last['EMA'] and last['close'] < last['SMA']):
                    open_position(pair, "BUY", 1, 300, 100)

            for index, last in last_row.iterrows():
                # Exit strategy
                if(last['close'] < last['EMA'] and last['close'] > last['SMA']):
                    close_positions_by_symbol(symbol=pair)

    def run_trader(self, time_frame: int):
        """analyze market at given time and react depending on the needs

        Args:
            time_frame (int): the time frame you are trading
        """
        print("Running trader at", datetime.now())
        connect(account_id=ACCOUNT_ID)
        date_from = datetime(2021, 1, 1, tzinfo=pytz.timezone('Europe/Berlin'))
        date_to = datetime.now().astimezone(pytz.timezone('Europe/Berlin'))
        date_to = datetime(date_to.year, date_to.month, date_to.day, hour=date_to.hour, minute=date_to.minute)
        pair_data = get_data(time_frame=time_frame, begin = date_from, end = date_to)
        check_trades(time_frame=time_frame, pair_data=pair_data)

    def live_trading(self):
        """Start live trading
        """
        schedule.every().hour.at(":00").do(run_trader, mt5.TIMEFRAME_M15)
        schedule.every().hour.at(":15").do(run_trader, mt5.TIMEFRAME_M15)
        schedule.every().hour.at(":30").do(run_trader, mt5.TIMEFRAME_M15)
        schedule.every().hour.at(":45").do(run_trader, mt5.TIMEFRAME_M15)
        while True:
            schedule.run_pending()
            time.sleep(1)
