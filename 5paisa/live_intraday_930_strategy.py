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

# cred = {
#     "APP_NAME": "5P57752064",
#     "APP_SOURCE": "9322",
#     "USER_ID": "5eRLuL81EDc",
#     "PASSWORD": "mUG0xZduuO5",
#     "USER_KEY": "BkVgrzXhLIUJbSYqqGIxNpyXcTtpSh0s",
#     "ENCRYPTION_KEY": "pecRHVbBoroAavcjObdA6ITkK0ZmhSjq",
# }
# client = FivePaisaClient(
#     email="chanderg16@gmail.com", passwd="5321@rvsA", dob="19720316", cred=cred
# )
# client.login()

script_df = pd.read_csv("scripmaster-csv-format.csv")

nifty_script_code = 999920000
banknifty_script_code = 999920005
given_date = datetime.today().strftime("%Y-%m-%d")
strikePrice = client.historical_data("N", "C", banknifty_script_code, "1m", given_date, given_date)[
    "Open"
].loc[15]
strikePrice = round(strikePrice / 1000, 1) * 1000
print("Banknifty at 9:30am ", strikePrice)
expiry = "20220324"
symbol = "BANKNIFTY 24 Mar 2022"
call_symbol = symbol + " CE " + strikePrice.__str__() + "0"
put_symbol = symbol + " PE " + strikePrice.__str__() + "0"
call_script_code = script_df[script_df["FullName"]
                             == call_symbol].iloc[0]["Scripcode"].__int__()
put_script_code = script_df[script_df["FullName"]
                            == put_symbol].iloc[0]["Scripcode"].__int__()
call_script_code, put_script_code

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


def get_order_id(broker_order_id):
    order_book = client.order_book()
    for order in order_book:
        if(order["BrokerOrderId"] == broker_order_id):
            return order
    return None


def get_pending_order_by_script(script_code):
    order_book = client.order_book()
    for order in order_book:
        if(order["PendingQty"] > 0 and order["ScripCode"] == script_code and order["OrderStatus"] != "Cancelled"):
            return order
    return None


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
    order_broker_id = client.bo_order(test_order)["BrokerOrderIDNormal"]
    time.sleep(5)
    return get_order_id(order_broker_id)


def modify_sl_co_bo(script_code, quantity, stop_loss, exchange_id):
    test_order = test_order = Order(
        order_type="B",
        scrip_code=script_code,
        quantity=quantity,
        price=0,
        is_intraday=True,
        exchange="N",
        exchange_segment="D",
        exch_order_id=exchange_id,
        stoploss_price=stop_loss,
        is_stoploss_order=True,
    )
    return client.modify_order(test_order)


def get_last_traded_prices():
    market_data = client.fetch_market_feed([req_list[0]])["Data"]
    call_ltp = market_data[0]["LastRate"]
    market_data = client.fetch_market_feed([req_list[1]])["Data"]
    put_ltp = market_data[0]["LastRate"]
    return call_ltp, put_ltp


def get_requested_ltp():
    market_data = client.fetch_market_feed(req_list)["Data"]
    return math.floor(market_data[0]["LastRate"])


def if_order_executed(exchange_id):
    order_book = client.order_book()
    for order in order_book:
        if(order["ExchOrderID"] == exchange_id and order["OrderStatus"] == "Fully Executed"):
            return True
    return False


def wait_for_order_execution():
    while_flag = True
    while while_flag:
        if if_order_executed(call_order_id):
            return call_script_code
        elif if_order_executed(put_order_id):
            return put_script_code
        else:
            time.sleep(60)


def wait_for_exit(script_code, order_id):
    while(if_order_executed(order_id) == False):
        df = client.historical_data(
            'N', 'D', script_code, '1m', given_date, given_date).tail(1)
        low_price = df["Low"].iloc[0]
        if low_price < new_stop_loss:
            new_stop_loss = low_price*1.2
            modify_sl_co_bo(script_code, 25, new_stop_loss, order_id)
        time.sleep(60)


call_entry, put_entry = get_last_traded_prices()
call_stoploss, put_stoploss = call_entry*1.2, put_entry*1.2

print("Put Entry and Stoploss ", put_entry, put_stoploss)
print("Call Entry and Stoploss ", call_entry, call_stoploss)

call_order_id = place_co_bo("S", call_script_code,
                            25, call_entry, call_stoploss)["ExchOrderID"]
put_order_id = place_co_bo("S", put_script_code, 25,
                           put_entry, put_stoploss)["ExchOrderID"]

while(if_order_executed(call_order_id) == False):
    time.sleep(5)
while(if_order_executed(put_order_id) == False):
    time.sleep(5)

call_order_id = get_pending_order_by_script(call_script_code)["ExchOrderID"]
put_order_id = get_pending_order_by_script(put_script_code)["ExchOrderID"]


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

new_stop_loss = math.ceil(get_requested_ltp()*1.2)
print("LTP & New Stoploss ", new_stop_loss*0.75, new_stop_loss)

wait_for_exit(script_code, order_id)
