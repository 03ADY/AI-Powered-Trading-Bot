"""Streamlit views for advanced tabs."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from trading.config import BENCHMARK, INITIAL_CAPITAL
from trading.lab import (
    calendar_returns,
    portfolio_allocation,
    portfolio_var_approx,
    rolling_sharpe,
    signal_history_matrix,
    walk_forward,
)
from trading.reports import brief_html, dashboard_html
from trading.strategy import TradingStrategy

_SIGNAL_LABELS = {-1: "SELL", 0: "HOLD", 1: "BUY"}


def _format_signal_matrix(mat: pd.DataFrame) -> pd.DataFrame:
    """Map numeric signals to labels (Series.map — works on all pandas versions)."""
    out = mat.copy()
    for col in out.columns:
        out[col] = out[col].map(_SIGNAL_LABELS)
    return out


def render_strategy_lab(data: dict, strategy: TradingStrategy):
    st.header("🔬 Strategy Lab")
    sym = st.selectbox("Focus", [s for s in data if s != BENCHMARK], key="lab_sym")
    df = data[sym]

    c1, c2 = st.columns(2)
    with c1:
        mat = signal_history_matrix({sym: df}, strategy, lookback=15)
        if not mat.empty:
            st.subheader("Signal history (last 15 bars)")
            st.dataframe(_format_signal_matrix(mat), use_container_width=True)
    with c2:
        rs = rolling_sharpe(df["Close"], 30)
        if not rs.empty:
            rs_plot = rs.reset_index()
            rs_plot.columns = ["date", "sharpe"]
            st.plotly_chart(px.line(rs_plot, x="date", y="sharpe", title="Rolling 30d Sharpe"), use_container_width=True)

    cal = calendar_returns(df["Close"])
    if not cal.empty:
        st.subheader("Monthly return calendar")
        z = cal.astype(float).values
        fig = go.Figure(
            data=go.Heatmap(
                z=z,
                x=[str(c) for c in cal.columns],
                y=[str(i) for i in cal.index],
                colorscale="RdYlGn",
                zmid=0,
            )
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Year", height=320)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("Run walk-forward split", type="primary"):
        st.session_state.wf = walk_forward(df, sym)
    wf = st.session_state.get("wf")
    if wf:
        st.markdown(f"Split at **{wf.get('split_date')}**")
        i, o = wf.get("in_sample", {}), wf.get("out_sample", {})
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("IS return", f"{i.get('total_return', 0):.1%}")
        w2.metric("OOS return", f"{o.get('total_return', 0):.1%}")
        w3.metric("IS Sharpe", f"{i.get('sharpe', 0):.2f}")
        w4.metric("OOS Sharpe", f"{o.get('sharpe', 0):.2f}")


def render_allocation(data: dict, port):
    st.header("📦 Portfolio Allocation")
    alloc = portfolio_allocation(port)
    if alloc.empty:
        st.info("No positions — log BUY signals or run Perfect Demo.")
        eq = {s: 100 / len([x for x in data if x != BENCHMARK]) for s in data if s != BENCHMARK}
        st.subheader("Equal-weight benchmark (demo)")
        st.dataframe(pd.DataFrame([{"symbol": s, "weight": w} for s, w in eq.items()]), hide_index=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(alloc, names="symbol", values="weight", hole=0.4), use_container_width=True)
        with c2:
            st.dataframe(alloc, use_container_width=True, hide_index=True)
    weights = {row["symbol"]: row["weight"] / 100 for _, row in alloc.iterrows()} if not alloc.empty else {}
    if weights:
        pvar = portfolio_var_approx(data, weights)
        st.metric("Portfolio VaR (approx)", f"{pvar:.2%}")


def render_export_center(scanner, port, metrics: dict, symbol: str, executive_brief_fn):
    st.header("📦 Export Center")
    brief = executive_brief_fn(scanner, metrics, symbol)
    pack = dashboard_html(
        brief,
        kpis={
            "equity": port.equity,
            "positions": len(port.positions),
            "buy_signals": int((scanner["signal"] == "BUY").sum()) if scanner is not None and not scanner.empty else 0,
        },
    )
    st.download_button("Full dashboard HTML", pack.encode(), "tradepulse_dashboard.html", type="primary")
    st.download_button("Executive brief MD", brief.encode(), "tradepulse_brief.md")
    st.download_button("Scanner CSV", scanner.to_csv(index=False).encode(), "scanner.csv")
