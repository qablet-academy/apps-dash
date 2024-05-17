"""
A Cashflow Model using data from a CSV file parsed into a polars dataframe.
"""

import polars as pl
from qablet.base.cf import CFModelPyBase

MS_IN_DAY = 1000 * 3600 * 24
TS_TO_YEARS = 1 / (365 * 24 * 3600 * 1e9)


class CFModelPyCSV(CFModelPyBase):
    """CFModel that uses data from a CSV and interfaces with qablet cashflow model."""

    def __init__(self, filename, base):
        """Read the csv file on initialization. Assumes that there is a date column and the
        data is sorted by the date column. Assumes that the other columns are the units.
        infer_schema_length is set to None, which causes the csv reader to read the whole file
        before inferring the schema. This is needed if the first row may have blanks. A faster
        read can be accomplished by supplying the schema directly."""

        self.data = pl.read_csv(
            filename, try_parse_dates=True, infer_schema_length=None
        ).set_sorted("date")
        self.ts = self.data["date"].cast(int)

        super().__init__(base)

    def get_value(self, unit, ts):
        """Return value for given unit, on given timestamp (ms).
        search_sorted is faster than filter by date. It picks the date on or before the ts.
        it appears that polars stores dates as a day timestamp, so a conversion is
        needed from qablet's milliseconds timestamp."""
        row = self.ts.search_sorted(ts // MS_IN_DAY)
        val = self.data.item(row, unit)
        return val


def get_cf(pricing_ts, timetable, stats):
    """Return cashflows and years for a given timetable and stats."""
    cf_vec = stats["value"].to_numpy()
    idx_vec = stats["index"].to_numpy()
    ts_vec = timetable["events"]["time"].to_numpy()[idx_vec]
    yrs_vec = (ts_vec - pricing_ts.to_numpy()).astype(float) * TS_TO_YEARS
    return yrs_vec, cf_vec, ts_vec


class DataModel:
    """A Datamodel (for csv files) used by the app. We will keep it separate from
    the qablet model."""

    def __init__(self, filename):
        self.data = pl.read_csv(
            filename, try_parse_dates=True, infer_schema_length=None
        ).set_sorted("date")

    def get_value(self, unit, dt):
        """Return value for given unit, on given datetime."""
        row = self.data["date"].search_sorted(dt)
        val = self.data.item(row, unit)
        return val

    def get_curve(self, unit, start, end):
        """Return value for given unit, for given datetime range."""
        return self.data.filter(pl.col("date") >= start).filter(
            pl.col("date") <= end
        )
