"""Strategy lab: heatmaps, rolling metrics, walk-forward."""

import numpy as np
import pandas as pd

from trading.backtest import run_backtest
from trading.risk import PortfolioAnalytics
from trading.strategy import TradingStrategy


def signal_history_matrix(data: dict, strategy: TradingStrategy, lookback: int = 20) -> pd.DataFrame:
    rows = {}
    for sym, df in data.items():
        if df.empty or len(df) < lookback + 50:
            continue
        hist = []
        for i in range(-lookback, 0):
            window = df.iloc[: len(df) + i]
            if len(window) < 50:
                continue
            sig = strategy.generate_signal(window, sym)
            hist.append(sig["signal"])
        rows[sym] = hist
    return pd.DataFrame(rows)


def rolling_sharpe(close: pd.Series, window: int = 30) -> pd.Series:
    rets = close.pct_change()
    roll = rets.rolling(window).mean() / rets.rolling(window).std()
    return (roll * np.sqrt(252)).replace([np.inf, -np.inf], np.nan).dropna()


def walk_forward(df: pd.DataFrame, symbol: str, split: float = 0.7, initial: float = 100_000) -> dict:
    if df.empty:
        return {}
    cut = int(len(df) * split)
    in_sample = run_backtest(df.iloc[:cut], symbol, initial)
    out_sample = run_backtest(df.iloc[cut - 50 :], symbol, initial)  # need warmup
    return {
        "in_sample": in_sample.get("metrics", {}),
        "out_sample": out_sample.get("metrics", {}),
        "split_date": df.index[cut] if cut < len(df) else df.index[-1],
    }


def calendar_returns(close: pd.Series) -> pd.DataFrame:
    rets = close.pct_change()
    df = pd.DataFrame({"ret": rets})
    df["year"] = df.index.year
    df["month"] = df.index.month
    return df.pivot_table(index="year", columns="month", values="ret", aggfunc="sum").fillna(0)


def portfolio_allocation(port) -> pd.DataFrame:
    if not port.positions:
        return pd.DataFrame(columns=["symbol", "weight"])
    total = sum(p["market_value"] for p in port.positions.values()) or 1
    return pd.DataFrame([
        {"symbol": s, "weight": p["market_value"] / total * 100}
        for s, p in port.positions.items()
    ])


def portfolio_var_approx(data: dict, weights: dict[str, float], alpha: float = 0.05) -> float:
    """Weighted sum of marginal VaR (demo simplification)."""
    var_sum = 0.0
    for sym, w in weights.items():
        if sym not in data or w <= 0:
            continue
        rets = PortfolioAnalytics.daily_returns(data[sym]["Close"])
        v, _ = PortfolioAnalytics.var_cvar(rets, alpha)
        var_sum += abs(w) * abs(v)
    return var_sum
