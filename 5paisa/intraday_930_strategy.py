from py5paisa import FivePaisaClient
import time
import pandas as pd
cred = {
    "APP_NAME": "5P56409084",
    "APP_SOURCE": "9217",
    "USER_ID": "pybeQPEbjju",
    "PASSWORD": "AESDZQGqyAa",
    "USER_KEY": "542GTEZguBbLERUXRZe26rLvfWU2X2KD",
    "ENCRYPTION_KEY": "R4adCPfgGq8HuTbru8WnpKzzTVHWhvWI"
}
client = FivePaisaClient(email="vasuappliedai@gmail.com",
                         passwd="Vasudeva@2", dob="19981218", cred=cred)
client.login()

'''
9:30 AM strategy starts here
'''
expiry = "20220317"
strikePrice = "35500"
symbol = "BANKNIFTY 17 MAR 2022"
call_symbol = symbol + " CE "+strikePrice + ".00"
put_symbol = symbol + " PE "+strikePrice + ".00"
call_script_code = 48140
put_script_code = 48141
given_date = "2022-03-15"

req_list_ = [{"Exch": "N", "ExchType": "D", "Symbol": call_symbol, "Expiry": expiry, "StrikePrice": strikePrice, "OptionType": "CE"},
             {"Exch": "N", "ExchType": "D", "Symbol": put_symbol, "Expiry": expiry, "StrikePrice": strikePrice, "OptionType": "PE"}]


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


def entry_stoploss(script_code: int, date):
    df = client.historical_data(
        'N', 'D', script_code, '5m', date, date)
    entry_price = df.loc[3]["Open"]
    stop_loss = entry_price*1.2
    return(entry_price, stop_loss)


def get_stoploss_time(script_code, date, stop_loss):
    df = client.historical_data('N', 'D', script_code, '1m',
                                date, date).iloc[15:]
    # print(df[df["Datetime"] == "2022-03-15T09:49:00"])
    temp_df = df[df["High"] >= stop_loss]
    stop_loss_time = None
    if(len(temp_df) > 0):
        stop_loss_time = temp_df.iloc[0]["Datetime"]
    return stop_loss_time


def get_dataframe_date(df, given_date):
    final_df = pd.DataFrame()
    for index in range(len(df)):
        temp_df = df.iloc[index]
        if(temp_df["Datetime"].__contains__(given_date)):
            final_df = final_df.append(temp_df)
    return final_df


def new_entry_stoploss(script_code, date, stop_loss_time):
    df = client.historical_data(
        'N', 'D', script_code, '1m', date, date).loc[15:]
    new_entry_index = df.index[df["Datetime"] == stop_loss_time][0]
    new_entry_point = df.loc[new_entry_index]["Close"]
    new_stop_loss = new_entry_point*1.2
    print("New stop loss at ", new_entry_point, new_stop_loss)
    screen_dataframe = get_dataframe_date(df, given_date)
    # If Test after market uncomment below
    # screen_dataframe = screen_dataframe[new_entry_index:-30]
    screen_dataframe = screen_dataframe[new_entry_index:]
    return screen_dataframe, new_stop_loss


def get_exit_points(screen_dataframe, new_stop_loss):
    buy_point = -1
    for index in range(len(screen_dataframe)):
        temp_df = screen_dataframe.iloc[index]
        temp_close_point = temp_df["High"]
        if(temp_close_point > new_stop_loss):
            buy_point = temp_close_point
            print("Exited att ", temp_close_point)
            print("Exited df\n", temp_df)
            break
        elif(temp_close_point < new_stop_loss*0.75):
            new_stop_loss = temp_close_point*1.2
    if(buy_point == -1):
        print("Exited at ", screen_dataframe.iloc[len(
            screen_dataframe)-1]["Close"])
        print("Exited df ", screen_dataframe.iloc[len(
            screen_dataframe)-1])


call_entry, call_stoploss = entry_stoploss(call_script_code, given_date)
put_entry, put_stoploss = entry_stoploss(put_script_code, given_date)
print("Put Entry and Stoploss ", put_entry, put_stoploss)
print("Call Entry and Stoploss ", call_entry, call_stoploss)

put_stop_loss_time = get_stoploss_time(
    put_script_code, given_date, put_stoploss)
print("Stoploss hit time at PUT ", put_stop_loss_time)
call_stop_loss_time = get_stoploss_time(
    call_script_code, given_date, call_stoploss)
print("Stoploss hit time at CALL ", call_stop_loss_time)

stop_loss_time = None
trailing_script_code = None
if(put_stop_loss_time is not None):
    stop_loss_time = put_stop_loss_time
    trailing_script_code = call_script_code
if(call_stop_loss_time is not None):
    stop_loss_time = call_stop_loss_time
    trailing_script_code = put_script_code

screen_dataframe, new_stop_loss = (None, None)
if(stop_loss_time is not None):
    screen_dataframe, new_stop_loss = new_entry_stoploss(
        trailing_script_code, given_date, stop_loss_time)
    get_exit_points(screen_dataframe, new_stop_loss)

'''
9:30 AM strategy ends here
'''
