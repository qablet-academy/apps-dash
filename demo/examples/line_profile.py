# Description: This file is used to profile the code using line_profiler

import sys
from os.path import dirname

from line_profiler import LineProfiler

if __name__ == "__main__":
    sys.path.append(dirname(dirname(dirname(__file__))))

    from demo.src.backtest import run_backtest
    from try_backtest import main  # noqa: F401

    # Create a LineProfiler object, specifying the methods to be profiled by line
    lprofiler = LineProfiler(run_backtest)
    # Wrap the entry function with the LineProfiler object, then run it.
    lp_wrapper = lprofiler(main)
    lp_wrapper()
    # Print the profiling results in milliseconds
    lprofiler.print_stats(output_unit=1e-03)
