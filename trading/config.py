APP_NAME = "TradePulse Enterprise"

DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "TSLA", "SPY"]
BENCHMARK = "SPY"
INITIAL_CAPITAL = 100_000.0

SCENARIOS = {
    "Tech momentum": {
        "symbols": ["NVDA", "MSFT", "AAPL", "META", "GOOGL"],
        "blurb": "Growth-heavy watchlist for momentum demo.",
    },
    "Blue chip": {
        "symbols": ["AAPL", "MSFT", "AMZN", "GOOGL", "SPY"],
        "blurb": "Large-cap stability narrative.",
    },
    "High volatility": {
        "symbols": ["TSLA", "NVDA", "META", "AMZN"],
        "blurb": "Higher beta names — risk analytics stand out.",
    },
    "Custom": {
        "symbols": DEFAULT_SYMBOLS,
        "blurb": "Pick symbols in sidebar.",
    },
}
