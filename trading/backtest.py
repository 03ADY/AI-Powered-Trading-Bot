"""Simple strategy backtest on close prices."""

import numpy as np
import pandas as pd

from trading.strategy import TradingStrategy


def run_backtest(df: pd.DataFrame, symbol: str, initial: float = 100_000) -> dict:
    if df.empty or len(df) < 50:
        return {"equity_curve": pd.Series(), "metrics": {}, "trades": []}

    strategy = TradingStrategy()
    cash = initial
    shares = 0.0
    equity = []
    trades = []

    for i in range(50, len(df)):
        window = df.iloc[: i + 1]
        price = float(window["Close"].iloc[-1])
        sig = strategy.generate_signal(window, symbol)
        action = sig["signal"]

        if action == 1 and cash > price and shares == 0:
            shares = cash / price
            cash = 0
            trades.append({"date": window.index[-1], "side": "BUY", "price": price, "reason": sig["reason"]})
        elif action == -1 and shares > 0:
            cash = shares * price
            shares = 0
            trades.append({"date": window.index[-1], "side": "SELL", "price": price, "reason": sig["reason"]})

        equity.append(cash + shares * price)

    curve = pd.Series(equity, index=df.index[50 : 50 + len(equity)])
    rets = curve.pct_change().dropna()
    total_ret = (curve.iloc[-1] / initial - 1) if len(curve) else 0
    max_dd = _max_drawdown(curve)

    drawdown = (curve - curve.cummax()) / curve.cummax()

    return {
        "equity_curve": curve,
        "drawdown": drawdown,
        "metrics": {
            "total_return": total_ret,
            "max_drawdown": max_dd,
            "trades": len(trades),
            "sharpe": float(np.sqrt(252) * rets.mean() / rets.std()) if len(rets) and rets.std() else 0,
            "win_rate": _win_rate(trades),
        },
        "trades": trades,
    }


def backtest_vs_buy_hold(df: pd.DataFrame, initial: float, equity_curve: pd.Series) -> dict:
    if df.empty or equity_curve.empty:
        return {}
    start_idx = df.index.get_loc(equity_curve.index[0]) if equity_curve.index[0] in df.index else 50
    start_price = float(df["Close"].iloc[start_idx])
    end_price = float(df["Close"].iloc[-1])
    bh = initial * (end_price / start_price)
    strat = float(equity_curve.iloc[-1])
    return {"strategy": strat, "buy_hold": bh, "alpha": strat - bh}


def _win_rate(trades: list) -> float:
    if len(trades) < 2:
        return 0.0
    wins = 0
    pairs = 0
    for i in range(1, len(trades)):
        if trades[i - 1]["side"] == "BUY" and trades[i]["side"] == "SELL":
            pairs += 1
            if trades[i]["price"] > trades[i - 1]["price"]:
                wins += 1
    return wins / pairs if pairs else 0.0


def _max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())
