import numpy as np
import pandas as pd


class PortfolioAnalytics:
    @staticmethod
    def daily_returns(close: pd.Series) -> pd.Series:
        return close.pct_change().dropna()

    @staticmethod
    def sharpe(rets: pd.Series) -> float:
        if rets.empty or rets.std() == 0:
            return 0.0
        return float(np.sqrt(252) * rets.mean() / rets.std())

    @staticmethod
    def sortino(rets: pd.Series) -> float:
        if rets.empty:
            return 0.0
        down = rets[rets < 0]
        if down.empty or down.std() == 0:
            return 0.0
        return float(np.sqrt(252) * rets.mean() / down.std())

    @staticmethod
    def var_cvar(rets: pd.Series, alpha: float = 0.05) -> tuple[float, float]:
        if rets.empty:
            return 0.0, 0.0
        var = float(np.percentile(rets, alpha * 100))
        tail = rets[rets <= var]
        cvar = float(tail.mean()) if len(tail) else var
        return var, cvar

    @staticmethod
    def max_drawdown(close: pd.Series) -> float:
        if close.empty:
            return 0.0
        equity = (1 + close.pct_change().fillna(0)).cumprod()
        peak = equity.cummax()
        return float(((equity - peak) / peak).min())

    @staticmethod
    def beta_vs_benchmark(asset_rets: pd.Series, bench_rets: pd.Series) -> float:
        aligned = pd.concat([asset_rets, bench_rets], axis=1).dropna()
        if len(aligned) < 10:
            return 0.0
        cov = aligned.cov().iloc[0, 1]
        var = aligned.iloc[:, 1].var()
        return float(cov / var) if var else 0.0

    @staticmethod
    def correlation_matrix(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
        cols = {}
        for sym, df in frames.items():
            if not df.empty and "Close" in df.columns:
                cols[sym] = PortfolioAnalytics.daily_returns(df["Close"])
        return pd.DataFrame(cols).corr() if len(cols) > 1 else pd.DataFrame()
