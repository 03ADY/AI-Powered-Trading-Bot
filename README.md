# TradePulse Enterprise

Algorithmic trading command center: multi-symbol **scanner**, **backtest lab**, **paper portfolio**, risk analytics (Sharpe, VaR, beta vs SPY), and **full dashboard export**.

## Features

- **Run perfect demo** — one-click load, backtest, positions, alerts  
- Live OHLC + Bollinger + RSI + MACD + **SPY benchmark overlay**  
- Demo scenarios (Tech momentum, Blue chip, High volatility)  
- Signal scanner with confidence ranking  
- Strategy backtest with equity curve + buy & hold alpha  
- **Strategy Lab** — signal history, rolling Sharpe, monthly calendar, walk-forward IS/OOS  
- **Allocation** pie + approximate portfolio VaR  
- Paper portfolio & trade journal  
- Correlation heatmap & return distribution  
- **Monte Carlo**, **position sizing**, **symbol compare**, **alerts**  
- **Export center** — full dashboard HTML + brief + scanner CSV  
- **Synthetic data** fallback for offline demos  

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
.\scripts\start-demo.ps1
```

## Config

- **Demo mode:** Yahoo Finance via `yfinance` (default)  
- **Alpaca:** copy `.streamlit/secrets.toml.example` → `secrets.toml`  

See [DEMO.md](DEMO.md).

**Disclaimer:** Demo/education only — not financial advice.
