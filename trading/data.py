from datetime import datetime, timedelta

import pandas as pd
import streamlit as st


@st.cache_data(ttl=300, show_spinner="Fetching market data…")
def fetch_yfinance(symbols: list[str], days: int = 60) -> dict[str, pd.DataFrame]:
    import yfinance as yf

    out = {}
    end = datetime.now()
    start = end - timedelta(days=days)
    for sym in dict.fromkeys(symbols):
        try:
            raw = yf.download(sym, start=start, end=end, progress=False, auto_adjust=True)
            if raw.empty:
                continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            df = raw.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
            df.index.name = "timestamp"
            out[sym] = df
        except Exception:
            from trading.synthetic import generate_synthetic
            out[sym] = generate_synthetic(sym, days=days)
    return out
