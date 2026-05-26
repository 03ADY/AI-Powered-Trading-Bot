"""TradePulse Enterprise — trading command center."""

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

from trading.backtest import backtest_vs_buy_hold, run_backtest
from trading.compare import compare_symbols
from trading.monte_carlo import simulate_paths
from trading.sizing import fixed_fractional, kelly_fraction
from trading.config import APP_NAME, BENCHMARK, INITIAL_CAPITAL, SCENARIOS, DEFAULT_SYMBOLS
from trading.data import fetch_yfinance
from trading.indicators import add_indicators
from trading.insights import executive_brief, insight_cards, scan_signals
from trading.portfolio_sim import PaperPortfolio
from trading.reports import brief_html
from trading.risk import PortfolioAnalytics
from trading.strategy import TradingStrategy
from trading.demo_flow import run_perfect_demo
from trading.views import render_allocation, render_export_center, render_strategy_lab

st.set_page_config(page_title=APP_NAME, page_icon="📈", layout="wide")

st.markdown(f"""
<div style="background:linear-gradient(135deg,#059669,#2563eb);padding:1.5rem 2rem;border-radius:14px;color:white;">
<h1 style="margin:0;">📈 {APP_NAME}</h1>
<p style="margin:0.4rem 0 0;">Perfect demo · Strategy Lab · Walk-forward · Full dashboard export</p>
</div>
""", unsafe_allow_html=True)

strategy = TradingStrategy()
analytics = PortfolioAnalytics()

if "portfolio" not in st.session_state:
    st.session_state.portfolio = PaperPortfolio(cash=INITIAL_CAPITAL)
if "market_data" not in st.session_state:
    st.session_state.market_data = {}

with st.sidebar:
    st.markdown("### 🎬 Demo")
    present = st.toggle("Present mode", value=True)
    scenario = st.selectbox("Scenario", list(SCENARIOS.keys()), index=0)
    st.caption(SCENARIOS[scenario]["blurb"])
    preset_syms = SCENARIOS[scenario]["symbols"] if scenario != "Custom" else DEFAULT_SYMBOLS
    symbols = st.multiselect("Symbols", DEFAULT_SYMBOLS, default=preset_syms[:5])
    days = 90 if present else st.slider("History (days)", 30, 365, 90)
    dry_run = st.toggle("Dry run orders", value=True)
    use_synthetic = st.toggle("Force synthetic data", value=False, help="Offline demo without Yahoo")
    auto_refresh = False if present else st.toggle("Auto-refresh", value=False)
    if st.button("📥 Load / refresh data", type="primary", use_container_width=True):
        st.cache_data.clear()
        sym_list = list(dict.fromkeys(symbols + [BENCHMARK]))
        if use_synthetic:
            from trading.synthetic import generate_synthetic
            raw = {s: generate_synthetic(s, days=days) for s in sym_list}
            st.session_state.data_source = "synthetic"
        else:
            raw = fetch_yfinance(sym_list, days=days)
            st.session_state.data_source = "yahoo"
        for sym in raw:
            raw[sym] = add_indicators(raw[sym])
        st.session_state.market_data = raw
        st.toast(f"Loaded {len(raw)} symbols ({st.session_state.data_source})")
    if st.button("✨ Run perfect demo", use_container_width=True):
        with st.spinner("Running full demo flow…"):
            run_perfect_demo(preset_syms, days=days, synthetic=use_synthetic)
        st.cache_data.clear()
        st.rerun()
    if st.button("🔄 Reset paper portfolio"):
        st.session_state.portfolio = PaperPortfolio(cash=INITIAL_CAPITAL)
        st.session_state.pop("perfect_demo_done", None)
        st.rerun()
    with st.expander("✅ Presenter checklist"):
        st.markdown("""
1. **Run perfect demo**  
2. **Scanner** → top BUY  
3. **Strategy Lab** → walk-forward  
4. **Backtest** → vs buy & hold  
5. **Monte Carlo** → fan chart  
6. **Export Center** → dashboard HTML  
        """)
    try:
        if "API_KEY" in st.secrets:
            st.toggle("Alpaca (needs keys)", value=False)
    except Exception:
        pass

