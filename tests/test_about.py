"""
Script to test "about contracts" without launching the app.
"""

import pytest
from demo.src.about import tt_description


def test_tt_description():
    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Vanilla Option",
        "option_type": "Put",
    }
    expected_text = "Expected output based on the contract parameters"
    text = tt_description(contract_params)

    expected_text = """
Vanilla Option

An **European Call Option** offers the holder the option to buy a stock for
    a fixed strike price, on the option maturity date.
    Similarly, a **Put Option** offers the holder the option to sell a stock for
    a fixed strike price.
```
         time op  quantity unit track
0  12/31/2020  >      0.00  USD      
1  12/31/2020  +   3230.78  USD      
2  12/31/2020  +     -1.00  SPX      
```"""
    assert text == expected_text


if __name__ == "__main__":
    pytest.main()
