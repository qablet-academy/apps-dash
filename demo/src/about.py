"""
Write about the contract in markdown.
"""
from datetime import datetime

import pandas as pd

from src.model import DataModel
from src.timetables import create_timetable
from src.utils import ROOTDIR


def tt_description(contract_params: dict, trial=0):
    # Create Contract
    filename = ROOTDIR + "/data/spots.csv"
    csvdata = DataModel(filename)

    # get all month ends
    monthend_dates = pd.bdate_range(
        datetime(2020, 3, 31), datetime(2024, 4, 30), freq="1BME"
    )
    pricing_ts = monthend_dates[trial]  # timestamp of trading date

    spot = csvdata.get_value(contract_params["ticker"], pricing_ts)

    contract = create_timetable(
        pricing_ts, monthend_dates, spot, trial, contract_params
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
