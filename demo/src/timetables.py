"""
Create timetables for different contracts.
"""
from qablet_contracts.eq.autocall import AutoCallable
from qablet_contracts.eq.barrier import OptionKO
from qablet_contracts.eq.cliquet import Accumulator
from qablet_contracts.eq.vanilla import Option

CONTRACT_TYPES = ["AutoCallable", "KnockOut", "Vanilla", "Cliquet"]


def create_timetable(pricing_ts, monthend_dates, spot, trial, params):
    """Create the timetable for the autocallable."""
    contract_type = params["ctr-type"]

    # switch case for different contract types
    if contract_type == "AutoCallable":
        return create_autocallable_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    elif contract_type == "KnockOut":
        return create_barrier_timetable(
            pricing_ts, monthend_dates, spot, trial, params
        )
    elif contract_type == "Vanilla":
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
    cpn_rate = 0.05

    return AutoCallable(
        ccy="USD",
        asset_name=ticker,
        initial_spot=spot,
        strike=80,  # percent
        accrual_start=pricing_ts,
        maturity=barrier_dts[-1],
        barrier=100,
        barrier_dates=barrier_dts,
        cpn_rate=cpn_rate,
    ).timetable()


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
    ).timetable()


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
    ).timetable()


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
    ).timetable()
