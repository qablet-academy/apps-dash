from datetime import datetime

import polars as pl
from qablet.base.cf import CFModelPyBase

MS_IN_DAY = 1000 * 3600 * 24
TS_TO_YEARS = 1 / (365 * MS_IN_DAY)


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

    df = pl.from_arrow(stats)
    # get the timestamp of the events, corresponding to the index in the stats
    ts_col = pl.from_arrow(
        timetable["events"]["time"], schema={"time": pl.Int64}
    )[df["index"]]
    df = df.with_columns(ts=ts_col)
    # net cashflows by timestamp
    df = df.group_by("ts").agg(pl.col("value").sum())

    cf_vec = df["value"].to_numpy()
    ts_vec = df["ts"].to_numpy()
    yrs_vec = (ts_vec - pricing_ts).astype(float) * TS_TO_YEARS
    return yrs_vec, cf_vec, ts_vec


class DataModel:
    """A Datamodel (for csv files) used by the app. We will keep it separate from
    the qablet model."""

    def __init__(self, filename):
        self.data = pl.read_csv(
            filename, try_parse_dates=True, infer_schema_length=None
        ).set_sorted("date")
        self.start_date = datetime(2019, 12, 31)
        self.end_date = datetime(2024, 4, 30)

    def get_value(self, unit, dt):
        """Return value for given unit, on given datetime."""
        row = self.data["date"].search_sorted(dt)
        val = self.data.item(row, unit)
        return val

    def get_curve(self, start, end):
        """Return value for given unit, for given datetime range."""
        return self.data.filter(pl.col("date") >= start).filter(
            pl.col("date") <= end
        )

    def monthend_datetimes(self, ticker):
        """Return month-end datetimes for a given ticker."""

        # First generate month-end dates using Polars
        monthend_datetimes = pl.datetime_range(
            self.start_date, self.end_date, "1mo", eager=True, time_zone="UTC"
        )

        # Find valid dates for the ticker
        valid_ticker_data = self.data.select(["date", ticker]).drop_nulls()
        valid_datetimes = (
            valid_ticker_data["date"]
            .cast(datetime)
            .dt.convert_time_zone("UTC")
        )

        # Adjust the dates to the nearest trading date for that ticker (on or before)
        adjusted_datetimes = []
        for dt in monthend_datetimes:
            idx = valid_datetimes.search_sorted(dt, side="right") - 1
            if idx >= 0:
                adjusted_datetimes.append(valid_datetimes[idx])
            else:
                raise ValueError(f"No valid date found for {dt}")

        return adjusted_datetimes
