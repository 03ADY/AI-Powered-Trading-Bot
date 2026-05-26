"""Paper portfolio simulation."""

from dataclasses import dataclass, field


@dataclass
class PaperPortfolio:
    cash: float = 100_000.0
    positions: dict[str, dict] = field(default_factory=dict)
    trade_log: list[dict] = field(default_factory=list)

    @property
    def equity(self) -> float:
        return self.cash + sum(p.get("market_value", 0) for p in self.positions.values())

    def update_prices(self, prices: dict[str, float]) -> None:
        for sym, pos in self.positions.items():
            if sym in prices:
                pos["last_price"] = prices[sym]
                pos["market_value"] = pos["qty"] * prices[sym]

    def execute_signal(self, symbol: str, signal: int, price: float, confidence: float, reason: str, *, dry_run: bool = True) -> dict:
        record = {
            "symbol": symbol,
            "signal": signal,
            "price": price,
            "confidence": confidence,
            "reason": reason,
            "dry_run": dry_run,
            "status": "logged",
        }
        if dry_run:
            self.trade_log.append(record)
            return record

        if signal == 1 and symbol not in self.positions and self.cash > price * 10:
            qty = int((self.cash * 0.1) / price)
            cost = qty * price
            self.cash -= cost
            self.positions[symbol] = {"qty": qty, "avg_price": price, "last_price": price, "market_value": cost}
            record.update({"side": "BUY", "qty": qty, "status": "filled"})
        elif signal == -1 and symbol in self.positions:
            pos = self.positions.pop(symbol)
            proceeds = pos["qty"] * price
            self.cash += proceeds
            record.update({"side": "SELL", "qty": pos["qty"], "status": "filled"})
        self.trade_log.append(record)
        return record
