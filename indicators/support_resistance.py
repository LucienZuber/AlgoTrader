import pandas as pd
import datetime

def detect_support_resistances(df: pd.DataFrame, initial_state: int = 20, precision: int = 3, expiration_time: datetime.timedelta = datetime.timedelta(days=7)):
    initial_min = df['Close'].iloc[:initial_state].idxmin()
    initial_max = df['Close'].iloc[:initial_state].idxmax()

    supports=pd.DataFrame({'Support': df['Close'].loc[initial_min]}, index=[initial_min])
    resistances=pd.DataFrame({'Resistance': df['Close'].loc[initial_max]}, index=[initial_max])

    expiration_support = initial_min + expiration_time
    expiration_resistance = initial_max + expiration_time

    for (index, close_price) in enumerate(df['Close'].iloc[initial_state:], initial_state):
        index_datetime = df.index[index]
        latest_min_index = df['Close'].iloc[index-precision:index].idxmin()
        latest_min_value = df['Close'].iloc[index-precision:index].min()
        latest_max_index = df['Close'].iloc[index-precision:index].idxmax()
        latest_max_value = df['Close'].iloc[index-precision:index].max()
        if (expiration_support <= index_datetime):
            supports.loc[latest_min_index] = latest_min_value
            expiration_support = latest_min_index + expiration_time

        elif (expiration_resistance <= index_datetime):
            resistances.loc[latest_max_index] =latest_max_value
            expiration_resistance = latest_min_index + expiration_time

        elif (latest_max_value < supports['Support'].iloc[-1]):
            supports.loc[latest_min_index] = latest_min_value
            expiration_support = latest_min_index + expiration_time

        elif (latest_min_value > resistances['Resistance'].iloc[-1]):
            resistances.loc[latest_max_index] = latest_max_value
            expiration_resistance = latest_min_index + expiration_time

    supports = supports.reindex(df.index.values)
    resistances = resistances.reindex(df.index.values)

    result = supports.join(resistances)

    return result