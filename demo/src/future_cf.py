"""
Project Future Cashflows for a given contract.
"""

from finmc.models.localvol import LVMC
from qablet.base.flags import Stats
from qablet.base.mc import MCPricer

from src.model import DataModel
from src.timetables import (
    create_forward_timetable,
    create_timetable,
    extend_timetable,
)
from src.utils import ROOTDIR, base_dataset, dataset_assets


def model_cashflows(contract_params: dict, trial=0, vol=0.3):
    # Create the models
    csvdata = DataModel(f"{ROOTDIR}/data/spots.csv")
    model = MCPricer(LVMC)

    ticker = contract_params["ticker"]
    monthend_datetimes = csvdata.monthend_datetimes(ticker)
    pricing_datetime = monthend_datetimes[trial]
    pricing_ts = int(pricing_datetime.timestamp() * 1000)
    spot = csvdata.get_value(ticker, pricing_datetime)

    # prepare dataset
    dataset = base_dataset()

    dataset["PRICING_TS"] = pricing_ts
    dataset["ASSETS"] = dataset_assets(spot, contract_params)
    dataset["LV"] = {"ASSET": ticker, "VOL": vol}

    # create timetable for contract
    timetable = create_timetable(
        monthend_datetimes, spot, trial, contract_params
    ).timetable()

    # turn on cashflow flag
    dataset["MC"]["FLAGS"] = Stats.CASHFLOW
    dataset["MC"]["PATHS"] = 100  # Too many dots otherwise

    # create forward timetable
    end_dt = timetable["events"]["time"][-1].as_py()
    fwd_timetable = create_forward_timetable(end_dt, contract_params)

    extend_timetable(timetable, fwd_timetable)

    _, stats = model.price(timetable, dataset)

    # Compute net cashflows for original timetable, and the forward timetable
    sums = []
    for i in range(2):
        sum = 0
        for v in stats["CASHFLOW"][i].values():
            sum = sum + v
        sums.append(sum)

    return sums, spot


def vol_risk(contract_params: dict, trial=0):
    # Create the models
    csvdata = DataModel(f"{ROOTDIR}/data/spots.csv")
    model = MCPricer(LVMC)

    ticker = contract_params["ticker"]
    monthend_datetimes = csvdata.monthend_datetimes(ticker)
    pricing_datetime = monthend_datetimes[trial]
    pricing_ts = int(pricing_datetime.timestamp() * 1000)
    spot = csvdata.get_value(ticker, pricing_datetime)

    # prepare dataset
    dataset = base_dataset()

    dataset["PRICING_TS"] = pricing_ts
    dataset["ASSETS"] = dataset_assets(spot, contract_params)
    dataset["LV"] = {"ASSET": ticker}  # Vol to be added later

    # create timetable for contract
    timetable = create_timetable(
        monthend_datetimes, spot, trial, contract_params
    ).timetable()

    vols = [0.02, 0.05, 0.1, 0.2, 0.3]
    prices = []
    for vol in vols:
        dataset["LV"]["VOL"] = vol
        price, _ = model.price(timetable, dataset)
        prices.append(price)

    return vols, prices