data = st.session_state.market_data
if not data:
    st.info("Click **Load / refresh data** in the sidebar to begin.")
    st.stop()

prices = {s: float(d["Close"].iloc[-1]) for s, d in data.items() if not d.empty and "Close" in d.columns}
st.session_state.portfolio.update_prices(prices)
port = st.session_state.portfolio

day_pnl = port.equity - INITIAL_CAPITAL * 0.98
day_pnl_pct = (port.equity / (INITIAL_CAPITAL * 0.98) - 1) * 100
scanner = scan_signals({k: v for k, v in data.items() if k != BENCHMARK}, strategy)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Equity", f"${port.equity:,.0f}")
c2.metric("Cash", f"${port.cash:,.0f}")
c3.metric("Positions", len(port.positions))
c4.metric("Day P&L", f"${day_pnl:,.0f}", delta=f"{day_pnl_pct:.2f}%")
c5.metric("BUY signals", int((scanner["signal"] == "BUY").sum()) if not scanner.empty else 0)

cards = insight_cards(scanner, day_pnl_pct)
html_cards = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.75rem;margin:0.5rem 0 1rem;">'
for c in cards:
    border = {"positive": "#22c55e", "warning": "#f59e0b", "neutral": "#3b82f6"}.get(c["tone"], "#3b82f6")
    html_cards += f'<div style="border-left:4px solid {border};padding:0.8rem;background:#fff;border-radius:8px;border:1px solid #e2e8f0;"><small>{c["icon"]} {c["title"]}</small><div>{c["body"]}</div></div>'
html_cards += "</div>"
st.markdown(html_cards, unsafe_allow_html=True)

if auto_refresh:
    import time
    time.sleep(30)
    st.cache_data.clear()
    st.rerun()

if st.session_state.get("data_source") == "synthetic":
    st.caption("Using synthetic prices (offline demo mode).")

if st.session_state.get("perfect_demo_done"):
    st.success("Perfect demo loaded — explore tabs below.")

tabs = st.tabs([
    "📊 Command", "📡 Scanner", "🧪 Backtest", "💼 Portfolio", "⚠️ Risk",
    "🔬 Lab", "📦 Alloc", "🎲 Monte Carlo", "📐 Sizing", "⚖️ Compare", "🔔 Alerts",
    "📦 Export",
])

