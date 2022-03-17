import pandas as pd

script_df = pd.read_csv("scripmaster-csv-format.csv")
call = script_df[script_df["FullName"] == "BANKNIFTY 24 Mar 2022 CE 36400.00"].iloc[0]["Scripcode"]
print(type(call.__int__()))
