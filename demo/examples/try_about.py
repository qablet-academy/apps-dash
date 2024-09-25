"""
Script to test "about contracts" without launching the app.
"""

from demo.src.about import tt_description

if __name__ == "__main__":
    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Vanilla Option",
        "option_type": "Put",
    }
    text = tt_description(contract_params)
    print(text)
