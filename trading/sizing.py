"""Position sizing calculators."""


def fixed_fractional(equity: float, risk_pct: float, entry: float, stop: float) -> dict:
    risk_amount = equity * (risk_pct / 100)
    per_share_risk = abs(entry - stop)
    if per_share_risk <= 0:
        return {"shares": 0, "position_value": 0, "risk_amount": risk_amount}
    shares = int(risk_amount / per_share_risk)
    return {
        "shares": shares,
        "position_value": shares * entry,
        "risk_amount": risk_amount,
        "pct_of_equity": (shares * entry / equity * 100) if equity else 0,
    }


def kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 0.0
    b = avg_win / abs(avg_loss)
    p = win_rate
    q = 1 - p
    k = (b * p - q) / b
    return max(0.0, min(k, 0.25))  # cap at 25% for demo safety
