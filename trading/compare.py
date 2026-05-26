"""Symbol comparison utilities."""

import numpy as np
import pandas as pd
import plotly.express as px

from trading.risk import PortfolioAnalytics


def _finite(x: float) -> float:
    if x is None or not np.isfinite(x):
        return 0.0
    return float(x)


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
        vol = rets.std() * (252 ** 0.5) if not rets.empty else 0.0
        rows.append({
            "symbol": sym,
            "return": _finite(total_ret),
            "volatility": _finite(vol),
            "sharpe": _finite(PortfolioAnalytics.sharpe(rets)),
            "max_dd": _finite(PortfolioAnalytics.max_drawdown(close)),
            "beta": _finite(
                PortfolioAnalytics.beta_vs_benchmark(rets, bench_rets) if bench_rets is not None else 0.0
            ),
        })
    if not rows:
        return pd.DataFrame(columns=["symbol", "return", "volatility", "sharpe", "max_dd", "beta"])
    return pd.DataFrame(rows).sort_values("sharpe", ascending=False)


def risk_return_scatter(cmp: pd.DataFrame):
    """Risk/return chart — marker size must be non-negative (Plotly constraint)."""
    plot = cmp.copy()
    for col in ("return", "volatility", "sharpe", "max_dd", "beta"):
        plot[col] = pd.to_numeric(plot[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    plot["marker_size"] = plot["sharpe"].abs().clip(lower=0.05) + 0.15
    return px.scatter(
        plot,
        x="volatility",
        y="return",
        size="marker_size",
        color="sharpe",
        hover_name="symbol",
        title="Risk/return",
        color_continuous_scale="RdYlGn",
    )
