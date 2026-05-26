"""Monte Carlo equity path simulation."""

import numpy as np
import pandas as pd


def simulate_paths(close: pd.Series, days: int = 30, simulations: int = 500, initial: float = 100_000) -> pd.DataFrame:
    rets = close.pct_change().dropna()
    if rets.empty:
        return pd.DataFrame()
    mu, sigma = rets.mean(), rets.std()
    rng = np.random.default_rng(42)
    paths = []
    for i in range(simulations):
        daily = rng.normal(mu, sigma, days)
        equity = initial * np.cumprod(1 + daily)
        paths.append(equity)
    return pd.DataFrame(paths).T
