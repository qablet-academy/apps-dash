"""
Script to test "about contracts" without launching the app.
"""

import sys
from os.path import dirname

if __name__ == "__main__":
    sys.path.append(dirname(dirname(dirname(__file__))))

    from src.about import tt_description

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Vanilla Option",
        "option_type": "Put",
    }
    text = tt_description(contract_params)
    print(text)
