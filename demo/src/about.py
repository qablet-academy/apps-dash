"""
Write about the contract in markdown.
"""

from demo.src.model import DataModel
from demo.src.timetables import create_timetable


def tt_description(contract_params: dict, trial=0):
    # Create Contract
    csvdata = DataModel()

    # get all month ends
    monthend_datetimes = csvdata.monthend_datetimes(contract_params["ticker"])

    pricing_datetime = monthend_datetimes[trial]  # timestamp of trading date

    spot = csvdata.get_value(contract_params["ticker"], pricing_datetime)

    contract = create_timetable(
        monthend_datetimes, spot, trial, contract_params
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
