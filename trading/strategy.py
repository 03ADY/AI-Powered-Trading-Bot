import numpy as np
import pandas as pd


class TradingStrategy:
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> dict:
        if df.empty or len(df) < 50:
            return {"signal": 0, "confidence": 0, "reason": "Insufficient data"}
        latest, prev = df.iloc[-1], df.iloc[-2]
        signals, reasons = [], []
        if latest["MACD"] > latest["MACD_Signal"] and prev["MACD"] <= prev["MACD_Signal"]:
            signals.append(1)
            reasons.append("MACD bullish cross")
        elif latest["MACD"] < latest["MACD_Signal"] and prev["MACD"] >= prev["MACD_Signal"]:
            signals.append(-1)
            reasons.append("MACD bearish cross")
        if latest["RSI"] < 30:
            signals.append(1)
            reasons.append("RSI oversold")
        elif latest["RSI"] > 70:
            signals.append(-1)
            reasons.append("RSI overbought")
        if not signals:
            return {"signal": 0, "confidence": 0, "reason": "No clear signal"}
        sig = np.mean(signals)
        conf = min(len(signals) / 3, 1.0)
        if latest.get("Volume_Ratio", 1) > 1.2:
            conf *= 1.15
        return {
            "signal": 1 if sig > 0.3 else (-1 if sig < -0.3 else 0),
            "confidence": min(conf, 1.0),
            "reason": ", ".join(reasons),
        }
