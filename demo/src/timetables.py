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


def create_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the contract."""
    contract_type = params["ctr-type"]

    # switch case for different contract types
    if contract_type == "Discount Certificate":
        return create_autocallable_timetable(
            monthend_datetimes, spot, trial, params
        )
    if contract_type == "Reverse Convertible":
        return create_reverse_cb_timetable(
            monthend_datetimes, spot, trial, params
        )
    elif contract_type == "Knockout Option":
        return create_barrier_timetable(
            monthend_datetimes, spot, trial, params
        )
    elif contract_type == "Vanilla Option":
        return create_vanilla_timetable(
            monthend_datetimes, spot, trial, params
        )
    elif contract_type == "Cliquet":
        return create_cliquet_timetable(
            monthend_datetimes, spot, trial, params
        )
    else:
        raise ValueError(f"Unknown contract type: {contract_type}")


def create_autocallable_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the discount certificate."""
    ticker = params["ticker"]
    strike = params.get("strike", 80)

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_datetimes[trial + m_per : trial + m_exp + 1 : m_per]
    cpn_rate = 0.17
    accrual_start = monthend_datetimes[trial]

    return DiscountCert(
        ccy="USD",
        asset_name=ticker,
        initial_spot=spot,
        strike=strike,  # percent
        accrual_start=accrual_start,
        maturity=barrier_dts[-1],
        barrier=100,
        barrier_dates=barrier_dts,
        cpn_rate=cpn_rate,
    )


def create_reverse_cb_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the reverse cb."""
    ticker = params["ticker"]
    strike = params.get("strike", 80)

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_datetimes[trial + m_per : trial + m_exp + 1 : m_per]
    cpn_rate = 0.15
    accrual_start = monthend_datetimes[trial]

    return ReverseCB(
        ccy="USD",
        asset_name=ticker,
        initial_spot=spot,
        strike=strike,  # percent
        accrual_start=accrual_start,
        maturity=barrier_dts[-1],
        barrier=100,
        barrier_dates=barrier_dts,
        cpn_rate=cpn_rate,
    )


def create_barrier_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the barrier option."""
    ticker = params["ticker"]
    strike = params.get("strike", spot)

    m_per = 1
    m_exp = 12
    barrier_dts = monthend_datetimes[trial + m_per : trial + m_exp + 1 : m_per]

    return OptionKO(
        ccy="USD",
        asset_name=ticker,
        #strike=strike,
        strike = params.get("strike", 100) * spot / 100,
        maturity=barrier_dts[-1],
        is_call=params["option_type"] == "Call",
        barrier=spot * 1.2,
        barrier_type="Up/Out",
        barrier_dates=barrier_dts,
        rebate=spot * 0.01,
    )


def create_vanilla_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the vanilla option."""
    ticker = params["ticker"]
    strike = params.get("strike", spot)

    m_per = 3
    m_exp = 12
    barrier_dts = monthend_datetimes[trial + m_per : trial + m_exp + 1 : m_per]

    return Option(
        ccy="USD",
        asset_name=ticker,
        strike = params.get("strike", 100) * spot / 100,
        #strike=strike,
        maturity=barrier_dts[-1],  # simplify later
        is_call=params["option_type"] == "Call",
    )


def create_cliquet_timetable(monthend_datetimes, spot, trial, params):
    """Create the timetable for the cliquet option."""
    ticker = params["ticker"]

    m_per = 1
    m_exp = 12
    fix_dates = monthend_datetimes[trial + m_per : trial + m_exp + 1 : m_per]

    # Reverse cap_floor values and divide by 100
    local_cap, local_floor = [val / 100 for val in reversed(params.get("cap_floor", [0.05, -0.05]))]

    return Accumulator(
        ccy="USD",
        asset_name=ticker,
        fix_dates=fix_dates,
        global_floor=0.0,
        local_cap=local_cap,
        local_floor=local_floor,
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
