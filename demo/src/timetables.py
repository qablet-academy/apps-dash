"""
Create timetables for different contracts, using the contract parameters dict.
"""
import polars as pl
import pyarrow as pa
from qablet_contracts.eq.autocall import DiscountCert, ReverseCB
from qablet_contracts.eq.barrier import OptionKO
from qablet_contracts.eq.cliquet import Accumulator
from qablet_contracts.eq.vanilla import Option
from qablet_contracts.timetable import TS_EVENT_SCHEMA

CONTRACT_TYPES = [
    "Discount Certificate",
    "Reverse Convertible",
    "Knockout Option",
    "Vanilla Option",
    "Cliquet",
]


def create_timetable(pricing_ts, monthend_dates, spot, trial, params):
    """Create the timetable for the autocallable."""
    contract_type = params["ctr-type"]

    # switch case for different contract types
    if contract_type == "Discount Certificate":
        return create_autocallable_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    if contract_type == "Reverse Convertible":
        return create_reverse_cb_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    elif contract_type == "Knockout Option":
        return create_barrier_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    elif contract_type == "Vanilla Option":
        return create_vanilla_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    elif contract_type == "Cliquet":
        return create_cliquet_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    else:
        raise ValueError(f"Unknown contract type: {contract_type}")


def create_autocallable_timetable(
    pricing_ts, monthend_dates, spot, trial, params
):
    """Create the timetable for the autocallable."""
    ticker = params["ticker"]

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_dates[trial + m_per : trial + m_exp + 1 : m_per]
    cpn_rate = 0.16

    return DiscountCert(
        ccy="USD",
        asset_name=ticker,
        initial_spot=spot,
        strike=80,  # percent
        accrual_start=pricing_ts,
        maturity=barrier_dts[-1],
        barrier=100,
        barrier_dates=barrier_dts,
        cpn_rate=cpn_rate,
    )


def create_reverse_cb_timetable(
    pricing_ts, monthend_dates, spot, trial, params
):
    """Create the timetable for the autocallable."""
    ticker = params["ticker"]

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_dates[trial + m_per : trial + m_exp + 1 : m_per]
    cpn_rate = 0.15

    return ReverseCB(
        ccy="USD",
        asset_name=ticker,
        initial_spot=spot,
        strike=80,  # percent
        accrual_start=pricing_ts,
        maturity=barrier_dts[-1],
        barrier=100,
        barrier_dates=barrier_dts,
        cpn_rate=cpn_rate,
    )


def create_barrier_timetable(pricing_ts, monthend_dates, spot, trial, params):
    """Create the timetable for the barrier option."""
    ticker = params["ticker"]

    m_per = 1
    m_exp = 12
    barrier_dts = monthend_dates[trial + m_per : trial + m_exp + 1 : m_per]

    return OptionKO(
        ccy="USD",
        asset_name=ticker,
        strike=spot,
        maturity=barrier_dts[-1],
        is_call=True,
        barrier=spot * 1.1,
        barrier_type="Up/Out",
        barrier_dates=barrier_dts,
        rebate=spot * 0.01,
    )


def create_vanilla_timetable(pricing_ts, monthend_dates, spot, trial, params):
    """Create the timetable for the vanilla option."""
    ticker = params["ticker"]

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_dates[trial + m_per : trial + m_exp + 1 : m_per]

    return Option(
        ccy="USD",
        asset_name=ticker,
        strike=spot,
        maturity=barrier_dts[-1],  # simplify later
        is_call=True,
    )


def create_cliquet_timetable(pricing_ts, monthend_dates, spot, trial, params):
    """Create the timetable for the cliquet option."""
    ticker = params["ticker"]

    m_per = 1
    m_exp = 12
    fix_dates = monthend_dates[trial + m_per : trial + m_exp + 1 : m_per]

    return Accumulator(
        ccy="USD",
        asset_name=ticker,
        fix_dates=fix_dates,
        global_floor=0.0,
        local_cap=0.05,
        local_floor=-0.05,
    )


def extend_timetable(tt1, tt2):
    """Extend the tt1 with new events, in place.
    Assume that all events in tt2 are after the last event in tt1."""
    df1 = pl.from_arrow(tt1["events"])
    df2 = pl.from_arrow(tt2["events"])
    tt1["events"] = df1.extend(df2)._df.to_arrow()[0].cast(TS_EVENT_SCHEMA)


def create_forward_timetable(end_dt, params):
    events = [
        {
            "track": "F",
            "time": end_dt,
            "op": "+",
            "quantity": 1,
            "unit": params["ticker"],
        }
    ]

    events_table = pa.RecordBatch.from_pylist(events, schema=TS_EVENT_SCHEMA)
    return {"events": events_table, "expressions": {}}
