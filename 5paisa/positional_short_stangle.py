import pandas as pd
from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange
import time
import math
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=FutureWarning)
cred = {
    "APP_NAME": "5P56409084",
    "APP_SOURCE": "9217",
    "USER_ID": "pybeQPEbjju",
    "PASSWORD": "AESDZQGqyAa",
    "USER_KEY": "542GTEZguBbLERUXRZe26rLvfWU2X2KD",
    "ENCRYPTION_KEY": "l8sRTIsjl1JhUrz8X48XQJzKGI4k0gft",
}
client = FivePaisaClient(
    email="vasuappliedai@gmail.com", passwd="Vasudeva@1", dob="19981218", cred=cred
)
client.login()
given_date = datetime.today().strftime("%Y-%m-%d")
indices = script_df.index[script_df["FullName"].str.contains(
    pat=bank_nifty_symbol + " CE", regex=True) == True].tolist()


script_df = pd.read_csv("scripmaster-csv-format.csv")
symbol = "BANKNIFTY 24 Mar 2022"


def get_current_expiry_strikes(symbol, start_strike, end_strike):
    temp_df = script_df["FullName"].str.contains(
        pat=symbol + " CE", regex=True)
    call_df = script_df[temp_df]
    call_df = call_df[call_df["StrikeRate"] > start_strike]
    call_df = call_df[call_df["StrikeRate"] < end_strike]
    call_df.to_csv("bank_nifty_call_expiry" + symbol + ".csv")
    temp_df = script_df["FullName"].str.contains(
        pat=symbol + " PE", regex=True)
    put_df = script_df[temp_df]
    put_df = put_df[put_df["StrikeRate"] > start_strike]
    put_df = put_df[put_df["StrikeRate"] < end_strike]
    put_df.to_csv("bank_nifty_put_expiry" + symbol + ".csv")
    return call_df, put_df


def map_prices_to_strike_prices(data_frame):
    temp_rows = []
    for _, row in data_frame.iterrows():
        script_code = row["Scripcode"]
        try:
            close_point = client.historical_data(
                "N", "D", script_code, "5m", given_date, given_date
            ).tail(1)
            temp_rows.append(close_point["Close"].iloc[0])
        except:
            continue
    data_frame["LTP"] = temp_rows
    return data_frame


# call_df, put_df = get_current_expiry_strikes(symbol, 34000, 38000)
