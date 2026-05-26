"""Executive narrative and scanner helpers."""

from datetime import datetime

import pandas as pd

from trading.config import APP_NAME


def scan_signals(data: dict, strategy) -> pd.DataFrame:
    rows = []
    for sym, df in data.items():
        if df.empty:
            continue
        sig = strategy.generate_signal(df, sym)
        price = float(df["Close"].iloc[-1]) if "Close" in df.columns else 0
        rows.append({
            "symbol": sym,
            "signal": {1: "BUY", -1: "SELL", 0: "HOLD"}.get(sig["signal"], "HOLD"),
            "confidence": sig["confidence"],
            "reason": sig["reason"],
            "price": price,
            "rsi": float(df["RSI"].iloc[-1]) if "RSI" in df.columns else None,
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("confidence", ascending=False)
    return out


def insight_cards(scanner: pd.DataFrame, day_pnl_pct: float) -> list[dict]:
    cards = []
    if scanner.empty:
        return [{"icon": "📊", "title": "Scanner", "body": "Load market data to scan.", "tone": "neutral"}]
    buys = (scanner["signal"] == "BUY").sum()
    sells = (scanner["signal"] == "SELL").sum()
    top = scanner.iloc[0]
    cards.append({
        "icon": "🎯",
        "title": "Top opportunity",
        "body": f"{top['symbol']} — {top['signal']} ({top['confidence']:.0%}) · {top['reason']}",
        "tone": "positive" if top["signal"] == "BUY" else "warning",
    })
    cards.append({
        "icon": "📡",
        "title": "Scanner",
        "body": f"{buys} BUY · {sells} SELL · {len(scanner)} symbols tracked.",
        "tone": "neutral",
    })
    cards.append({
        "icon": "💰",
        "title": "Day P&L",
        "body": f"Portfolio day change {day_pnl_pct:+.2f}% (demo account).",
        "tone": "positive" if day_pnl_pct >= 0 else "warning",
    })
    return cards


def executive_brief(scanner: pd.DataFrame, metrics: dict, symbol: str) -> str:
    lines = [
        f"# {APP_NAME} — Trading Brief",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Focus symbol: **{symbol}**",
        "",
        "## Risk metrics (focus)",
        f"- Sharpe: **{metrics.get('sharpe', 0):.2f}**",
        f"- Max drawdown (backtest): **{metrics.get('max_drawdown', 0):.1%}**",
        f"- VaR 5%: **{metrics.get('var', 0):.2%}**",
        "",
        "## Scanner highlights",
    ]
    for _, row in scanner.head(5).iterrows():
        lines.append(f"- **{row['symbol']}** {row['signal']} ({row['confidence']:.0%}) — {row['reason']}")
    lines.extend(["", "---", "*Not financial advice · demo only*"])
    return "\n".join(lines)
