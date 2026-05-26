"""Symbol comparison utilities."""

import pandas as pd

from trading.risk import PortfolioAnalytics


def compare_symbols(data: dict[str, pd.DataFrame], benchmark: str = "SPY") -> pd.DataFrame:
    rows = []
    bench_rets = None
    if benchmark in data and not data[benchmark].empty:
        bench_rets = PortfolioAnalytics.daily_returns(data[benchmark]["Close"])
    for sym, df in data.items():
        if sym == benchmark or df.empty:
            continue
        close = df["Close"]
        rets = PortfolioAnalytics.daily_returns(close)
        total_ret = (close.iloc[-1] / close.iloc[0] - 1) if len(close) > 1 else 0
        rows.append({
            "symbol": sym,
            "return": total_ret,
            "volatility": rets.std() * (252 ** 0.5) if not rets.empty else 0,
            "sharpe": PortfolioAnalytics.sharpe(rets),
            "max_dd": PortfolioAnalytics.max_drawdown(close),
            "beta": PortfolioAnalytics.beta_vs_benchmark(rets, bench_rets) if bench_rets is not None else 0,
        })
    return pd.DataFrame(rows).sort_values("sharpe", ascending=False)
