import polars as pl
from datetime import datetime,date,timedelta
from qablet.base.cf import CFModelPyBase
import numpy as np
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

    df = pl.from_arrow(stats)
    # get the timestamp of the events, corresponding to the index in the stats
    ts_col = pl.from_arrow(timetable["events"]["time"])[df["index"]]
    df = df.with_columns(ts=ts_col)
    # net cashflows by timestamp
    df = df.group_by("ts").agg(pl.col("value").sum())

    cf_vec = df["value"].to_numpy()
    ts_vec = df["ts"].to_numpy()
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

    def get_curve(self, start, end):
        """Return value for given unit, for given datetime range."""
        return self.data.filter(pl.col("date") >= start).filter(
            pl.col("date") <= end
        )
    
    

    def monthend_dates(self, ticker):
     """Return month-end dates for a given range."""
     start_date = datetime(2019, 12, 31)
     end_date = datetime(2024, 4, 30)

     # Generate month-end dates using Polars
     monthend_dates = pl.date_range(start_date, end_date, "1mo", eager=True)

     # Adjust the dates to the nearest trading date for that ticker (on or before)
     adjusted_dates = []
     for date in monthend_dates:
         # Pass the ticker value to filter the dataframe
         ticker_data = self.data.select(["date", ticker]).drop_nulls()
         valid_dates = ticker_data["date"]

         # Convert valid_dates to datetime.datetime
         #valid_dates = [datetime.combine(d, datetime.min.time())]

         if len(valid_dates) == 0:
             adjusted_dates.append(None)  # Handle empty list case
         else:
             idx = valid_dates.search_sorted(date, side="right") - 1
             if idx >= 0:
                 adjusted_dates.append(valid_dates[idx])
             else:
                 adjusted_dates.append(None)

     # Ensure adjusted_dates are in datetime.datetime format
     #adjusted_dates = [datetime.combine(d, datetime.min.time()) if isinstance(d, datetime.date) and not isinstance(d, datetime.datetime) else d for d in adjusted_dates]
    
     
     return adjusted_dates

