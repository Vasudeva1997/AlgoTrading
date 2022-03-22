from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange, Bo_co_order
import time
import math
import pandas as pd
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
script_df = pd.read_csv("scripmaster-csv-format.csv")
"""
9:30 AM strategy starts here
"""
nifty_script_code = 999920000
banknifty_script_code = 999920005
given_date = datetime.today().strftime("%Y-%m-%d")
strikePrice = client.historical_data("N", "C", banknifty_script_code, "1m", given_date, given_date)[
    "Open"
].loc[15]
strikePrice = round(strikePrice / 1000, 1) * 1000
print("Banknifty at 10:30am ", strikePrice)
expiry = "20220324"
symbol = "BANKNIFTY 24 Mar 2022"
call_symbol = symbol + " CE " + strikePrice.__str__() + "0"
put_symbol = symbol + " PE " + strikePrice.__str__() + "0"
call_script_code = script_df[script_df["FullName"]
                             == call_symbol].iloc[0]["Scripcode"].__int__()
put_script_code = script_df[script_df["FullName"]
                            == put_symbol].iloc[0]["Scripcode"].__int__()
req_list = [
    {
        "Exch": "N",
        "ExchType": "D",
        "Symbol": call_symbol,
        "Expiry": expiry,
        "StrikePrice": strikePrice,
        "OptionType": "CE",
    },
    {
        "Exch": "N",
        "ExchType": "D",
        "Symbol": put_symbol,
        "Expiry": expiry,
        "StrikePrice": strikePrice,
        "OptionType": "PE",
    },
]


def place_co_bo(order_type, script_code, quantity, price, stop_loss):
    test_order = Bo_co_order(
        script_code,
        quantity,
        price,
        0,
        0,
        order_type,
        "N",
        "D",
        "p",
        stop_loss + 0.5,
        stop_loss,
    )
    return client.bo_order(test_order)


def modify_order(order_type, script_code, quantity, price, order_id):
    modify_order = Order(
        order_type="B",
        quantity=25,
        exchange="N",
        exchange_segment="D",
        price=new_stop_loss,
        is_intraday=True,
        exch_order_id=order_id,
    )
    return client.modify_order(modify_order)


def get_last_traded_prices():
    market_data = client.fetch_market_feed([req_list[0]])["Data"]
    call_ltp = market_data[0]["LastRate"]
    market_data = client.fetch_market_feed([req_list[1]])["Data"]
    put_ltp = market_data[0]["LastRate"]
    return call_ltp, put_ltp


def get_requested_ltp():
    market_data = client.fetch_market_feed(req_list)["Data"]
    return market_data[0]["LastRate"]


def wait_for_order_execution():
    while_flag = True
    while while_flag:
        call_ltp, put_ltp = get_last_traded_prices()
        if call_ltp >= call_stoploss:
            # Check if call_order_id has triggered
            while_flag = False
            return call_script_code
        elif put_ltp >= put_stoploss:
           # Check if put_order_id has triggered
            while_flag = False
            return put_script_code
        else:
            time.sleep(60)


call_entry, call_stoploss = entry_stoploss(call_script_code, given_date)
put_entry, put_stoploss = entry_stoploss(put_script_code, given_date)


# place_order("S", 53435, 25, 500, 600)
# cover order
call_order_id = place_co_bo("S", call_script_code,
                            25, call_entry, call_stoploss)["ExchOrderID"]
put_order_id = place_co_bo("S", put_script_code, 25,
                           put_entry, put_stoploss)["ExchOrderID"]

print("Put Entry and Stoploss ", put_entry, put_stoploss)
print("Call Entry and Stoploss ", call_entry, call_stoploss)
print("Call Order ID and PUT Order ID ", call_order_id, put_order_id)

sl_hit_script = wait_for_order_execution()

order_id = None
script_code = None
req_list = None
if sl_hit_script == call_script_code:
    script_code = put_script_code
    order_id = put_order_id
    req_list = [{
        "Exch": "N",
        "ExchType": "D",
        "Symbol": put_symbol,
        "Expiry": expiry,
        "StrikePrice": strikePrice,
        "OptionType": "PE",
    }]
if sl_hit_script == put_script_code:
    script_code = call_script_code
    order_id = call_order_id
    req_list = [{
        "Exch": "N",
        "ExchType": "D",
        "Symbol": call_symbol,
        "Expiry": expiry,
        "StrikePrice": strikePrice,
        "OptionType": "CE",
    }]
