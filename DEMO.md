# TradePulse Enterprise — Demo

```powershell
.\scripts\start-demo.ps1
```

**http://127.0.0.1:8505**

## One-click (30 sec)

1. Sidebar → **Run perfect demo** (loads data, backtest, paper positions, alerts)  
2. Open **Strategy Lab** → walk-forward split  
3. **Export** tab → download **Full dashboard HTML**  

## Full tour (3 min)

1. **Perfect demo** or **Load data** (+ optional **Force synthetic data**)  
2. **Command** — candlesticks + SPY benchmark overlay  
3. **Scanner** → export CSV  
4. **Backtest** → equity, drawdown, vs buy & hold  
5. **Strategy Lab** — signal history, rolling Sharpe, monthly calendar, walk-forward  
6. **Alloc** — position pie + portfolio VaR (approx)  
7. **Monte Carlo** → fan chart  
8. **Sizing** / **Compare** / **Alerts**  
9. **Export** — dashboard HTML pack  

## Presenter checklist

Use the sidebar expander — same flow as above.

## Offline / Streamlit Cloud

Toggle **Force synthetic data** — no internet required. On **share.streamlit.io**, this defaults **on** (Yahoo Finance is often blocked).

Console warnings like `Unrecognized feature: 'battery'` or `403` on `/api/v1/app/event/focus` are from Streamlit’s hosting page, not TradePulse.
