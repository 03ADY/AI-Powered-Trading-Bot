"""Synthetic OHLCV when live data unavailable (offline demo)."""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_synthetic(symbol: str, days: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(abs(hash(symbol)) % (2**32))
    dates = pd.bdate_range(end=datetime.now(), periods=days)
    n = len(dates)
    ret = rng.normal(0.0008, 0.018, n)
    close = 100 * np.exp(np.cumsum(ret))
    open_ = close * (1 + rng.normal(0, 0.002, n))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, n))
    vol = rng.integers(1_000_000, 5_000_000, n)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol},
        index=dates,
    )
