import cProfile
import pstats
from pstats import SortKey

from try_backtest import main  # noqa: F401

if __name__ == "__main__":
    main()
    cProfile.run("main()", "restats")
    p = pstats.Stats("restats")
    p.sort_stats(SortKey.CUMULATIVE).print_stats(30)
