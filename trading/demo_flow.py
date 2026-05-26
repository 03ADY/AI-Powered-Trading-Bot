"""One-click perfect demo — populates session state."""

from trading.backtest import run_backtest
from trading.config import BENCHMARK, INITIAL_CAPITAL
from trading.data import fetch_yfinance
from trading.indicators import add_indicators
from trading.insights import scan_signals
from trading.portfolio_sim import PaperPortfolio
from trading.strategy import TradingStrategy


def run_perfect_demo(symbols: list[str], days: int = 90, *, synthetic: bool = False) -> None:
    import streamlit as st

    if synthetic:
        from trading.synthetic import generate_synthetic
        sym_list = list(dict.fromkeys(symbols + [BENCHMARK]))
        raw = {s: generate_synthetic(s, days=days) for s in sym_list}
        st.session_state.data_source = "synthetic"
    else:
        sym_list = list(dict.fromkeys(symbols + [BENCHMARK]))
        raw = fetch_yfinance(sym_list, days=days)
        st.session_state.data_source = "yahoo"
    for sym in raw:
        raw[sym] = add_indicators(raw[sym])
    st.session_state.market_data = raw

    strategy = TradingStrategy()
    trade_syms = [s for s in raw if s != BENCHMARK]
    if trade_syms:
        bt = run_backtest(raw[trade_syms[0]], trade_syms[0], INITIAL_CAPITAL)
        st.session_state.backtest = bt

    scanner = scan_signals({k: v for k, v in raw.items() if k != BENCHMARK}, strategy)
    st.session_state.demo_scanner = scanner

    port = PaperPortfolio(cash=INITIAL_CAPITAL)
    sig_map = {"BUY": 1, "SELL": -1, "HOLD": 0}
    for _, row in scanner.head(2).iterrows():
        if row["signal"] == "BUY":
            port.execute_signal(
                row["symbol"], sig_map["BUY"], float(row["price"]), float(row["confidence"]),
                str(row["reason"]), dry_run=False,
            )
    st.session_state.portfolio = port
    st.session_state.alerts = [
        {"time": "Demo", "message": f"Auto: {row['symbol']} {row['signal']} ({row['confidence']:.0%})"}
        for _, row in scanner.head(3).iterrows()
    ]
    st.session_state.perfect_demo_done = True
