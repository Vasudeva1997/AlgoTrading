import pandas as pd
# from py5paisa import FivePaisaClient
# from py5paisa.order import Order, OrderType, Exchange, bo_co_order
# import time
# import math
# import warnings
# from datetime import datetime

# warnings.filterwarnings("ignore", category=FutureWarning)
# cred = {
#     "APP_NAME": "5P56409084",
#     "APP_SOURCE": "9217",
#     "USER_ID": "pybeQPEbjju",
#     "PASSWORD": "AESDZQGqyAa",
#     "USER_KEY": "542GTEZguBbLERUXRZe26rLvfWU2X2KD",
#     "ENCRYPTION_KEY": "R4adCPfgGq8HuTbru8WnpKzzTVHWhvWI",
# }
# client = FivePaisaClient(
#     email="vasuappliedai@gmail.com", passwd="Vasudeva@2", dob="19981218", cred=cred
# )
# client.login()
script_df = pd.read_csv("scripmaster-csv-format.csv")
symbol = "BANKNIFTY 24 Mar 2022"


def get_current_expiry_strikes(symbol):
    temp_df = script_df["FullName"].str.contains(pat=symbol+" CE", regex=True)
    call_df = script_df[temp_df]
    call_df.to_csv("bank_nifty_call_expiry"+symbol+".csv")
    temp_df = script_df["FullName"].str.contains(pat=symbol+" PE", regex=True)
    put_df = script_df[temp_df]
    put_df.to_csv("bank_nifty_put_expiry"+symbol+".csv")
    return call_df, put_df


def map_prices_to_df():
    pass


call_df, put_df = get_current_expiry_strikes(symbol)
print(call_df)
