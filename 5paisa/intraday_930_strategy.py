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
].loc[13]
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


def place_co_bo(order_type, script_code, quantity, price, stop_loss):
    if order_type == "B" or order_type == "S":
        return {"ExchOrderID": "12333"}
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


def modify_sl_co_bo(order_type, script_code, quantity, stop_loss, exchange_id):
    if order_type == "B" or order_type == "S":
        return {"ExchOrderID": "12333"}
    test_order = Order(
        order_type=order_type,
        scrip_code=script_code,
        quantity=quantity,
        price=0,
        is_intraday=True,
        exchange="N",
        exchange_segment="D",
        atmarket=True,
        exch_order_id=exchange_id,
        stoploss_price=stop_loss,
        is_stoploss_order=True,
        order_for="M",
    )
    return client.mod_bo_order(test_order)


def place_order(order_type, script_code, quantity, price, stop_loss):
    if order_type == "B" or order_type == "S":
        return {"ExchOrderID": "12333"}
    test_order = Order(
        order_type=order_type,
        exchange="N",
        exchange_segment="D",
        scrip_code=script_code,
        quantity=quantity,
        price=price,
        is_intraday=True,
        stoploss_price=stop_loss,
        is_stoploss_order=True,
    )
    return client.place_order(test_order)


def modify_order(order_type, script_code, quantity, price, order_id):
    if order_type == "B" or order_type == "S":
        return {"ExchOrderID": "12333"}
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


def get_current_price():
    while True:
        market_data = client.fetch_market_feed(req_list_)["Data"]
        print(market_data)
        call_price = market_data[0]["LastRate"]
        put_price = market_data[1]["LastRate"]
        print(call_price)
        print(put_price)
        print(client.margin()[0]["AvailableMargin"])
        print("\n\n\n================================\n\n\n")
        time.sleep(5)


def get_last_traded_prices():
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

    market_data = client.fetch_market_feed([req_list[0]])["Data"]
    call_ltp = market_data[0]["LastRate"]
    market_data = client.fetch_market_feed([req_list[1]])["Data"]
    put_ltp = market_data[0]["LastRate"]
    return call_ltp, put_ltp


def entry_stoploss(script_code: int, date):
    df = client.historical_data("N", "D", script_code, "5m", date, date)
    entry_price = df.loc[3]["Open"]
    stop_loss = entry_price * 1.2
    return (math.ceil(entry_price), math.ceil(stop_loss))


def get_stoploss_time(script_code, date, stop_loss):
    df = client.historical_data(
        "N", "D", script_code, "1m", date, date).iloc[15:]
    # print(df[df["Datetime"] == "2022-03-15T09:49:00"])
    temp_df = df[df["High"] >= stop_loss]
    stop_loss_time = None
    if len(temp_df) > 0:
        stop_loss_time = temp_df.iloc[0]["Datetime"]
    return stop_loss_time


def get_dataframe_date(df, given_date):
    final_df = pd.DataFrame()
    for index in range(len(df)):
        temp_df = df.iloc[index]
        if temp_df["Datetime"].__contains__(given_date):
            final_df = final_df.append(temp_df)
    return final_df


def new_entry_stoploss(script_code, date, stop_loss_time):
    df = client.historical_data(
        "N", "D", script_code, "1m", date, date).loc[15:]
    new_entry_index = df.index[df["Datetime"] == stop_loss_time][0]
    new_entry_point = df.loc[new_entry_index]["Close"]
    new_stop_loss = math.ceil(new_entry_point * 1.2)
    print("Current Price Vs New stop loss at ", new_entry_point, new_stop_loss)
    # print(modify_order("B", trailing_script_code, 25, new_stop_loss, order_id))
    modify_sl_co_bo("B", trailing_script_code, 25, new_stop_loss, order_id)
    # screen_dataframe = get_dataframe_date(df, given_date)
    # If Test after market uncomment below
    # screen_dataframe = screen_dataframe[new_entry_index:-30]
    screen_dataframe = df[new_entry_index:]
    return screen_dataframe, new_stop_loss


def get_exit_points(screen_dataframe, new_stop_loss):
    buy_point = -1
    for index in range(len(screen_dataframe)):
        temp_df = screen_dataframe.iloc[index]
        temp_high_point = temp_df["High"]
        temp_low_point = temp_df["Low"]
        if temp_high_point > new_stop_loss:
            buy_point = temp_high_point
            print("Exited att ", new_stop_loss)
            print("Exited dff\n", temp_df)
            break
        elif temp_low_point < new_stop_loss * 0.75:
            new_stop_loss = math.ceil(temp_low_point * 1.2)
            # print(modify_order("B", trailing_script_code,
            #       25, new_stop_loss, order_id))
            print(
                "Updated stoploss & Current Price & Time ",
                new_stop_loss,
                temp_low_point,
                temp_df["Datetime"],
            )
    if buy_point == -1:
        print("Exited at ", new_stop_loss)
        print("Exited dff \n", screen_dataframe.tail(1))


def wait_for_order_execution(brokerId):
    while_flag = True
    while while_flag:
        call_ltp, put_ltp = get_last_traded_prices()
        if call_ltp == call_stoploss:
            print("call stop loss hit")
            while_flag = False
        elif put_ltp == put_stoploss:
            print("put stop loss hit")
            while_flag = False
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
# Normal Order
# call_order_id = place_order("S", call_script_code, 25, call_entry,
#                             call_stoploss)["ExchOrderID"]
# put_order_id = place_order("S", put_script_code, 25, put_entry,
#                            put_stoploss)["ExchOrderID"]
print("Put Entry and Stoploss ", put_entry, put_stoploss)
print("Call Entry and Stoploss ", call_entry, call_stoploss)
print("Call Order ID and PUT Order ID ", call_order_id, put_order_id)

put_stop_loss_time = get_stoploss_time(
    put_script_code, given_date, put_stoploss)
print("Stoploss hit time at PUT ", put_stop_loss_time)
call_stop_loss_time = get_stoploss_time(
    call_script_code, given_date, call_stoploss)
print("Stoploss hit time at CALL ", call_stop_loss_time)

stop_loss_time = None
trailing_script_code = None
order_id = None
if put_stop_loss_time is not None:
    stop_loss_time = put_stop_loss_time
    trailing_script_code = call_script_code
    order_id = call_order_id
if call_stop_loss_time is not None:
    stop_loss_time = call_stop_loss_time
    trailing_script_code = put_script_code
    order_id = put_order_id

screen_dataframe, new_stop_loss = (None, None)
if stop_loss_time is not None:
    screen_dataframe, new_stop_loss = new_entry_stoploss(
        trailing_script_code,
        given_date,
        stop_loss_time,
    )
    get_exit_points(screen_dataframe, new_stop_loss)

"""
9:30 AM strategy ends here
"""
