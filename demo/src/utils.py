import numpy as np
from scipy.optimize import minimize_scalar


# IRR
def loss_irr(
    ytm: float, payments: np.ndarray, times: np.ndarray, price: float
) -> float:
    df = np.exp(-ytm * times)
    pv = np.dot(payments, df)
    err = pv - price
    return 0.5 * err * err


def compute_return(
    payments: np.ndarray,
    times: np.ndarray,
    price: float,
    annualized: bool = True,
) -> float:
    if not annualized:
        return payments.sum() / price - 1
    try:
        res = minimize_scalar(fun=loss_irr, args=(payments, times, price))
        if res.success:
            return res.x
        else:
            raise ValueError(f"Optimization failed: {res.message}")
    except Exception:
        return None
        # raise ValueError(f"IRR Excedption: {res.message}")
