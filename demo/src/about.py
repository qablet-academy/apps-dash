"""
Write about the contract in markdown.
"""
import os
from datetime import datetime

import pandas as pd
import polars as pl

from src.timetables import create_timetable

ROOTDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def tt_description(contract_params: dict):
    # TODO: There is some duplication code here with run_backtest.
    # Create Contract
    filename = ROOTDIR + "/data/spots.csv"

    # get all month ends
    df = pl.read_csv(
        filename, try_parse_dates=True, infer_schema_length=None
    ).set_sorted("date")

    monthend_dates = pd.bdate_range(
        datetime(2020, 3, 31), datetime(2024, 4, 30), freq="1BME"
    )
    i = 0
    pricing_ts = monthend_dates[i]  # timestamp of trading date

    row_idx = df["date"].search_sorted(pricing_ts)
    spot = df.item(row_idx, contract_params["ticker"])

    contract = create_timetable(
        pricing_ts, monthend_dates, spot, i, contract_params
    )

    # Get Definition Text from Contract docstring
    defn_text = contract.__doc__.split("\n\n")[0]

    # Create Timetable Text
    timetable = contract.timetable()
    df = timetable["events"].to_pandas()
    df["time"] = df["time"].dt.strftime(
        "%m/%d/%Y"
    )  # replace timestamp by Date
    tt_text = df.to_string()

    # Compose Full Text
    # Contract Name, Definition, followed by Timetable in Code Block
    full_text = f"""
{contract_params["ctr-type"]}

{defn_text}
```
{tt_text}
```"""
    return full_text