with tabs[0]:
    sym = st.selectbox("Chart symbol", [s for s in data.keys() if s != BENCHMARK], key="chart_sym")
    df = data[sym]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="OHLC"), row=1, col=1)
    if "SMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA20", line=dict(color="orange")), row=1, col=1)
    if "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], fill="tonexty", name="Bollinger", line=dict(width=0)), row=1, col=1)
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", row=2, col=1)
    if "MACD" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signal"), row=3, col=1)
    if BENCHMARK in data and sym != BENCHMARK:
        bench = data[BENCHMARK]["Close"].reindex(df.index).ffill()
        norm = bench / bench.iloc[0] * df["Close"].iloc[0]
        fig.add_trace(go.Scatter(x=df.index, y=norm, name=f"{BENCHMARK} (norm)", line=dict(dash="dot", color="gray")), row=1, col=1)
    fig.update_layout(height=650, xaxis_rangeslider_visible=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    sig = strategy.generate_signal(df, sym)
    if st.button("Log signal to journal", type="primary"):
        port.execute_signal(sym, sig["signal"], prices.get(sym, 0), sig["confidence"], sig["reason"], dry_run=dry_run)
        st.success(f"Logged {sig['signal']} for {sym}")

with tabs[1]:
    st.subheader("Multi-symbol scanner")
    st.dataframe(scanner, use_container_width=True, hide_index=True)
    st.download_button("Export scanner CSV", scanner.to_csv(index=False).encode(), "scanner.csv")
    if not scanner.empty:
        st.plotly_chart(px.bar(scanner, x="symbol", y="confidence", color="signal", title="Confidence by symbol"), use_container_width=True)

with tabs[2]:
    bt_sym = st.selectbox("Backtest symbol", [s for s in data.keys() if s != BENCHMARK], key="bt_sym")
    cap = st.number_input("Initial capital", 10_000, 500_000, int(INITIAL_CAPITAL), 5000)
    if st.button("Run backtest", type="primary"):
        with st.spinner("Simulating…"):
            bt = run_backtest(data[bt_sym], bt_sym, float(cap))
        st.session_state.backtest = bt
    bt = st.session_state.get("backtest")
    if bt and not bt.get("equity_curve", pd.Series()).empty:
        m = bt["metrics"]
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.metric("Total return", f"{m.get('total_return', 0):.1%}")
        b2.metric("Max drawdown", f"{m.get('max_drawdown', 0):.1%}")
        b3.metric("Sharpe", f"{m.get('sharpe', 0):.2f}")
        b4.metric("Win rate", f"{m.get('win_rate', 0):.0%}")
        b5.metric("Trades", m.get("trades", 0))
        vs = backtest_vs_buy_hold(data[bt_sym], float(cap), bt["equity_curve"])
        if vs:
            st.caption(f"Strategy ${vs['strategy']:,.0f} vs buy & hold ${vs['buy_hold']:,.0f} (alpha ${vs['alpha']:,.0f})")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.line(bt["equity_curve"], title="Equity curve"), use_container_width=True)
        with c2:
            if "drawdown" in bt:
                st.plotly_chart(px.area(bt["drawdown"], title="Drawdown"), use_container_width=True)
        if bt["trades"]:
            st.dataframe(pd.DataFrame(bt["trades"]), use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Paper positions")
    if port.positions:
        pos_df = pd.DataFrame([
            {"symbol": s, "qty": p["qty"], "avg": p["avg_price"], "last": p["last_price"], "value": p["market_value"]}
            for s, p in port.positions.items()
        ])
        st.dataframe(pos_df, use_container_width=True, hide_index=True)
    else:
        st.info("No open positions — log BUY signals from Command tab.")
    st.subheader("Trade journal")
    if port.trade_log:
        log_df = pd.DataFrame(port.trade_log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.download_button("Export journal", log_df.to_csv(index=False).encode(), "trade_journal.csv")
    else:
        st.caption("No trades logged yet.")

with tabs[4]:
    sym = st.selectbox("Risk focus", [s for s in data.keys() if s != BENCHMARK], key="risk_sym")
    rets = analytics.daily_returns(data[sym]["Close"])
    bench_rets = analytics.daily_returns(data[BENCHMARK]["Close"]) if BENCHMARK in data else rets
    var, cvar = analytics.var_cvar(rets)
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Sharpe", f"{analytics.sharpe(rets):.2f}")
    r2.metric("Sortino", f"{analytics.sortino(rets):.2f}")
    r3.metric("VaR 5%", f"{var:.2%}")
    r4.metric("Max DD", f"{analytics.max_drawdown(data[sym]['Close']):.1%}")
    r5.metric("Beta vs SPY", f"{analytics.beta_vs_benchmark(rets, bench_rets):.2f}")
    corr = analytics.correlation_matrix({k: v for k, v in data.items() if k != BENCHMARK})
    if not corr.empty:
        st.plotly_chart(go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale="RdBu", zmid=0)), use_container_width=True)
    st.plotly_chart(px.histogram(rets, nbins=40, title="Return distribution"), use_container_width=True)

with tabs[5]:
    render_strategy_lab(data, strategy)

with tabs[6]:
    render_allocation(data, port)

with tabs[7]:
    mc_sym = st.selectbox("Symbol", [s for s in data.keys() if s != BENCHMARK], key="mc_sym")
    mc_days = st.slider("Forward days", 10, 90, 30)
    mc_sims = st.slider("Simulations", 100, 1000, 300, 100)
    paths = simulate_paths(data[mc_sym]["Close"], days=mc_days, simulations=mc_sims, initial=port.equity)
    if not paths.empty:
        p5 = paths.quantile(0.05, axis=1)
        p50 = paths.quantile(0.5, axis=1)
        p95 = paths.quantile(0.95, axis=1)
        fig = go.Figure()
        for col in paths.columns[:: max(1, len(paths.columns) // 30)]:
            fig.add_trace(go.Scatter(y=paths[col], mode="lines", line=dict(width=0.5, color="lightgray"), showlegend=False))
        fig.add_trace(go.Scatter(y=p50, name="Median", line=dict(color="blue", width=2)))
        fig.add_trace(go.Scatter(y=p95, fill=None, line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(y=p5, fill="tonexty", name="90% band", line=dict(width=0)))
        fig.update_layout(title=f"{mc_sym} — Monte Carlo equity paths", height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Median terminal equity", f"${p50.iloc[-1]:,.0f}")

with tabs[8]:
    sz_sym = st.selectbox("Symbol", [s for s in data.keys() if s != BENCHMARK], key="sz_sym")
    entry = float(data[sz_sym]["Close"].iloc[-1])
    stop = st.number_input("Stop price", 0.0, entry * 2, entry * 0.95)
    risk_pct = st.slider("Risk % of equity", 0.5, 5.0, 1.0, 0.5)
    sz = fixed_fractional(port.equity, risk_pct, entry, stop)
    st.metric("Suggested shares", sz["shares"])
    st.metric("Position value", f"${sz['position_value']:,.0f}")
    st.metric("% of equity", f"{sz['pct_of_equity']:.1f}%")
    wr = st.slider("Kelly — win rate", 0.3, 0.7, 0.55, 0.05)
    kf = kelly_fraction(wr, 1.2, 1.0)
    st.caption(f"Kelly fraction (capped): {kf:.1%} of equity")

with tabs[9]:
    cmp = compare_symbols(data, BENCHMARK)
    st.dataframe(cmp, use_container_width=True, hide_index=True)
    if not cmp.empty:
        st.plotly_chart(px.scatter(cmp, x="volatility", y="return", size="sharpe", hover_name="symbol", title="Risk/return"), use_container_width=True)
    st.download_button("Export compare CSV", cmp.to_csv(index=False).encode(), "compare.csv")

with tabs[10]:
    st.subheader("Price alerts (demo)")
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    a_sym = st.selectbox("Symbol", [s for s in data.keys() if s != BENCHMARK], key="alert_sym")
    rule = st.selectbox("Rule", ["RSI < 30", "RSI > 70", "Price below SMA20", "MACD bullish cross"])
    if st.button("Evaluate now"):
        df = data[a_sym]
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        fired = False
        msg = ""
        if rule == "RSI < 30" and latest.get("RSI", 50) < 30:
            fired, msg = True, f"{a_sym} RSI oversold ({latest['RSI']:.0f})"
        elif rule == "RSI > 70" and latest.get("RSI", 50) > 70:
            fired, msg = True, f"{a_sym} RSI overbought ({latest['RSI']:.0f})"
        elif rule == "Price below SMA20" and latest["Close"] < latest.get("SMA_20", latest["Close"]):
            fired, msg = True, f"{a_sym} below SMA20"
        elif rule == "MACD bullish cross" and latest["MACD"] > latest["MACD_Signal"] and prev["MACD"] <= prev["MACD_Signal"]:
            fired, msg = True, f"{a_sym} MACD bullish cross"
        if fired:
            st.session_state.alerts.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "message": msg})
            st.warning(msg)
        else:
            st.success("No alert triggered.")
    if st.session_state.alerts:
        st.dataframe(pd.DataFrame(st.session_state.alerts), use_container_width=True, hide_index=True)

with tabs[11]:
    focus = st.selectbox("Brief symbol", [s for s in data.keys() if s != BENCHMARK], key="brief_sym")
    rets = analytics.daily_returns(data[focus]["Close"])
    var, cvar = analytics.var_cvar(rets)
    bt = st.session_state.get("backtest", {})
    m = bt.get("metrics", {}) if bt else {}
    m.update({"sharpe": analytics.sharpe(rets), "var": var, "max_drawdown": m.get("max_drawdown", analytics.max_drawdown(data[focus]["Close"]))})
    brief = executive_brief(scanner, m, focus)
    with st.expander("Executive brief preview"):
        st.markdown(brief)
    render_export_center(scanner, port, m, focus, executive_brief)

st.caption(f"{APP_NAME} · Not financial advice · DEMO.md")
